"""Detailed Light/Climate host contracts; no actual HA or hardware calls."""

import asyncio
from copy import deepcopy
import importlib
import json
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_entity_control as shared
import test_ha_layout as base
import test_climate_temperature_control as thermal
import test_light_color_temperature as kelvin

model = importlib.import_module("_atmosfera_test.detail_domain")
feature = importlib.import_module("_atmosfera_test.detail_features")
codec = shared.codec
KINDS = ["light", "number", "choice", "cover", "fan", "humidifier", "robot", "panel"]


def environment(family="climate"):
    if family == "light":
        hass, state = kelvin.light()
        state.attributes.update(supported_features=4, effect_list=["Solid", " Soft "], effect="Solid")
    else:
        hass, state, _ = thermal.climate()
        state.state = "heat"
        state.attributes.update(supported_features=1|4|8|16|32|512, hvac_modes=["off","heat","cool"],
            preset_modes=["eco","comfort"], preset_mode=None, fan_modes=["low","high"], fan_mode="low",
            swing_modes=["off","on"], swing_mode="off", swing_horizontal_modes=["off","on"], swing_horizontal_mode="off",
            min_humidity=20,max_humidity=80,humidity=45,current_humidity=40,hvac_action="heating")
        hass.services.names.update("climate." + name for name in ("set_humidity","set_hvac_mode","set_preset_mode","set_fan_mode","set_swing_mode","set_swing_horizontal_mode"))
    return hass, state


class DetailModelTests(unittest.TestCase):
    def test_all_actual_facets_and_fingerprint_excludes_measurement_and_targets(self):
        for family, mask in (("light",3),("climate",127)):
            hass, state = environment(family)
            domain = model.DetailDomain.from_ha(hass,state)
            self.assertEqual(domain.mask,mask)
            first = domain.fingerprint
            state.attributes.update(current_temperature=24,current_humidity=60,temperature=22,brightness=130,hvac_action="idle")
            self.assertEqual(model.DetailDomain.from_ha(hass,state).fingerprint,first)
            self.assertEqual(len(first),64)
            self.assertEqual(hass.services.calls,[])

    def test_partial_unsupported_does_not_hide_other_capabilities_and_no_truncation(self):
        hass,state = environment()
        state.attributes["preset_modes"]=[str(i) for i in range(9)]
        state.attributes.pop("target_temp_step")
        domain=model.DetailDomain.from_ha(hass,state)
        self.assertEqual(domain.mask,127-8-1)
        self.assertIsNone(domain.main(state)["domain"])
        self.assertFalse(domain.main(state)["editable"])
        self.assertEqual(dict(domain.reasons)["preset_mode"],"unsupported_catalogue")
        self.assertTrue(domain.allowed_facet("humidity"))

    def test_label_collision_or_overflow_falls_back_to_exact_full_canonical_catalogue(self):
        hass,state=environment()
        for labels in (("same","same"),("x"*33,"ok"),("bad\n","ok")):
            with patch.object(base.cards,"choice_control_labels",return_value=labels):
                domain=model.DetailDomain.from_ha(hass,state)
                for _, choices, presented in domain.choices:
                    self.assertEqual(presented,choices.options)

    def test_display_only_modes_range_unknown_and_mismatched_units(self):
        hass,state=environment()
        state.attributes.update(supported_features=2,target_temp_low=19,target_temp_high=23)
        domain=model.DetailDomain.from_ha(hass,state)
        self.assertEqual(domain.mask,4)
        self.assertEqual((domain.main(state)["low"],domain.main(state)["high"]),("19","23"))
        self.assertIsNone(domain.main(state)["domain"])
        state.state="unavailable"
        offline=model.DetailDomain.from_ha(hass,state)
        self.assertEqual(offline,domain)
        self.assertEqual(offline.main(state)["mode"],"unknown")
        self.assertEqual(offline.main(state)["low"],"")
        hass.services.names.clear()
        self.assertEqual(model.DetailDomain.from_ha(hass,state).mask,0)
        self.assertIn("climate_panel",base.cards._detail_control_metadata(hass,state))
        hass,state=environment()
        hass.config.units.temperature_unit="°F"
        self.assertFalse(model.DetailDomain.from_ha(hass,state).mask & 1)

    def test_kelvin_stale_off_and_empty_effect_are_distinct(self):
        hass,state=environment("light")
        domain=model.DetailDomain.from_ha(hass,state)
        state.state="off"
        state.attributes["effect"]=None
        self.assertEqual(domain.observed(state,"color_temp_kelvin"),(None,False))
        self.assertEqual(domain.observed(state,"effect"),(None,True))
        state.attributes.pop("effect")
        self.assertEqual(domain.observed(state,"effect"),(None,False))
        state.state="on";state.attributes["color_mode"]="hs"
        self.assertEqual(domain.observed(state,"color_temp_kelvin"),(None,False))

    def test_climate_limits_remain_metadata_when_unknown_and_participate_in_fingerprint(self):
        hass,state=environment()
        state.attributes.pop("target_temp_step")
        before=model.DetailDomain.from_ha(hass,state)
        original=before.main(state)
        state.state="unavailable"
        offline=model.DetailDomain.from_ha(hass,state)
        self.assertEqual(offline,before)
        self.assertEqual((offline.main(state)["min"],offline.main(state)["max"]),(original["min"],original["max"]))
        for key in ("target","current","low","high"):
            self.assertEqual(offline.main(state)[key],"")
        state.attributes["min_temp"]+=1
        self.assertNotEqual(model.DetailDomain.from_ha(hass,state).fingerprint,before.fingerprint)

    def test_projection_and_layout_require_explicit_negotiated_profiles(self):
        for family,action in (("light",model.LIGHT_ACTION),("climate",model.CLIMATE_ACTION)):
            hass,state=environment(family)
            card=base.card(entity=state.entity_id,action=action)
            doc=base.document([card])|{"version":3}
            self.assertEqual(base.layout.validate_layout(doc),doc)
            disabled=base.cards.presentation_payload(hass,[card],light_control_supported=True,
                panel_types=("timer","remote","power"),press_enabled_supported=True)["cards"][2]
            self.assertNotIn("control_kind",disabled)
            self.assertFalse(disabled["press_enabled"])
            enabled=base.cards.presentation_payload(hass,[card],light_detail_supported=True,
                climate_panel_supported=True,press_enabled_supported=True)["cards"][2]
            self.assertEqual(enabled["control_kind"],"light" if family=="light" else "panel")
            if family=="light":self.assertEqual(enabled["control_detail_version"],1)
            self.assertIsNone(base.cards.resolve_action(hass,card))
        for bad in (True,0,2,"1"):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(model.LIGHT_ACTION|{"detail":bad},"light.test",layout_version=3)
        self.assertEqual(base.layout.device_profile()["schema_panel_types"],["timer","remote","power"])


class DetailCodecTests(unittest.TestCase):
    def snapshot(self,family="climate",facet="main"):
        hass,state=environment(family)
        domain=model.DetailDomain.from_ha(hass,state)
        value=codec.envelope("state",**(shared.CodecTests().identity()|{"control_kind":"light" if family=="light" else "panel"}),
                             state_seq=1,ttl_ms=30000,title="Device")
        body=domain.view(state,facet,0 if facet=="main" else 1)
        if family=="light":
            return value|domain.main(state)|{"light_detail":{"version":1,"facets":domain.mask,"state_generation":1,**body}}
        return value|{"panel_type":"climate","available":True,"panel_caps":{"facets":domain.mask},"panel_state":body,
                      "eligible_actions":(1 if facet in {"main","humidity"} else 2) if body["editable"] else 0,"state_generation":1}

    def test_every_facet_roundtrip_and_legacy_negotiation_rejects(self):
        for family in ("light","climate"):
            for facet in model.FACETS[family]:
                if facet in {"color", "range"}:  # Optional profiles have independent corpora.
                    continue
                value=self.snapshot(family,facet)
                self.assertEqual(codec.decode(codec.encode(value,light_detail=True,climate_panel=True),light_detail=True,climate_panel=True),value)
                with self.assertRaises(codec.ProtocolError):codec.encode(value)

    def test_malformed_cross_fields_and_foreign_view_are_rejected(self):
        value=self.snapshot()
        for changes in ({"editable":True,"index":None},{"facet":"temperature"},{"view_seq":True},
                        {"unit":None},{"extra":1},{"mode":"invented"}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value|{"panel_state":value["panel_state"]|changes},climate_panel=True)
        value=self.snapshot("climate","hvac_mode")
        for changes in ({"choice_known":True,"index":None},{"options":["x"]*8},{"options":["x"*33]},
                        {"editable":False,"index":1},{"domain":None}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value|{"panel_state":value["panel_state"]|changes},climate_panel=True)
        identity={key:value[key] for key in codec.SELECTION}
        view=codec.envelope("facet",**identity,view_seq=1,facet="humidity")
        self.assertEqual(codec.decode_report(shared.wire(view)),view)
        for extra in ({"command_seq":1},{"op":"turn_on"},{"target_index":1},{"view_seq":0}):
            with self.assertRaises(codec.ProtocolError):codec.decode_report(shared.wire(view|extra))

    def test_max_escaped_catalogue_fits_and_new_receipts_are_not_commands(self):
        value=self.snapshot("light","effect")
        value["title"]='"'*160
        value["light_detail"]["options"]=['\\'*i+'"'*(32-i) for i in range(8)]
        self.assertLess(len(codec.encode(value,light_detail=True).encode()),2048)
        identity={key:value[key] for key in codec.SELECTION}
        receipt=codec.envelope("facet_result",**identity,view_seq=1,facet="effect",state_seq=1,status="ready",reason="none")
        self.assertEqual(codec.decode(codec.encode(receipt,light_detail=True),light_detail=True),receipt)
        with self.assertRaises(codec.ProtocolError):codec.decode_report(shared.wire(receipt))
        with self.assertRaises(codec.ProtocolError):codec.encode(receipt|{"status":"state_matches"},light_detail=True)

    def test_features_are_independent_strict_subset_and_old_family_unchanged(self):
        for light,climate in ((1,0),(0,1),(1,1)):
            value=json.loads(feature.bind_payload("a"*32,light,climate))|{"accepted":True}
            self.assertEqual(feature.decode_features(NS(success=True,response_data=shared.wire(value).encode()),bind=True),value)
        for light,climate in ((0,0),(True,1),(1,2)):
            with self.assertRaises(codec.ProtocolError):feature.bind_payload("a"*32,light,climate)


class DetailOwnerTests(unittest.IsolatedAsyncioTestCase):
    send=shared.NumberOwnerTests.send
    change=shared.NumberOwnerTests.change
    results=shared.NumberOwnerTests.results
    asyncTearDown=shared.NumberOwnerTests.asyncTearDown

    def bind(self):
        payload=self.owner.prepare_bind(shared.wire(codec.envelope("capability",enabled=True,max_payload_bytes=2048,control_kinds=KINDS)),epoch=1,runtime=self.runtime)
        self.owner.accept_bind(shared.wire(payload),epoch=1,runtime=self.runtime)
        self.owner.accept_detail_features(self.owner.channel,1,1)
        self.owner.accept_panel_features(self.owner.channel,["timer","remote","power"])

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.fail_service=False
        self.configure("climate")

    def configure(self,family):
        self.family=family
        self.hass,self.state=environment(family)
        self.owner.hass=self.hass
        self.card.update(entity_id=self.state.entity_id,action=deepcopy(model.LIGHT_ACTION if family=="light" else model.CLIMATE_ACTION))
        async def service(*args,**kwargs):
            self.hass.services.calls.append((args,kwargs));self.service_entered.set()
            if self.service_gate:await self.service_gate.wait()
            if self.fail_service:raise RuntimeError("provider error")
            if not self.apply:return
            operation,data=args[1:3]
            values={key:value for key,value in data.items() if key!="entity_id"}
            if operation=="set_hvac_mode":self.change(values.pop("hvac_mode"),**values)
            elif family=="light":
                if "brightness_pct" in values:values["brightness"]=round(values.pop("brightness_pct")*255/100)
                if "color_temp_kelvin" in values:values["color_mode"]="color_temp"
                self.change("off" if operation=="turn_off" else "on",**values)
            else:self.change(self.state.state,**values)
        self.hass.services.async_call=service

    async def open(self,seq=1,marker=True):
        fields=dict(channel=self.owner.channel,open_seq=seq,slot=2,card_id="card-2",revision=4,
                    control_kind="light" if self.family=="light" else "panel")
        if self.family=="light" and marker:fields["detail_version"]=1
        return await self.owner.async_handle(shared.wire(codec.envelope("open",**fields)),self.user)

    async def facet(self,name,sequence=None):
        selected=self.owner._selection
        if sequence is None:sequence=selected.domain_state.highest_view+1
        return await self.owner.async_handle(shared.wire(codec.envelope("facet",**selected.identity,view_seq=sequence,facet=name)),self.user)

    def command(self,seq=1,op="facet_number",target=None,**changes):
        selected=self.owner._selection;current=selected.domain_state
        fields={"view_seq":current.view_seq,"expected_state_generation":current.generation}
        if op in {"facet_number","facet_choice"}:
            index,_=current.domain.observed(self.state,current.facet)
            fields.update(facet=current.facet,expected_index=index,target_index=(index+1 if target is None and index is not None else target))
        elif op=="brightness":fields["value"]=target
        return codec.envelope("command",**selected.identity,command_seq=seq,op=op,**fields)|changes

    async def test_passive_open_views_and_absolute_numeric_then_mode_commands(self):
        await self.open()
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls[-1][0],("climate","set_temperature",{"entity_id":"climate.test","temperature":22}))
        await self.facet("humidity")
        await self.send(self.command(2))
        self.assertEqual(self.hass.services.calls[-1][0][2]["humidity"],46)
        await self.facet("hvac_mode")
        await self.send(self.command(3,"facet_choice",0))
        self.assertEqual(self.state.state,"off")
        await self.send(self.command(4,"facet_choice",0))
        self.assertEqual(self.results()[-1]["status"],"already_matched")
        self.assertEqual(len(self.hass.services.calls),3)
        self.assertTrue(all(kwargs["context"] is self.user for _,kwargs in self.hass.services.calls))

    async def test_all_choices_use_exact_authoritative_mapping_and_empty_preset(self):
        await self.open()
        for seq,facet in enumerate(("preset_mode","fan_mode","swing_mode","swing_horizontal_mode"),1):
            await self.facet(facet)
            await self.send(self.command(seq,"facet_choice",1))
            self.assertEqual(self.results()[-1]["status"],"state_matches")
        self.assertEqual([args[1] for args,_ in self.hass.services.calls],["set_preset_mode","set_fan_mode","set_swing_mode","set_swing_horizontal_mode"])

    async def test_light_requires_explicit_open_and_preserves_zero_off(self):
        self.configure("light")
        with self.assertRaises(codec.ProtocolError):await self.open(marker=False)
        await self.open(2)
        await self.send(self.command(1,"brightness",0))
        self.assertEqual(self.state.state,"off")
        self.assertEqual(self.hass.services.calls[0][0],("light","turn_off",{"entity_id":"light.test"}))
        await self.send(self.command(2,"turn_on"))
        await self.facet("color_temp_kelvin")
        await self.send(self.command(3))
        self.assertEqual(self.hass.services.calls[-1][0][2]["color_temp_kelvin"],2701)
        await self.facet("effect")
        await self.send(self.command(4,"facet_choice",1))
        self.assertEqual(self.hass.services.calls[-1][0][2]["effect"]," Soft ")

    async def test_measurements_preserve_intent_but_target_ABA_and_old_facet_do_not(self):
        await self.open();old=self.command()
        self.change("heat",current_temperature=42,current_humidity=90,hvac_action="idle")
        self.assertEqual(self.owner._selection.domain_state.generation,old["expected_state_generation"])
        await self.send(old)
        old=self.command(2)
        self.change("heat",temperature=22.5);self.change("heat",temperature=22)
        await self.send(old)
        self.assertEqual(self.results()[-1]["reason"],"stale_state")
        old=self.command(3)
        await self.facet("humidity")
        await self.send(old)
        self.assertEqual(len(self.hass.services.calls),1)

    async def test_metadata_ABA_while_view_authorizes_cannot_show_or_dispatch(self):
        await self.open();self.auth_gate=asyncio.Event();self.auth_entered.clear()
        job=asyncio.create_task(self.facet("humidity"))
        await asyncio.wait_for(self.auth_entered.wait(),.2)
        self.change("heat",preset_modes=["different"]);self.change("heat",preset_modes=["eco","comfort"])
        self.auth_gate.set();await job
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls,[])

    async def test_view_during_pending_service_does_not_cancel_it_and_close_does_not_undo(self):
        await self.open();self.service_gate=asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()),self.user)
        await asyncio.wait_for(self.service_entered.wait(),.2)
        result=await self.facet("humidity")
        self.assertEqual((result["status"],result["reason"]),("rejected","busy"))
        self.assertFalse(self.owner._service_task.cancelled())
        await self.owner.async_close();self.service_gate.set();await asyncio.sleep(.02)
        self.assertEqual(len(self.hass.services.calls),1)

    async def test_command_during_view_authorization_is_busy_without_cancelling_view(self):
        await self.open();self.auth_gate=asyncio.Event();self.auth_entered.clear()
        job=asyncio.create_task(self.facet("humidity"))
        await asyncio.wait_for(self.auth_entered.wait(),.2)
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"],"busy")
        self.auth_gate.set();result=await job
        self.assertEqual(result["status"],"ready")
        self.assertEqual(self.hass.services.calls,[])

    async def test_view_sequence_duplicates_conflicts_and_permission_denial(self):
        await self.open();result=await self.facet("humidity",1)
        self.assertEqual(result,await self.facet("humidity",1))
        self.assertEqual((await self.facet("main",1))["reason"],"sequence_conflict")
        self.allowed=False
        self.assertEqual((await self.facet("main",2))["reason"],"unauthorized")
        self.assertEqual(self.owner._selection.domain_state.facet,"humidity")
        self.assertEqual((await self.facet("main",1))["reason"],"stale_sequence")

    async def test_offline_climate_retains_real_metadata_and_no_fabricated_command(self):
        await self.open();old=self.command()
        before=self.owner._selection.domain_state.domain.main(self.state)
        self.change("unavailable")
        await self.owner.async_state_changed()
        current=self.outputs[-1]
        self.assertFalse(current["available"])
        self.assertIsNotNone(current["panel_state"]["domain"])
        self.assertIsNone(current["panel_state"]["index"])
        self.assertEqual((current["panel_state"]["min"],current["panel_state"]["max"]),(before["min"],before["max"]))
        self.assertEqual(codec.decode(codec.encode(current,climate_panel=True),climate_panel=True),current)
        await self.send(old)
        self.assertEqual(self.hass.services.calls,[])
        self.change("heat");await self.facet("humidity")
        self.assertEqual(self.owner._selection.domain_state.facet,"humidity")

    async def test_display_only_setpoint_and_range_feedback_advance_generation_but_measurements_do_not(self):
        for ranged in (False,True):
            await self.owner.async_close()
            self.configure("climate")
            self.state.attributes.pop("target_temp_step")
            if ranged:
                self.state.attributes.update(supported_features=2,target_temp_low=19,target_temp_high=23)
            await self.open(2 if ranged else 1)
            selected=self.owner._selection
            self.assertIsNone(selected.domain_state.domain.main(self.state)["domain"])
            generation=selected.domain_state.generation
            changes={"target_temp_low":20,"target_temp_high":24} if ranged else {"temperature":22.5}
            self.change("heat",**changes)
            self.assertEqual(self.owner._selection.domain_state.generation,generation+1)
            self.change("heat",current_temperature=24,hvac_action="idle")
            self.assertEqual(self.owner._selection.domain_state.generation,generation+1)
            await self.owner.async_state_changed()
            self.assertEqual(codec.decode(codec.encode(self.outputs[-1],climate_panel=True),climate_panel=True),self.outputs[-1])
        self.assertEqual(self.hass.services.calls,[])

    async def test_rebind_resets_only_new_flags_and_service_failure_never_confirms(self):
        await self.open();self.fail_service=True
        await self.send(self.command())
        self.assertEqual((self.results()[-1]["status"],self.results()[-1]["reason"]),("rejected","service_error"))
        await self.owner.async_disconnect()
        self.assertEqual((self.owner.light_detail_version,self.owner.climate_panel_version),(0,0))
        self.assertEqual(self.owner.panel_types,())

    async def test_newer_busy_view_retires_old_receipt_without_cancelling_old_read(self):
        await self.open();self.auth_gate=asyncio.Event();self.auth_entered.clear()
        job=asyncio.create_task(self.facet("humidity",1))
        await asyncio.wait_for(self.auth_entered.wait(),.2)
        self.assertEqual((await self.facet("main",2))["reason"],"busy")
        self.auth_gate.set();self.assertEqual((await job)["status"],"ready")
        self.assertEqual((await self.facet("humidity",1))["reason"],"stale_sequence")
        self.assertEqual((await self.facet("main",2))["reason"],"busy")
        self.assertEqual(self.hass.services.calls,[])

    async def test_late_view_authorization_after_close_never_reopens(self):
        await self.open();self.auth_gate=asyncio.Event();self.auth_entered.clear()
        job=asyncio.create_task(self.facet("humidity"))
        await asyncio.wait_for(self.auth_entered.wait(),.2)
        await self.owner.async_close();self.auth_gate.set();await job
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["kind"],"close")
        self.assertEqual(self.hass.services.calls,[])


class DetailTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_supplementary_flags_are_channel_bound_and_fail_independently(self):
        api=shared.integration.transport
        for mode in ("valid","missing","wrong_channel","bad_version","epoch_change"):
            bridge=shared.NumberModelTransportTests().generic_bridge()
            original=bridge.runtime.client.execute_service
            if mode!="missing":
                for name in ("entity_detail_get_features","entity_detail_bind_features"):
                    bridge.services[name]=NS(name=name,key=100+len(bridge.services),
                        args=[] if "get" in name else [NS(name="payload",type=api.UserServiceArgType.STRING)],
                        supports_response=api.SupportsResponseType.ONLY)
            async def execute(service,data,**kwargs):
                if service.name=="entity_detail_get_features":
                    value={"v":1,"type":feature.TYPE,"detail_version":1,"light_detail_version":1,
                           "climate_panel_version":2 if mode=="bad_version" else 1}
                elif service.name=="entity_detail_bind_features":
                    value=json.loads(data["payload"])|{"accepted":True}
                    if mode=="wrong_channel":value["channel"]="f"*32
                    if mode=="epoch_change":bridge._connection_epoch+=1
                else:
                    response=await original(service,data,**kwargs)
                    if service.name=="entity_control_get_status":
                        value=json.loads(response.response_data);value["control_kinds"].append("panel")
                        response.response_data=shared.wire(value).encode()
                    return response
                return NS(success=True,response_data=shared.wire(value).encode())
            bridge.runtime.client.execute_service=execute
            transport=bridge._light_control
            try:
                accepted=await transport.async_negotiate()
                self.assertEqual(accepted,mode!="epoch_change")
                self.assertEqual(transport.light_detail_supported,mode=="valid")
                self.assertEqual(transport.climate_panel_supported,mode=="valid")
                self.assertEqual(transport.panel_types,())
                if mode!="epoch_change":self.assertTrue(transport.number_supported)
                transport.invalidate_connection()
                self.assertFalse(transport.light_detail_supported)
            finally:await transport.async_shutdown()

