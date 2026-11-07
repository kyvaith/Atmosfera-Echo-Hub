"""Color1 through the real HA adapter/owner; no HA instance or device calls."""
import ast
import asyncio
from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, Mock, patch

import voluptuous as vol
import test_detail_control as detail
import test_entity_control as shared
import test_ha_layout as base

domain = importlib.import_module("_atmosfera_test.light_color_domain")
features = importlib.import_module("_atmosfera_test.light_color_features")
codec = shared.codec


def environment(mode="hs", modes=None):
    hass, state = detail.environment("light")
    state.attributes.update(supported_color_modes=modes or ["hs", "color_temp"], color_mode=mode,
                            brightness=181, hs_color=(30, 100), rgb_color=(255, 128, 0), xy_color=(.612, .374), effect=None)
    return hass, state


def snapshot(reason="none"):
    hass, state = environment()
    changes = {"off": ("off", {}), "source_unavailable": ("unavailable", {}),
               "unsupported_mode": ("on", {"color_mode": "brightness"}),
               "invalid_color": ("on", {"hs_color": None}), "invalid_brightness": ("on", {"brightness": None})}
    if reason in changes:
        state.state, attrs = changes[reason]; state.attributes.update(attrs)
    d = detail.model.DetailDomain.from_ha(hass, state, color=True)
    value = detail.DetailCodecTests().snapshot("light", "main")
    value.update(**d.main(state), light_detail={"version": 1, "facets": d.mask, "state_generation": 1,
                                             "facet": "color", "view_seq": 1}, light_color=d.color.source(state))
    return value


class ColorModelTests(unittest.TestCase):
    def test_modes_route_and_default_detail_unchanged(self):
        for modes, route in ((["rgb"], "rgb"), (["hs", "xy"], "hs"), (["rgb", "xy"], "rgb"), (["xy"], "xy")):
            hass, state = environment(modes=modes)
            self.assertEqual(domain.ColorDomain.from_ha(hass, state).write_mode, route)
            self.assertFalse(detail.model.DetailDomain.from_ha(hass, state).mask & 4)
            self.assertTrue(detail.model.DetailDomain.from_ha(hass, state, color=True).mask & 4)
        for modes in ([], None, ["rgbw"], ["hs", "rgbww"], ["rgb", "onoff"], ["color_temp"], ["hs", "hs"], [True], [{"hs": 1}]):
            hass, state = environment(); state.attributes["supported_color_modes"] = modes
            with self.assertRaises(domain.ColorDomainError): domain.ColorDomain.from_ha(hass, state)

    def test_precision_ct_seed_and_exact_raw_brightness(self):
        hass, state = environment("color_temp")
        state.attributes["hs_color"] = (360, 66.667)
        d = domain.ColorDomain.from_ha(hass, state)
        source = d.source(state)
        self.assertEqual((source["hue_milli"], source["saturation_milli"], source["source_mode"]), (0, 66667, "color_temp"))
        self.assertTrue(source["editable"])
        self.assertEqual(d.service(state, 123456, 98765), {"hs_color": [123.456, 98.765], "brightness": 181})
        self.assertFalse(d.unchanged(state, 0, 66667))  # Explicit mode switch, even at seed.
        for h, s in ((True, 1), (360000, 1), (-1, 1), (1, 100001), (1.0, 1), (1, False)):
            with self.assertRaises(domain.ColorDomainError): d.service(state, h, s)

    def test_unknown_off_and_invalid_brightness_never_invent_values(self):
        for reason in domain.REASONS:
            value = snapshot(reason)["light_color"]
            self.assertEqual(value["reason"], reason)
            self.assertEqual(value["editable"], reason == "none")
            self.assertEqual(value["rgb"] is not None, reason in ("none", "invalid_brightness"))
        hass, state = environment(); d = domain.ColorDomain.from_ha(hass, state)
        for field, value in (("brightness", 0), ("brightness", True), ("rgb_color", [True, 2, 3]),
                             ("hs_color", [float("nan"), 50]), ("color_mode", {}), ("color_mode", "rgb")):
            current = deepcopy(state); current.attributes[field] = value
            self.assertFalse(d.source(current)["editable"])

    def test_projection_uses_core_and_matching_does_not_reuse_unconverted_rgb(self):
        util = base.module("homeassistant.util")
        colors = NS(color_hs_to_RGB=Mock(return_value=(255, 127, 0)), color_hs_to_xy=Mock(return_value=(.612, .374)),
                    color_xy_to_RGB=Mock(return_value=(255, 129, 2)))
        util.color = colors
        for mode, rgb in (("hs", (255, 127, 0)), ("rgb", (255, 127, 0)), ("xy", (255, 129, 2))):
            hass, state = environment(mode, [mode]); d = domain.ColorDomain.from_ha(hass, state)
            state.attributes["rgb_color"] = rgb
            self.assertEqual(d.projection(29882, 100000), rgb)
            self.assertTrue(d.matches(state, 29882, 100000, 181))
            self.assertFalse(d.matches(state, 29882, 100000, 180))
        colors.color_hs_to_xy.assert_called_with(29.882, 100.0)

    def test_equal_projection_is_noop_across_color_routes_but_not_ct_mode_switch(self):
        hass, state = environment("rgb", ["rgb", "hs", "color_temp"])
        d = domain.ColorDomain.from_ha(hass, state)
        with patch.object(domain.ColorDomain, "projection", return_value=tuple(state.attributes["rgb_color"])):
            self.assertTrue(d.unchanged(state, 29882, 100000))
            self.assertFalse(d.matches(state, 29882, 100000, 181))  # Confirmation still owns its route.
            state.attributes["color_mode"] = "color_temp"
            self.assertFalse(d.unchanged(state, 29882, 100000))

    def test_semantic_generation_inputs_exclude_metadata_and_keep_raw_brightness(self):
        hass, state = environment(); d = domain.ColorDomain.from_ha(hass, state); first = d.observation(state)
        state.attributes.update(friendly_name="Renamed", icon="mdi:lamp", extra="metadata")
        self.assertEqual(d.observation(state), first)
        for attrs in ({"brightness": 182}, {"color_mode": "color_temp"}, {"hs_color": (30.001, 100)},
                      {"hs_color": (30.0001, 100)},
                      {"xy_color": (.613, .374)}, {"rgb_color": (255, 127, 0)}, {"effect": "rainbow"}):
            current = deepcopy(state); current.attributes.update(attrs)
            self.assertNotEqual(d.observation(current), first)


class ColorCodecTests(unittest.TestCase):
    def test_actual_adapter_corpus_roundtrip_and_ingress(self):
        corpus = json.loads((Path(__file__).parent / "fixtures/light_color/wire.json").read_text(encoding="utf8"))
        self.assertEqual(corpus["integration"], 125)
        for row in corpus["rows"]:
            with self.subTest(name=row["name"]):
                value = codec.decode(row["wire"], light_detail=True, light_color=True)
                self.assertEqual(codec.encode(value, light_detail=True, light_color=True), row["wire"])
                if row["direction"] == "device_to_ha": self.assertEqual(codec.decode_report(row["wire"]), value)

    def test_state_matrix_default_off_and_main_grant_shape(self):
        for reason in domain.REASONS:
            value = snapshot(reason)
            self.assertEqual(codec.decode(codec.encode(value, light_detail=True, light_color=True), light_detail=True, light_color=True), value)
            with self.assertRaises(codec.ProtocolError): codec.encode(value, light_detail=True)
        value = snapshot(); value.pop("light_color"); value["light_detail"]["facet"] = "main"
        value["light_detail"]["view_seq"] = 0
        self.assertEqual(codec.decode(codec.encode(value, light_detail=True, light_color=True), light_detail=True, light_color=True), value)
        with self.assertRaises(codec.ProtocolError): codec.encode(value | {"light_color": snapshot()["light_color"]}, light_detail=True, light_color=True)

    def test_closed_cross_field_color_state(self):
        value = snapshot()
        for change in ({"version": True}, {"write_mode": "rgbw"}, {"source_mode": "other"}, {"rgb": [1, 2, True]},
                       {"hue_milli": 360000}, {"saturation_milli": -1}, {"rgb": None}, {"editable": False},
                       {"reason": "off"}, {"brightness": 180}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value | {"light_color": value["light_color"] | change}, light_detail=True, light_color=True)
        for invalid in (value | {"control_kind": "panel"}, value | {"kind": "grant"},
                        value | {"light_detail": value["light_detail"] | {"facets": 3}}):
            with self.assertRaises(codec.ProtocolError): codec.encode(invalid, light_detail=True, light_color=True, climate_panel=True)
        for reason in domain.REASONS:
            invalid = snapshot(reason)
            invalid["on"] = not invalid["on"]
            with self.assertRaises(codec.ProtocolError): codec.encode(invalid, light_detail=True, light_color=True)

    def test_actual_ingress_and_exact_command_only_targets(self):
        identity = shared.CodecTests().identity() | {"control_kind": "light"}
        command = codec.envelope("command", **identity, command_seq=1, op="facet_color", facet="color", view_seq=1,
                                 expected_state_generation=1, target_hue_milli=123456, target_saturation_milli=98765)
        source = ast.parse((base.COMPONENT/"__init__.py").read_text(encoding="utf8"))
        setup = next(n for n in source.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "async_setup")
        function = next(n for n in setup.body if isinstance(n, ast.FunctionDef) and n.name == "entity_payload")
        namespace = {"vol": vol, "decode_entity_control": codec.decode_report, "ProtocolError": codec.ProtocolError}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_entity_service_validator", "exec"), namespace)
        raw = shared.wire(command)
        self.assertEqual(namespace["entity_payload"](raw), raw)
        self.assertEqual(codec.decode_report(raw), command)
        with self.assertRaises(codec.ProtocolError): codec.decode(raw, light_detail=True)
        for change in ({"brightness": 181}, {"expected_rgb": [1, 2, 3]}, {"target_hue_milli": True}, {"target_saturation_milli": 1.5},
                       {"facet": "effect"}, {"view_seq": 0}, {"control_kind": "panel"}):
            with self.assertRaises(vol.Invalid): namespace["entity_payload"](shared.wire(command | change))
        with self.assertRaises(vol.Invalid): namespace["entity_payload"](raw.replace('"target_hue_milli":123456', '"target_hue_milli":123456,"target_hue_milli":123456'))

    def test_feature_exact_grammar_and_rejected_bind(self):
        good = {"v": 1, "type": features.TYPE, "color_version": 1}
        reply = lambda v: NS(success=True, response_data=shared.wire(v).encode())
        self.assertEqual(features.decode_features(reply(good)), good)
        bound = json.loads(features.bind_payload("a"*32)) | {"accepted": True}
        self.assertEqual(features.decode_features(reply(bound), bind=True), bound)
        rejected = good | {"color_version": 0, "accepted": False, "channel": ""}
        self.assertEqual(features.decode_features(reply(rejected), bind=True), rejected)
        for bad in (good | {"color_version": True}, good | {"extra": 1}, bound | {"channel": ""}, rejected | {"color_version": 1}):
            with self.assertRaises(codec.ProtocolError): features.decode_features(reply(bad), bind="accepted" in bad)


class ColorOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown
    configure = detail.DetailOwnerTests.configure
    open = detail.DetailOwnerTests.open
    facet = detail.DetailOwnerTests.facet

    def bind(self):
        detail.DetailOwnerTests.bind(self)
        self.owner.accept_color_features(self.owner.channel)

    async def asyncSetUp(self):
        await detail.DetailOwnerTests.asyncSetUp(self)
        self.configure("light")
        self.state.attributes.update(environment()[1].attributes)
        self.projection = patch.object(domain.ColorDomain, "projection", return_value=(0, 255, 0))
        self.projection.start(); self.addCleanup(self.projection.stop)

        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs)); self.service_entered.set()
            if self.service_gate: await self.service_gate.wait()
            if self.fail_service: raise RuntimeError("provider failure")
            if not self.apply: return
            values = args[2]
            route = domain.ColorDomain.from_ha(self.hass, self.state).write_mode
            self.change("on", color_mode=route, hs_color=tuple(values["hs_color"]), rgb_color=(0, 255, 0), brightness=values["brightness"])
        self.hass.services.async_call = service

    def command(self, seq=1, h=120000, s=100000):
        selected = self.owner._selection; current = selected.domain_state
        return codec.envelope("command", **selected.identity, command_seq=seq, op="facet_color", facet="color",
                              view_seq=current.view_seq, expected_state_generation=current.generation,
                              target_hue_milli=h, target_saturation_milli=s)

    async def test_ct_seed_apply_once_context_exact_brightness_and_duplicate(self):
        self.change("on", color_mode="color_temp")
        await self.open(); await self.facet("color")
        self.assertEqual(self.hass.services.calls, [])
        command = self.command(h=30000)
        await self.send(command)
        self.assertEqual(self.hass.services.calls[0][0], ("light", "turn_on", {"entity_id": self.state.entity_id, "hs_color": [30.0, 100.0], "brightness": 181}))
        self.assertIs(self.hass.services.calls[0][1]["context"], self.user)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        await self.send(command)
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_active_unchanged_no_command_and_close_no_service(self):
        await self.open(); await self.facet("color")
        await self.send(self.command(h=30000))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        await self.owner.async_close("navigation")
        self.assertEqual(self.hass.services.calls, [])

    async def test_brightness_and_color_aba_during_authorization_reject(self):
        await self.open(); await self.facet("color")
        self.auth_gate = asyncio.Event()
        command = self.command(); self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(command), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("on", brightness=182); self.change("on", brightness=181)
        task = self.owner._selection.command.task
        self.auth_gate.set(); await asyncio.wait_for(task, .4)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_unprocessed_brightness_change_at_dispatch_task_fence_zero_service(self):
        await self.open(); await self.facet("color")
        original = self.owner._run_dispatch
        async def mutate(selected, record, dispatch, context):
            self.state.attributes["brightness"] = 182  # No observer delivery before final fresh read.
            return await original(selected, record, dispatch, context)
        with patch.object(self.owner, "_run_dispatch", side_effect=mutate): await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["status"], "rejected")

    async def test_off_does_not_expose_retained_color_or_turn_on(self):
        self.change("off")
        await self.open(); await self.facet("color")
        self.assertEqual(self.outputs[-2]["light_color"]["reason"], "off")
        self.assertIsNone(self.outputs[-2]["light_color"]["rgb"])
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])

    async def test_metadata_preserves_edit_but_effect_change_retires_generation(self):
        await self.open(); await self.facet("color")
        command = self.command(); generation = self.owner._selection.domain_state.generation
        self.change("on", friendly_name="New name", icon="mdi:lightbulb")
        self.assertEqual(self.owner._selection.domain_state.generation, generation)
        self.change("on", effect="rainbow")
        await self.send(command)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_unknown_feedback_remains_unconfirmed_not_retried(self):
        await self.open(); await self.facet("color"); self.apply = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_each_supported_route_confirms_only_authoritative_projected_color(self):
        for seq, route in enumerate(("hs", "rgb", "xy"), 1):
            with self.subTest(route=route):
                if self.owner._selection is not None: await self.owner.async_close("navigation")
                self.change("on", supported_color_modes=[route], color_mode=route, hs_color=(30, 100),
                            rgb_color=(255, 128, 0))
                await self.open(seq=seq); await self.facet("color")
                before = len(self.hass.services.calls)
                await self.send(self.command())
                self.assertEqual(len(self.hass.services.calls), before + 1)
                self.assertEqual(self.results()[-1]["status"], "state_matches")
                self.assertEqual(self.state.attributes["color_mode"], route)

    async def test_authorization_recheck_and_close_during_pending_authorization_zero_service(self):
        await self.open(); await self.facet("color")
        self.auth_gate = asyncio.Event(); self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        task = self.owner._selection.command.task
        await self.owner.async_close("navigation")
        self.auth_gate.set()
        await asyncio.gather(task, return_exceptions=True)
        self.assertEqual(self.hass.services.calls, [])
        self.assertIsNone(self.owner._selection)

    async def test_rebind_clears_color_without_disabling_detail(self):
        self.owner.accept_detail_features(self.owner.channel, 1, 1)
        self.assertEqual(self.owner.light_color_version, 0)
        self.assertEqual(self.owner.light_detail_version, 1)
        await self.open()
        self.assertFalse(self.outputs[-1]["light_detail"]["facets"] & 4)
        with self.assertRaises(codec.ProtocolError): await self.facet("color")


class ColorTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_optional_query_bind_and_late_client_or_epoch_never_enable_color(self):
        api = shared.integration.transport
        for mode in ("valid", "missing", "bad_query", "rejected", "wrong_channel", "query_client", "bind_client", "epoch"):
            with self.subTest(mode=mode):
                bridge = shared.NumberModelTransportTests().generic_bridge()
                original = bridge.runtime.client.execute_service
                for name in ("entity_detail_get_features", "entity_detail_bind_features", features.QUERY, features.BIND):
                    if mode == "missing" and name in (features.QUERY, features.BIND): continue
                    bridge.services[name] = NS(name=name, key=100+len(bridge.services),
                        args=[] if name in ("entity_detail_get_features", features.QUERY) else [NS(name="payload", type=api.UserServiceArgType.STRING)],
                        supports_response=api.SupportsResponseType.ONLY)
                calls = []
                async def execute(service, data, **kwargs):
                    calls.append(service.name)
                    if service.name == "entity_detail_get_features":
                        value = {"v":1, "type":detail.feature.TYPE, "detail_version":1, "light_detail_version":1, "climate_panel_version":0}
                    elif service.name == "entity_detail_bind_features": value = json.loads(data["payload"]) | {"accepted": True}
                    elif service.name == features.QUERY:
                        value = {"v":1, "type":features.TYPE, "color_version":2 if mode == "bad_query" else 1}
                        if mode == "query_client": bridge.runtime.client = NS(execute_service=execute)
                    elif service.name == features.BIND:
                        value = json.loads(data["payload"]) | {"accepted": True}
                        if mode == "rejected": value.update(accepted=False, color_version=0, channel="")
                        if mode == "wrong_channel": value["channel"] = "f"*32
                        if mode == "bind_client": bridge.runtime.client = NS(execute_service=execute)
                        if mode == "epoch": bridge._connection_epoch += 1
                    else: return await original(service, data, **kwargs)
                    return NS(success=True, response_data=shared.wire(value).encode())
                bridge.runtime.client.execute_service = execute
                transport = bridge._light_control
                try:
                    accepted = await transport.async_negotiate()
                    self.assertEqual(accepted, mode != "epoch")
                    self.assertEqual(transport.owner.light_color_version, int(mode == "valid"))
                    if mode != "epoch": self.assertTrue(transport.light_detail_supported)
                    if mode in ("missing", "bad_query", "query_client"): self.assertNotIn(features.BIND, calls)
                    transport.invalidate_connection()
                    self.assertEqual(transport.owner.light_color_version, 0)
                finally: await transport.async_shutdown()
