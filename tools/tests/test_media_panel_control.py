"""Media wire and sole-owner contracts with fake HA services only."""

import asyncio
from copy import deepcopy
import importlib
import json
from types import SimpleNamespace as NS
import unittest

import test_entity_control as shared
import test_media_panel_domain as domain_tests

codec = shared.codec
m = domain_tests.m
features = importlib.import_module("_atmosfera_test.extra_panel_features")
KINDS = ["light", "number", "choice", "cover", "fan", "humidifier", "robot", "panel"]


def fixture(suffix="music"):
    return domain_tests.MediaPanelDomainTests().fixture(suffix)


def snapshot(suffix="music", facet="main", state_change=None, attrs=None):
    hass, state, domain = fixture(suffix)
    if state_change is not None:
        state.state = state_change
    if attrs:
        state.attributes.update(attrs)
    domain = m.MediaDomain.from_ha(hass, state)
    body = domain.view(state, facet, 0 if facet == "main" else 1)
    eligible = body["eligible"] if facet == "main" else (1 if facet == "volume" else 2) if body["editable"] else 0
    return codec.envelope("state", **(shared.CodecTests().identity() | {"control_kind": "panel"}),
        state_seq=1, ttl_ms=30000, title="External Media", panel_type="media", available=domain.source(state)=="known",
        panel_caps=domain.descriptor(), panel_state=body, eligible_actions=eligible, state_generation=1)


class MediaCodecTests(unittest.TestCase):
    def test_metadata_and_projection_preserve_explicit_legacy_intents(self):
        base=domain_tests.base
        for suffix in ("music","tv"):
            hass,state,domain=fixture(suffix)
            card=base.card(entity=state.entity_id,action=deepcopy(m.MEDIA_ACTION))
            self.assertEqual(base.layout.validate_action(card["action"],state.entity_id,layout_version=3),m.MEDIA_ACTION)
            disabled=base.cards.presentation_payload(hass,[card],panel_types=("timer","remote","power"),press_enabled_supported=True)["cards"][2]
            enabled=base.cards.presentation_payload(hass,[card],panel_extra_profiles=("media",),press_enabled_supported=True)["cards"][2]
            self.assertFalse(disabled["press_enabled"])
            self.assertEqual(enabled["control_kind"],"panel")
            self.assertIsNone(base.cards.resolve_action(hass,card))
            metadata=m.media_metadata(hass,state)["media_panel"]
            self.assertEqual(metadata["caps"],domain.descriptor())
            state.attributes.update(media_position=99,media_title="new title",access_token="never serialize",volume_level=.425)
            self.assertEqual(m.media_metadata(hass,state)["media_panel"]["fingerprint"],metadata["fingerprint"])
            self.assertNotIn("never serialize",json.dumps(m.media_metadata(hass,state)))
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_action(m.MEDIA_ACTION,"light.test",layout_version=3)

    def test_actual_music_tv_and_every_view_roundtrip_requires_negotiation(self):
        for suffix, facets in (("music", ("main", "volume", "sound_mode", "repeat")), ("tv", ("main", "source", "sound_mode"))):
            for facet in facets:
                for phase in (None, "unknown", "unavailable", "off"):
                    value = snapshot(suffix, facet, phase)
                    self.assertEqual(codec.decode(codec.encode(value, extra_profiles=("media",)), extra_profiles=("media",)), value)
                    with self.assertRaises(codec.ProtocolError):
                        codec.encode(value, extra_profiles=("info", "lock"), climate_panel=True)

    def test_volume_never_uses_ui_step_to_round_observation_and_rejects_forged_display(self):
        value = snapshot(facet="volume", attrs={"volume_level": .425})
        self.assertEqual(value["panel_state"]["percent_text"], "42.5")
        for change in ({"observed_raw": "0.43"}, {"percent_text": "43"}, {"rail": 4300}, {"ui_step_percent": True},
                       {"observed_raw": "0.4250"}, {"rail": True}, {"observed_raw": None}, {"editable": False}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value | {"panel_state": value["panel_state"] | change}, extra_profiles=("media",))

    def test_closed_command_shapes_and_discriminator_cannot_enter_climate(self):
        identity = {k:v for k,v in snapshot().items() if k in codec.SELECTION}
        basic = codec.envelope("command", **identity, media_version=1, command_seq=1, view_seq=0,
                               facet="main", op="pause", expected_state_generation=1)
        messages = [basic, basic | {"op":"mute", "target":True}, basic | {"op":"shuffle", "target":False},
                    basic | {"op":"volume", "facet":"volume", "view_seq":1, "expected_raw":"0.425", "target_percent":43},
                    basic | {"op":"choice", "facet":"source", "view_seq":2, "expected_index":0, "target_index":1},
                    codec.envelope("facet", **identity, media_version=1, facet="source", view_seq=1)]
        for message in messages:
            self.assertEqual(codec.decode_report(shared.wire(message)),message)
            with self.assertRaises(codec.ProtocolError):
                codec.encode(message, climate_panel=True)
        for change in ({"media_version":True}, {"op":"media_play_pause"}, {"target":True}, {"facet":"humidity"},
                       {"control_kind":"light"}, {"expected_state_generation":0}, {"view_seq":True}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(basic | change, extra_profiles=("media",), light_detail=True, climate_panel=True)

    def test_unknown_metadata_boolean_and_feature_cross_fields_fail_closed(self):
        value=snapshot("tv")
        for changes in ({"muted":False}, {"volume_raw":"1", "volume_percent":"100", "volume_rail":10000},
                        {"shuffle":1}, {"phase":"invented"}, {"artist_status":"value", "media_artist":""},
                        {"media_title":"x"*129}, {"title_status":"excerpt", "media_title":"not excerpt"}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value|{"panel_state":value["panel_state"]|changes},extra_profiles=("media",))
        with self.assertRaises(codec.ProtocolError):
            codec.encode(value|{"panel_caps":value["panel_caps"]|{"facets":value["panel_caps"]["facets"]|1}},extra_profiles=("media",))


class MediaOwnerTests(unittest.IsolatedAsyncioTestCase):
    send=shared.NumberOwnerTests.send
    change=shared.NumberOwnerTests.change
    results=shared.NumberOwnerTests.results
    asyncTearDown=shared.NumberOwnerTests.asyncTearDown

    def bind(self):
        value=self.owner.prepare_bind(shared.wire(codec.envelope("capability",enabled=True,max_payload_bytes=2048,control_kinds=KINDS)),epoch=1,runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value),epoch=1,runtime=self.runtime)
        self.owner.accept_extra_features(self.owner.channel,list(features.PROFILES))
        self.owner.accept_detail_features(self.owner.channel,1,1)

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.configure()

    def configure(self, suffix="music"):
        self.hass,self.state,_=fixture(suffix)
        self.owner.hass=self.hass
        self.card.update(entity_id=self.state.entity_id, type="entity", action=deepcopy(m.MEDIA_ACTION))
        async def service(domain,operation,data,**kwargs):
            self.hass.services.calls.append(((domain,operation,data),kwargs))
            self.service_entered.set()
            if self.service_gate:await self.service_gate.wait()
            if not self.apply:return
            updates={"volume_set":("volume_level",data.get("volume_level")), "volume_mute":("is_volume_muted",data.get("is_volume_muted")),
                     "shuffle_set":("shuffle",data.get("shuffle")), "select_source":("source",data.get("source")),
                     "select_sound_mode":("sound_mode",data.get("sound_mode")), "repeat_set":("repeat",data.get("repeat"))}
            phase={"media_play":"playing","media_pause":"paused","media_stop":"off","turn_on":"idle","turn_off":"off"}
            if operation in updates:
                key,value=updates[operation];self.change(self.state.state,**{key:value})
            elif operation in phase:self.change(phase[operation])
        self.hass.services.async_call=service

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self,seq,"panel")

    async def facet(self,name,sequence=1):
        return await self.owner.async_handle(shared.wire(codec.envelope("facet",**self.owner._selection.identity,
            media_version=1,view_seq=sequence,facet=name)),self.user)

    def command(self,seq=1,op="pause",**changes):
        selected=self.owner._selection;current=selected.domain_state
        return codec.envelope("command",**selected.identity,media_version=1,command_seq=seq,facet=current.facet,
            view_seq=current.view_seq,expected_state_generation=current.generation,op=op)|changes

    async def test_absolute_release_one_service_context_and_fresh_confirmation(self):
        self.state.attributes["volume_level"]=.425
        grant=await self.open();self.assertEqual(grant["panel_state"]["volume_percent"],"42.5")
        await self.facet("volume");self.assertEqual(self.hass.services.calls,[])
        command=self.command(op="volume",expected_raw="0.425",target_percent=43)
        await self.send(command);await self.send(command)
        self.assertEqual(len(self.hass.services.calls),1)
        args,kwargs=self.hass.services.calls[0]
        self.assertEqual(args,("media_player","volume_set",{"entity_id":self.state.entity_id,"volume_level":.43}))
        self.assertIs(kwargs["context"],self.user)
        self.assertEqual(self.results()[-1]["status"],"state_matches")

    async def test_metadata_telemetry_preserves_generation_but_phase_volume_ABA_cancels(self):
        await self.open();await self.facet("volume")
        command=self.command(op="volume",expected_raw="1",target_percent=40)
        generation=self.owner._selection.domain_state.generation
        self.change(self.state.state,media_position=42,media_title="A new title",media_artist="Artist")
        self.assertEqual(self.owner._selection.domain_state.generation,generation)
        self.auth_gate,self.auth_entered=asyncio.Event(),asyncio.Event()
        await self.owner.async_handle(shared.wire(command),self.user)
        await asyncio.wait_for(self.auth_entered.wait(),.1)
        self.change(self.state.state,volume_level=.5);self.change(self.state.state,volume_level=1)
        self.auth_gate.set();await asyncio.sleep(.04)
        self.assertEqual(self.hass.services.calls,[])
        self.assertEqual(self.results()[-1]["reason"],"stale_state")

    async def test_explicit_play_pause_stop_and_no_feedback_is_not_success(self):
        await self.open();await self.send(self.command())
        self.assertEqual(self.results()[-1]["status"],"state_matches")
        await self.send(self.command(2,op="play"));await self.send(self.command(3,op="stop"))
        self.assertEqual(self.state.state,"off")
        self.assertEqual([x[0][1] for x in self.hass.services.calls],["media_pause","media_play","media_stop"])
        self.apply=False;await self.send(self.command(4,op="turn_on"))
        self.assertEqual(self.results()[-1]["status"],"not_confirmed")

    async def test_relative_and_track_commands_only_report_service_completion(self):
        await self.open();self.apply=False
        for index,operation in enumerate(("previous","next","volume_down"),1):
            await self.send(self.command(index,op=operation))
            self.assertEqual(self.results()[-1]["status"],"service_completed")

    async def test_tv_has_no_volume_control_even_with_attributes_and_choice_is_canonical(self):
        self.configure("tv");await self.open()
        self.assertEqual((await self.facet("volume"))["reason"],"unsupported")
        await self.send(self.command(op="mute",target=True))
        self.assertEqual(self.hass.services.calls,[])
        await self.facet("source",2)
        await self.send(self.command(2,op="choice",expected_index=0,target_index=1))
        self.assertEqual(self.hass.services.calls[0][0],("media_player","select_source",{"entity_id":self.state.entity_id,"source":"youtube"}))
        self.assertEqual(self.results()[-1]["status"],"state_matches")

    async def test_pending_service_blocks_facet_and_old_view_or_permission_never_dispatches(self):
        await self.open();self.service_gate=asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()),self.user)
        await asyncio.wait_for(self.service_entered.wait(),.1)
        self.assertEqual((await self.facet("volume"))["reason"],"busy")
        self.service_gate.set();await asyncio.sleep(.04)
        self.allowed=False
        self.assertEqual((await self.facet("volume",2))["reason"],"unauthorized")
        self.assertEqual(len(self.hass.services.calls),1)

    async def test_service_catalogue_change_retires_and_unknown_disables_without_fake_values(self):
        await self.open();self.change("unavailable")
        await self.owner.async_state_changed()
        state=[v for v in self.outputs if v["kind"]=="state"][-1]
        self.assertIsNone(state["panel_state"]["volume_raw"])
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls,[])
        self.hass.services.names.discard("media_player.media_pause")
        self.change("playing")
        self.assertIsNone(self.owner._selection)


if __name__ == "__main__":
    unittest.main()
