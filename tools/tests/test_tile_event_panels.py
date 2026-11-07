"""Tile-event Action2 owner, real service ingress and existing bridge callbacks.

HA/Core objects are host doubles; these tests do not claim installed/device proof.
"""
import asyncio
from copy import deepcopy
import importlib
import json
from types import SimpleNamespace as NS
import unittest
import voluptuous as vol

import test_ha_layout as base
import test_entity_control as shared
import test_extra_panels as extra
import test_tile_events as direct
import test_text_report_ingress as ingress

events = importlib.import_module('_atmosfera_test.tile_events')
features = importlib.import_module('_atmosfera_test.extra_panel_features')
action = importlib.import_module('_atmosfera_test.action_panel_domain')
codec = shared.codec


class TileEventPanelTests(unittest.IsolatedAsyncioTestCase):
    bind = extra.ExtraOwnerTests.bind
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.bridge = direct.EventDispatchTests.bridge(self)
        self.card.update(type='action', entity_id='', action=deepcopy(events.PANEL_ACTION))
        self.bridge.entry.options['home_layout'] = base.document([self.card]) | {'version': 3, 'revision': 4}
        self.bridge.layout = self.bridge.entry.options['home_layout']
        self.bridge.tile_cards = base.cards.normalize_cards([self.card])
        self.bridge.saved_revision = self.bridge.sent_revision = 4
        self.hass = self.bridge.hass
        self.hass.bus.async_listen = lambda *_: lambda: None
        self.state = base.State(self.entity, 'unknown', {'friendly_name': 'Event'})
        self.hass.states = base.States([self.state])
        self.owner.hass = self.hass
        self.owner._tile_event_resolver = self.bridge.resolve_tile_event_panel
        self.owner._tile_event_dispatch = self.bridge.dispatch_tile_event_panel
        self.callback_calls = []
        self.accept = True
        self.replace_registration()

    def replace_registration(self):
        def accept(payload, context):
            self.callback_calls.append((deepcopy(payload), context))
            if self.accept:
                self.state.state = '2026-11-06T13:00:00+00:00'
                return True
            return False
        self.remove = self.bridge.register_tile_event('card-2', self.entity, accept)
        self.assertIsNotNone(self.remove)

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, 'panel')

    def command(self, seq=1, **changes):
        selected = self.owner._selection
        return codec.envelope('command', **selected.identity, action_version=1, command_seq=seq,
            op='press', expected_state_generation=selected.domain_state[2]) | changes

    def registration(self):
        async def report(payload, context):
            return await self.owner.async_handle(payload, context)
        bridge = NS(node_name='test-node', _light_control=NS(owner=self.owner, async_report_generic=report))
        self.hass.config_entries = NS(async_loaded_entries=lambda _: [NS(runtime_data=bridge)])
        return ingress.report_registration(self.hass)

    async def through_ingress(self, registration, payload):
        validated = registration['schema']({'node_name': 'test-node', 'payload': payload})
        await registration['handler'](NS(data=validated, context=self.user))
        selected = self.owner._selection
        if selected and selected.command and selected.command.task:
            await asyncio.wait_for(selected.command.task, .4)

    async def test_actual_ingress_first_press_one_callback_bus_context_duplicate_no_service(self):
        grant = await self.open()
        self.assertEqual(grant['panel_caps']['action_type'], 'tile_event')
        self.assertEqual(grant['panel_state']['last_used_status'], 'unknown')
        self.assertEqual(grant['eligible_actions'], 1)
        token = self.bridge._tile_event_entities['card-2'][1]
        self.assertIs(self.owner._selection.caps['tile_event_binding'][1], token)
        self.assertNotIn('tile_event_binding', json.dumps(grant))
        self.assertEqual(self.callback_calls, [])
        registration, payload = self.registration(), shared.wire(self.command())
        await self.through_ingress(registration, payload)
        await self.through_ingress(registration, payload)
        self.assertEqual((len(self.callback_calls), len(self.bus)), (1, 1))
        self.assertIs(self.callback_calls[0][1], self.user)
        self.assertIs(self.bus[0][2], self.user)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]['status'], 'service_dispatched')
        self.assertNotIn('service_completed', [r['status'] for r in self.results()])

    async def test_open_close_direct_report_and_public_bus_cannot_press_panel(self):
        await self.open()
        await self.owner.async_close()
        await self.bridge.async_press_tile(2, card_id='card-2', revision=4, context=self.user)
        self.hass.bus.async_fire('atmosfera_echo_hub_tile_press', {'card_id': 'card-2'}, context=self.user)
        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.hass.services.calls, [])

    async def test_actual_ingress_does_not_grant_negotiation_or_accept_extra_payload(self):
        await self.open()
        registration, command = self.registration(), self.command()
        payload = shared.wire(command)
        for raw in (shared.wire(command | {'entity_id': self.entity}), shared.wire(command | {'event_type': 'any'}),
                    shared.wire(command | {'data': {}}), shared.wire(command | {'target_index': 0}),
                    payload.replace('"op":', '"op":"press","op":'), shared.wire(self.outputs[0])):
            with self.assertRaises(vol.Invalid):
                await self.through_ingress(registration, raw)
        self.owner._extra_profiles = ({'name': 'action', 'version': 2},)
        self.assertEqual(registration['schema']({'node_name': 'test-node', 'payload': payload})['payload'], payload)
        await self.through_ingress(registration, payload)
        self.assertEqual(self.callback_calls, [])

    async def test_authorization_targets_resolved_owned_event_before_and_after_open(self):
        checked = []
        async def authorize(context, entity):
            checked.append((context, entity))
            return True
        self.owner.authorize = authorize
        await self.open()
        await self.send(self.command())
        self.assertEqual(len(checked), 2)
        self.assertTrue(all(entity == self.entity and context is self.user for context, entity in checked))

    async def test_revision_slot_and_connection_changes_during_authorization_retire_old_command(self):
        for index, kind in enumerate(('revision', 'slot', 'connection')):
            await self.owner.async_close()
            self.context = shared.light.LightContext(1, self.runtime, True, 3, 4, 4, (self.card,))
            self.card['slot'] = 2
            self.bridge.entry.options['home_layout']['revision'] = self.bridge.sent_revision = self.bridge.saved_revision = 4
            await self.open(index+1)
            self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
            await self.owner.async_handle(shared.wire(self.command()), self.user)
            task = self.owner._selection.command.task
            await asyncio.wait_for(self.auth_entered.wait(), .2)
            if kind == 'revision':
                self.bridge.entry.options['home_layout']['revision'] = 5
            elif kind == 'slot':
                self.card['slot'] = 3
            else:
                self.context = shared.light.LightContext(2, object(), True, 3, 4, 4, (self.card,))
            self.auth_gate.set()
            await asyncio.wait_for(task, .4)
            self.assertEqual(self.callback_calls, [])
            self.auth_gate = None

    async def test_missing_one_profile_or_callbacks_deny_open(self):
        for names in (('action',), ('tile_event',), ()):
            self.owner._extra_profiles = tuple(p for p in features.PROFILES if p['name'] in names)
            with self.assertRaises(codec.ProtocolError):
                await self.open(self.owner._open_seq+1)
        self.bind()
        self.owner._tile_event_resolver = None
        with self.assertRaises(codec.ProtocolError):
            await self.open()
        self.assertEqual(self.callback_calls, [])

    async def test_permission_denied_and_disabled_registry_do_not_dispatch(self):
        await self.open()
        self.allowed = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]['reason'], 'unauthorized')
        self.allowed = True
        self.hass.entity_registry.entries[self.entity].disabled_by = 'user'
        with self.assertRaises(codec.ProtocolError):
            await self.send(self.command(2))
        self.assertEqual(self.callback_calls, [])

    async def test_registration_ABA_while_open_authorization_is_pending(self):
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        task = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        old = self.bridge._tile_event_entities['card-2']
        self.remove()
        self.replace_registration()
        self.assertIsNot(self.bridge._tile_event_entities['card-2'][1], old[1])
        self.auth_gate.set()
        with self.assertRaises(codec.ProtocolError):
            await task
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.callback_calls, [])

    async def test_registration_ABA_while_command_authorization_is_pending(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        task = self.owner._selection.command.task
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.remove()
        self.replace_registration()
        self.auth_gate.set()
        await asyncio.wait_for(task, .4)
        self.assertEqual(self.callback_calls, [])
        self.assertIsNone(self.owner._selection)

    async def test_registration_change_immediately_retires_only_matching_panel(self):
        await self.open()
        closes = []
        self.bridge._light_control = NS(tile_event_binding_changed=lambda card_id:
            closes.append(self.owner.observe_tile_event_binding(card_id)))
        self.assertIsNone(self.owner.observe_tile_event_binding('other-card'))
        self.assertIsNotNone(self.owner._selection)
        self.remove()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(closes[0]['reason'], 'capabilities_changed')
        self.replace_registration()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.callback_calls, [])

    async def test_final_scheduled_callback_rechecks_binding_and_callback_rejection(self):
        await self.open()
        self.accept = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]['reason'], 'service_error')
        self.assertEqual(len(self.callback_calls), 1)
        self.assertEqual(self.bus, [])
        self.accept = True
        original = self.owner._run_dispatch
        async def replace_before_job(*args):
            self.remove()
            self.replace_registration()
            return await original(*args)
        self.owner._run_dispatch = replace_before_job
        await self.send(self.command(2))
        self.assertEqual(len(self.callback_calls), 1)
        self.assertEqual(self.bus, [])

    async def test_callback_throw_before_effect_is_terminal_and_duplicate_never_retries(self):
        calls = []
        def throwing(payload, context):
            calls.append((payload, context))
            raise RuntimeError("owned callback rejected before effect")
        self.bridge.register_tile_event('card-2', self.entity, throwing)
        await self.open()
        registration, payload = self.registration(), shared.wire(self.command())
        await self.through_ingress(registration, payload)
        await self.through_ingress(registration, payload)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.results()[-1]['reason'], 'service_error')
        self.assertEqual(self.bus, [])
        self.assertEqual(self.hass.services.calls, [])

    async def test_pending_emit_released_after_close_cannot_dispatch_into_new_selection(self):
        await self.open()
        entered, release = asyncio.Event(), asyncio.Event()
        emit = self.owner.emit
        async def held(value, *args):
            if value.get('status') == 'pending':
                entered.set()
                await release.wait()
            await emit(value, *args)
        self.owner.emit = held
        command = asyncio.create_task(self.owner.async_handle(shared.wire(self.command()), self.user))
        await asyncio.wait_for(entered.wait(), .2)
        await self.owner.async_close()
        await self.open(2)
        selected = self.owner._selection
        release.set()
        await asyncio.wait_for(command, .3)
        await asyncio.sleep(0)
        self.assertIs(self.owner._selection, selected)
        self.assertIsNone(selected.command)
        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.bus, [])

    async def test_shared_registry_listener_closes_disable_enable_and_remove_recreate_ABA(self):
        listeners, removed = [], []
        self.hass.bus.async_listen = lambda kind, callback: (
            listeners.append((kind, callback)) or (lambda: removed.append(kind)))
        self.bridge._replace_tile_subscription()
        self.assertEqual([kind for kind, _ in listeners], ['entity_registry_updated'])
        changed = listeners[0][1]
        closes = []
        self.bridge._light_control = NS(tile_event_binding_changed=lambda card_id:
            closes.append(self.owner.observe_tile_event_binding(card_id)))
        original = self.hass.entity_registry.entries[self.entity]
        for seq, kind in enumerate(('disable', 'remove'), 1):
            await self.open(seq)
            selected = self.owner._selection
            changed(NS(data={'entity_id': self.entity, 'action': 'update', 'changes': {'name': 'old name', 'icon': None}}))
            self.assertIs(self.owner._selection, selected)
            self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
            await self.owner.async_handle(shared.wire(self.command()), self.user)
            task = self.owner._selection.command.task
            await asyncio.wait_for(self.auth_entered.wait(), .2)
            if kind == 'disable':
                original.disabled_by = 'user'
            else:
                del self.hass.entity_registry.entries[self.entity]
            changed(NS(data={'entity_id': self.entity, 'action': 'update' if kind == 'disable' else 'remove'}))
            original.disabled_by = None
            self.hass.entity_registry.entries[self.entity] = original
            changed(NS(data={'entity_id': self.entity, 'action': 'update' if kind == 'disable' else 'create'}))
            self.auth_gate.set()
            await asyncio.wait_for(task, .3)
            self.auth_gate = None
            self.assertIsNone(self.owner._selection)
        self.assertEqual([row['reason'] for row in closes if row], ['capabilities_changed'] * 2)
        self.assertEqual(self.callback_calls, [])
        self.assertEqual(self.bus, [])
        self.bridge._closed = True
        self.bridge._replace_tile_subscription()
        self.assertEqual(removed, ['entity_registry_updated'])

    async def test_timestamp_metadata_does_not_cancel_press_but_unavailable_ABA_does(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        task = self.owner._selection.command.task
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change('2026-11-06T12:00:00+00:00')
        self.auth_gate.set()
        await asyncio.wait_for(task, .4)
        self.assertEqual(len(self.callback_calls), 1)
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(2)), self.user)
        task = self.owner._selection.command.task
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change('unavailable')
        self.change('2026-11-06T12:00:00+00:00')
        self.auth_gate.set()
        await asyncio.wait_for(task, .4)
        self.assertEqual(len(self.callback_calls), 1)


class TileEventSchemaTests(unittest.TestCase):
    def test_layout_explicit_migration_and_projection_both_profiles(self):
        card = direct.event_card() | {'action': deepcopy(events.PANEL_ACTION)}
        document = base.document([card]) | {'version': 3}
        self.assertEqual(base.layout.validate_layout(document), document)
        self.assertTrue(events.is_event_definition(card))
        self.assertTrue(events.is_event_panel(card))
        self.assertFalse(events.is_event_card(card))
        for change in ({'entity_id': 'event.someone_else'}, {'type': 'entity'}, {'action': events.PANEL_ACTION | {'event_type': 'x'}}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(document | {'cards': [card | change]})
        hass, _ = base.environment()
        for profiles in ((), ('action',), ('tile_event',), ('action', 'tile_event')):
            row = base.cards.presentation_payload(hass, [card], press_enabled_supported=True,
                panel_extra_profiles=profiles, event_card_ids={card['id']})['cards'][2]
            self.assertEqual(row.get('control_kind'), 'panel' if len(profiles) == 2 else None)
            self.assertNotEqual(row['subtitle'], 'Automation')
        self.assertEqual(base.cards.card_entity_ids([card]), [])

    def test_additive_profiles_exact_bounds_and_action2_dependency(self):
        offered = list(features.PROFILES)
        channel = 'a'*32
        self.assertEqual(len(offered), 8)
        self.assertEqual(len(features.payload(channel, offered).encode()), 341)
        bound = json.loads(features.payload(channel, offered)) | {'accepted': True}
        self.assertEqual(len(shared.wire(bound).encode()), 357)
        self.assertFalse(features.valid_profiles([{'name': 'tile_event', 'version': 1}]))
        self.assertFalse(features.valid_profiles([{'name': 'action', 'version': 1}, {'name': 'tile_event', 'version': 1}]))
        old = [p for p in offered if p['name'] != 'tile_event']
        reply = NS(success=True, response_data=features.payload(channel, old).encode())
        self.assertEqual(features.decode_response(reply, channel=channel, offered=offered)['profiles'], old)

    def test_new_subtype_codec_requires_both_caps_and_exact_closed_fields(self):
        state = base.State('event.owned', 'unknown')
        hass, _ = base.environment()
        domain = action.ActionDomain('tile_event', 1)
        observed = action.ActionObservation.from_ha(hass, state, domain)
        value = codec.envelope('grant', channel='a'*32, token='b'*32, open_seq=1, slot=2, card_id='owned', revision=4,
            control_kind='panel', state_seq=1, ttl_ms=30000, title='Event', panel_type='action', panel_caps=domain.descriptor(),
            panel_state=observed.descriptor(), available=True, eligible_actions=1, state_generation=1)
        kw = {'extra_profiles': ('action', 'tile_event'), 'action_dispatched': True}
        self.assertEqual(codec.decode(codec.encode(value, **kw), **kw), value)
        for kwargs in ({}, {'extra_profiles': ('action',)}, {'extra_profiles': ('tile_event',), 'action_dispatched': True},
                       {'extra_profiles': ('action', 'tile_event')}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value, **kwargs)
        for caps in ({'operations': 2}, {'skip_condition': True}, {'run_blocked': 'needs_parameters'}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value | {'panel_caps': value['panel_caps'] | caps}, **kw)
        with self.assertRaises(action.ActionPanelError):
            domain.service_action('event.owned', 'press')


if __name__ == '__main__':
    unittest.main()
