"""Range1 actual adapter/ingress/owner tests; no live HA or device calls."""
import ast
import asyncio
from copy import deepcopy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import voluptuous as vol
import test_detail_control as detail
import test_entity_control as shared
import test_ha_layout as base
from homeassistant.components.climate import DATA_COMPONENT

domain = importlib.import_module("_atmosfera_test.climate_range_domain")
features = importlib.import_module("_atmosfera_test.climate_range_features")
codec = shared.codec


def environment():
    hass, state = detail.environment()
    native = hass.data[DATA_COMPONENT].get_entity(state.entity_id)
    native.native_temperature_unit = "°C"
    state.state = "heat_cool"
    state.attributes.update(supported_features=2 | 16, min_temp=7, max_temp=35, target_temp_step=.5,
                            temperature_unit="°C", target_temp_low=21, target_temp_high=24,
                            current_temperature=23, hvac_modes=["off", "heat_cool", "auto"],
                            preset_modes=["home", "eco"], preset_mode="home", hvac_action="idle")
    return hass, state, native


def snapshot(reason="none", *, facet="range"):
    hass, state, _ = environment()
    if reason == "inactive_mode": state.state = "off"
    if reason == "invalid_range": state.attributes["target_temp_low"] = None
    if reason == "source_unavailable": state.state = "unavailable"
    d = detail.model.DetailDomain.from_ha(hass, state, range_enabled=True)
    value = codec.envelope("state", **(shared.CodecTests().identity() | {"control_kind": "panel"}),
                           state_seq=1, ttl_ms=30000, title="Zakres")
    body = d.view(state, facet, 0 if facet == "main" else 1)
    return value | {"panel_type": "climate", "available": d.known(state), "panel_caps": {"facets": d.mask},
                    "panel_state": body, "eligible_actions": 1 if body["editable"] else 0, "state_generation": 1}


def command_fixture():
    return codec.envelope("command", **(shared.CodecTests().identity() | {"control_kind": "panel"}),
        command_seq=1, op="facet_range", facet="range", view_seq=1, expected_state_generation=1,
        target_low_index=29, target_high_index=34)


class RangeDomainTests(unittest.TestCase):
    def test_actual_core_unit_metadata_and_no_single_target_reinterpretation(self):
        hass, state, native = environment()
        d = domain.RangeDomain.from_ha(hass, state)
        self.assertEqual(d.domain.descriptor(), {"schema": "numeric_steps_v1", "min": "7", "max": "35",
                         "step": "0.5", "unit": "°C", "max_index": 56})
        self.assertEqual(d.indices(state), (28, 34))
        self.assertEqual(d.service(state, 29, 34), {"target_temp_low": 21.5, "target_temp_high": 24})
        old = detail.model.DetailDomain.from_ha(hass, state)
        new = detail.model.DetailDomain.from_ha(hass, state, range_enabled=True)
        self.assertEqual(new.mask, old.mask | 128)
        self.assertIsNone(new.main(state)["domain"])
        self.assertEqual(new.main(state)["target"], "")
        self.assertEqual((new.main(state)["low"], new.main(state)["high"]), ("21", "24"))
        native.temperature_unit = "°F"  # Core11 field, not legacy property, is authoritative.
        self.assertEqual(domain.RangeDomain.from_ha(hass, state), d)

    def test_missing_service_feature_loaded_entity_and_step_fail_closed(self):
        for field, value in (("supported_features", 1), ("supported_features", True),
                ("target_temp_step", None), ("target_temp_step", 0), ("target_temp_step", True),
                ("min_temp", 35), ("max_temp", float("inf")), ("temperature_unit", "°F")):
            hass, state, _ = environment(); state.attributes[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(domain.RangeDomainError):
                domain.RangeDomain.from_ha(hass, state)
        for mutate in (lambda h, s, n: h.services.names.clear(), lambda h, s, n: h.data.clear(),
                       lambda h, s, n: setattr(n, "native_temperature_unit", "°F"),
                       lambda h, s, n: s.attributes.pop("target_temp_step")):
            hass, state, native = environment(); mutate(hass, state, native)
            with self.assertRaises(domain.RangeDomainError): domain.RangeDomain.from_ha(hass, state)

    def test_matching_fahrenheit_zero_equality_and_fractional_tail(self):
        hass, state, native = environment()
        hass.config.units.temperature_unit = native.native_temperature_unit = "°F"
        state.attributes.update(temperature_unit="°F", min_temp=-10, max_temp=35.2, target_temp_step=.5,
                                target_temp_low=0, target_temp_high=0)
        d = domain.RangeDomain.from_ha(hass, state)
        self.assertEqual(d.indices(state), (20, 20)); self.assertEqual(d.domain.max_index, 90)
        self.assertEqual(d.service(state, 20, 20), {"target_temp_low": 0, "target_temp_high": 0})
        self.assertEqual(d.service(state, 0, 0), {"target_temp_low": -10, "target_temp_high": -10})
        with self.assertRaises(domain.RangeDomainError): d.target(0, 91)

    def test_inactive_unknown_and_invalid_pair_never_create_a_target(self):
        hass, state, _ = environment(); d = domain.RangeDomain.from_ha(hass, state)
        for value in (None, True, "21", float("nan"), 21.1, 25, -200):
            state.attributes["target_temp_low"] = value
            self.assertEqual(d.source(state)["reason"], "invalid_range")
            self.assertEqual((d.source(state)["low_index"], d.source(state)["high_index"]), (None, None))
            with self.assertRaises(domain.RangeDomainError): d.service(state, 28, 34)
        state.attributes["target_temp_low"] = 21
        for mode in ("off", "auto", "heat", "cool", "fan_only", "dry", "unavailable", "unknown"):
            state.state = mode; source = d.source(state)
            self.assertFalse(source["editable"])
            self.assertEqual(source["low_index"] is None, mode in ("unknown", "unavailable"))
            with self.assertRaises(domain.RangeDomainError): d.service(state, 28, 34)

    def test_raw_pair_and_preset_presence_are_semantic_but_measurement_is_not(self):
        hass, state, _ = environment(); d = domain.RangeDomain.from_ha(hass, state); first = d.observation(state)
        state.attributes.update(current_temperature=23.5, hvac_action="heating", friendly_name="New", icon="mdi:home")
        self.assertEqual(d.observation(state), first)
        for key, value in (("target_temp_low", 21.000001), ("target_temp_high", 24.000001), ("preset_mode", "eco")):
            other = deepcopy(state); other.attributes[key] = value
            self.assertNotEqual(d.observation(other), first)
        state.attributes["preset_mode"] = None; null = d.observation(state)
        del state.attributes["preset_mode"]; self.assertNotEqual(d.observation(state), null)


class RangeCodecTests(unittest.TestCase):
    def test_actual_adapter_corpus_roundtrip_and_ingress(self):
        corpus = json.loads((Path(__file__).parent / "fixtures/climate_range/wire.json").read_text(encoding="utf8"))
        self.assertEqual(corpus["integration"], 126)
        for row in corpus["rows"]:
            with self.subTest(name=row["name"]):
                value = codec.decode(row["wire"], climate_panel=True, climate_range=True)
                self.assertEqual(codec.encode(value, climate_panel=True, climate_range=True), row["wire"])
                if row["direction"] == "device_to_ha": self.assertEqual(codec.decode_report(row["wire"]), value)

    def test_source_matrix_roundtrip_main_and_default_off(self):
        for reason in domain.REASONS:
            value = snapshot(reason)
            self.assertEqual(codec.decode(codec.encode(value, climate_panel=True, climate_range=True),
                                          climate_panel=True, climate_range=True), value)
            with self.assertRaises(codec.ProtocolError): codec.encode(value, climate_panel=True)
        value = snapshot(facet="main"); value["kind"] = "grant"
        self.assertEqual(codec.decode(codec.encode(value, climate_panel=True, climate_range=True),
                                      climate_panel=True, climate_range=True), value)
        self.assertNotIn("low_index", value["panel_state"])

    def test_strict_state_cross_fields_and_pair_indices(self):
        value = snapshot()
        for change in ({"low_index": None}, {"low_index": True}, {"low_index": 35}, {"high_index": 57},
                {"reason": "inactive_mode"}, {"mode": "off"}, {"editable": False}, {"current_text": "23.0"},
                {"current_text": "nan"}, {"reason": []}, {"extra": 0}, {"view_seq": 0}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.encode(value | {"panel_state": value["panel_state"] | change}, climate_panel=True, climate_range=True)
        for change in ({"available": False}, {"eligible_actions": 2}, {"kind": "grant"}, {"control_kind": "light"}):
            with self.assertRaises(codec.ProtocolError): codec.encode(value | change, climate_panel=True, climate_range=True)

    def test_actual_service_ingress_and_negotiation_remains_owner_gate(self):
        source = ast.parse((base.COMPONENT / "__init__.py").read_text(encoding="utf8"))
        setup = next(n for n in source.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "async_setup")
        function = next(n for n in setup.body if isinstance(n, ast.FunctionDef) and n.name == "entity_payload")
        namespace = {"vol": vol, "decode_entity_control": codec.decode_report, "ProtocolError": codec.ProtocolError}
        exec(compile(ast.Module(body=[function], type_ignores=[]), "actual_entity_service_validator", "exec"), namespace)
        command = command_fixture(); raw = shared.wire(command)
        self.assertEqual(namespace["entity_payload"](raw), raw)
        self.assertEqual(codec.decode_report(raw), command)
        with self.assertRaises(codec.ProtocolError): codec.decode(raw, climate_panel=True)
        for change in ({"target_low_index": True}, {"target_high_index": 1.5}, {"target_low_index": 35},
                {"temperature": 21.5}, {"hvac_mode": "heat_cool"}, {"expected_low_index": 28},
                {"facet": "main"}, {"view_seq": 0}, {"control_kind": "light"}):
            with self.assertRaises(vol.Invalid): namespace["entity_payload"](shared.wire(command | change))
        with self.assertRaises(vol.Invalid):
            namespace["entity_payload"](raw.replace('"target_low_index":29', '"target_low_index":29,"target_low_index":29'))

    def test_query_bind_exact_grammar(self):
        reply = lambda value: NS(success=True, response_data=shared.wire(value).encode())
        value = {"v": 1, "type": features.TYPE, "range_version": 1}
        self.assertEqual(features.decode_features(reply(value)), value)
        bound = json.loads(features.bind_payload("a" * 32)) | {"accepted": True}
        self.assertEqual(features.decode_features(reply(bound), bind=True), bound)
        denied = value | {"range_version": 0, "channel": "", "accepted": False}
        self.assertEqual(features.decode_features(reply(denied), bind=True), denied)
        for bad in (value | {"range_version": True}, value | {"color_version": 1}, bound | {"channel": ""}, denied | {"range_version": 1}):
            with self.assertRaises(codec.ProtocolError): features.decode_features(reply(bad), bind="accepted" in bad)


class RangeOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown
    open = detail.DetailOwnerTests.open
    facet = detail.DetailOwnerTests.facet
    configure = detail.DetailOwnerTests.configure

    def bind(self):
        detail.DetailOwnerTests.bind(self)
        self.owner.accept_range_features(self.owner.channel)

    async def asyncSetUp(self):
        await detail.DetailOwnerTests.asyncSetUp(self)
        _, state, _ = environment()
        self.state.state = state.state; self.state.attributes.update(state.attributes)
        self.native = self.hass.data[DATA_COMPONENT].get_entity(self.state.entity_id)
        self.native.native_temperature_unit = "°C"

    def command(self, seq=1, low=29, high=34):
        current = self.owner._selection.domain_state
        return codec.envelope("command", **self.owner._selection.identity, command_seq=seq, op="facet_range", facet="range",
            view_seq=current.view_seq, expected_state_generation=current.generation, target_low_index=low, target_high_index=high)

    async def test_open_view_release_pair_once_context_and_duplicate(self):
        await self.open(); await self.facet("range")
        self.assertEqual(self.hass.services.calls, [])
        command = self.command(); await self.send(command)
        self.assertEqual(self.hass.services.calls[0][0], ("climate", "set_temperature",
            {"entity_id": self.state.entity_id, "target_temp_low": 21.5, "target_temp_high": 24}))
        self.assertIs(self.hass.services.calls[0][1]["context"], self.user)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        await self.send(command); self.assertEqual(len(self.hass.services.calls), 1)

    async def test_unchanged_back_close_and_default_off_zero_services(self):
        await self.open(); await self.facet("range"); await self.send(self.command(low=28))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        await self.facet("main"); await self.owner.async_close("navigation")
        self.owner.accept_detail_features(self.owner.channel, 1, 1)
        await self.open(seq=2)
        self.assertFalse(self.outputs[-1]["panel_caps"]["facets"] & 128)
        with self.assertRaises(codec.ProtocolError): await self.facet("range")
        self.assertEqual(self.hass.services.calls, [])

    async def test_pair_mode_and_raw_preset_aba_cancel_even_without_catalogue(self):
        self.state.attributes.update(supported_features=2)
        self.state.attributes.pop("preset_modes")
        await self.open(); await self.facet("range")
        for sequence, key, other, original in ((1, "target_temp_low", 22, 21), (2, "target_temp_high", 25, 24), (3, "preset_mode", "eco", "home")):
            command = self.command(sequence)
            self.change("heat_cool", **{key: other}); self.change("heat_cool", **{key: original})
            await self.send(command); self.assertEqual(self.results()[-1]["reason"], "stale_state")
        command = self.command(4); self.change("off"); self.change("heat_cool"); await self.send(command)
        self.assertEqual(self.results()[-1]["reason"], "stale_state"); self.assertEqual(self.hass.services.calls, [])

    async def test_measurement_changes_preserve_command_and_missing_preset_is_distinct(self):
        await self.open(); await self.facet("range"); command = self.command()
        self.change("heat_cool", current_temperature=23.5, hvac_action="heating", friendly_name="Renamed")
        await self.send(command); self.assertEqual(len(self.hass.services.calls), 1)
        command = self.command(2, low=30)
        self.state.attributes.pop("preset_mode")
        self.change("heat_cool")
        await self.send(command); self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_stale_or_inactive_source_does_not_use_native_retained_values(self):
        await self.open(); await self.facet("range")
        self.native.native_target_temperature_low = 21; self.native.native_target_temperature_high = 24
        self.change("off")
        await self.send(self.command()); self.assertEqual(self.hass.services.calls, [])
        self.change("heat_cool", target_temp_low=None)
        await self.send(self.command(2)); self.assertEqual(self.hass.services.calls, [])

    async def test_each_mutation_at_final_dispatch_fence_stops_service(self):
        await self.open(); await self.facet("range")
        for seq, mutate in enumerate((lambda: self.state.attributes.update(target_temp_high=25),
                lambda: self.state.attributes.update(preset_mode="eco"),
                lambda: setattr(self.native, "native_temperature_unit", "°F")), 1):
            command = self.command(seq)
            original = self.owner._run_dispatch
            async def change_before_dispatch(selected, record, dispatch, context):
                mutate(); return await original(selected, record, dispatch, context)
            with patch.object(self.owner, "_run_dispatch", side_effect=change_before_dispatch): await self.send(command)
            self.assertEqual(self.hass.services.calls, [])

    async def test_source_aba_during_authorization_zero_service(self):
        await self.open(); await self.facet("range")
        self.auth_gate = asyncio.Event(); self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("heat_cool", preset_mode="eco"); self.change("heat_cool", preset_mode="home")
        task = self.owner._selection.command.task; self.auth_gate.set(); await asyncio.wait_for(task, .4)
        self.assertEqual(self.hass.services.calls, [])

    async def test_authorization_denied_and_close_while_authorizing_zero_service(self):
        await self.open(); await self.facet("range"); self.allowed = False
        await self.send(self.command()); self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.allowed = True; self.auth_gate = asyncio.Event(); self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command(2)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2); task = self.owner._selection.command.task
        await self.owner.async_close("navigation"); self.auth_gate.set(); await asyncio.gather(task, return_exceptions=True)
        self.assertEqual(self.hass.services.calls, [])

    async def test_both_values_and_preserved_preset_required_for_confirmation(self):
        await self.open(); await self.facet("range"); self.apply = False
        original = self.hass.services.async_call
        async def partial(*args, **kwargs):
            await original(*args, **kwargs)
            self.change("heat_cool", target_temp_low=21.5)  # Target high25 is not confirmed.
        self.hass.services.async_call = partial
        await self.send(self.command(high=36))
        self.assertEqual(self.results()[-1]["status"], "not_confirmed"); self.assertEqual(len(self.hass.services.calls), 1)

    async def test_matching_pair_with_changed_preset_is_not_success(self):
        await self.open(); await self.facet("range"); self.apply = False
        original = self.hass.services.async_call
        async def different_preset(*args, **kwargs):
            await original(*args, **kwargs)
            self.change("heat_cool", target_temp_low=21.5, target_temp_high=24, preset_mode="eco")
        self.hass.services.async_call = different_preset
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_domain_revocation_during_authorization_does_not_dispatch(self):
        await self.open(); await self.facet("range")
        self.auth_gate = asyncio.Event(); self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2); task = self.owner._selection.command.task
        self.change("heat_cool", target_temp_step=1)
        self.auth_gate.set(); await asyncio.gather(task, return_exceptions=True)
        self.assertIsNone(self.owner._selection); self.assertEqual(self.hass.services.calls, [])

    async def test_close_during_pending_ack_cannot_dispatch_later(self):
        await self.open(); await self.facet("range")
        gate, entered = asyncio.Event(), asyncio.Event(); original = self.owner.emit
        async def emit(value, *args):
            if value.get("kind") == "result" and value.get("status") == "pending":
                entered.set(); await gate.wait()
            return await original(value, *args)
        self.owner.emit = emit
        job = asyncio.create_task(self.owner.async_handle(shared.wire(self.command()), self.user))
        try:
            await asyncio.wait_for(entered.wait(), .2)
            await self.owner.async_close("navigation")
        finally:
            gate.set(); await asyncio.gather(job, return_exceptions=True)
        self.assertEqual(self.hass.services.calls, [])

    async def test_service_exception_is_terminal_and_duplicate_does_not_retry(self):
        await self.open(); await self.facet("range"); self.fail_service = True
        command = self.command(); await self.send(command)
        self.assertEqual(self.results()[-1]["reason"], "service_error")
        await self.send(command); self.assertEqual(len(self.hass.services.calls), 1)

    async def test_equal_and_zero_targets_are_real_commands(self):
        self.change("heat_cool", min_temp=-10, max_temp=35)
        await self.open(); await self.facet("range")
        await self.send(self.command(low=20, high=20))
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(self.hass.services.calls[0][0][2], {"entity_id": self.state.entity_id,
                         "target_temp_low": 0, "target_temp_high": 0})

    async def test_color_range_bindings_are_independent_and_rebind_clears_both(self):
        self.owner.accept_color_features(self.owner.channel)
        self.assertEqual((self.owner.light_color_version, self.owner.climate_range_version), (1, 1))
        self.owner.accept_detail_features(self.owner.channel, 1, 1)
        self.assertEqual((self.owner.light_color_version, self.owner.climate_range_version), (0, 0))
        self.owner.accept_range_features(self.owner.channel)
        self.assertEqual((self.owner.light_color_version, self.owner.climate_range_version), (0, 1))


class RangeTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_current_client_and_epoch_optional_ack(self):
        api = shared.integration.transport
        for mode in ("valid", "missing", "no_climate", "bad_query", "rejected", "wrong_channel", "query_client", "bind_client", "epoch"):
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
                    if service.name == "entity_control_get_status":
                        value = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=detail.KINDS)
                    elif service.name == "entity_detail_get_features":
                        value = {"v": 1, "type": detail.feature.TYPE, "detail_version": 1, "light_detail_version": 1,
                                 "climate_panel_version": 0 if mode == "no_climate" else 1}
                    elif service.name == "entity_detail_bind_features": value = json.loads(data["payload"]) | {"accepted": True}
                    elif service.name == features.QUERY:
                        value = {"v": 1, "type": features.TYPE, "range_version": 2 if mode == "bad_query" else 1}
                        if mode == "query_client": bridge.runtime.client = NS(execute_service=execute)
                    elif service.name == features.BIND:
                        value = json.loads(data["payload"]) | {"accepted": True}
                        if mode == "rejected": value.update(accepted=False, range_version=0, channel="")
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
                    self.assertEqual(transport.owner.climate_range_version, int(mode == "valid"))
                    self.assertEqual(transport.owner.light_color_version, 0)
                    if mode in ("missing", "bad_query", "query_client", "no_climate"): self.assertNotIn(features.BIND, calls)
                    transport.invalidate_connection(); self.assertEqual(transport.owner.climate_range_version, 0)
                finally: await transport.async_shutdown()


class RangeMockTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_climate3_only_adds_explicit_half_degree_step(self):
        path = Path(__file__).resolve().parents[1] / "ha_demo/atmosfera_demo/entities.py"
        tree = ast.parse(path.read_text(encoding="utf8"))
        nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "demo_platform"
                 or isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DEMO_PLATFORMS" for t in node.targets)]
        entities = [NS(), NS(_attr_supported_features=3), NS(_attr_supported_features=18, _target_temperature_low=21,
                       _target_temperature_high=24, _preset="home", _unique_id="climate_3")]
        before = vars(entities[2]).copy()
        async def setup(hass, entry, add): add(entities)
        namespace = {"ClimateEntityFeature": NS(TARGET_TEMPERATURE_RANGE=2),
                     "import_module": lambda name: NS(async_setup_entry=setup)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
        accepted = []
        await namespace["demo_platform"]("climate")(None, None, lambda values, update=False: accepted.extend(values))
        self.assertIs(accepted[1], entities[2])
        self.assertEqual(vars(entities[2]), before | {"entity_id": "climate.atmosfera_demo_climate_presets",
                                                    "_attr_target_temperature_step": .5})
        self.assertEqual(entities[1]._attr_supported_features, 1)


if __name__ == "__main__":
    unittest.main()
