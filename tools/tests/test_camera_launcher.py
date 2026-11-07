"""Manual Camera launcher: host schema, real ingress routing and async fences.

The HA/API objects are doubles. No camera stream or device proof is claimed.
"""
import ast
import asyncio
import sys
from copy import deepcopy
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch

import pytest
import voluptuous as vol
import test_ha_layout as host

c = host.controller


def card():
    return host.card() | {"type": "entity", "entity_id": "camera.door", "icon": "camera",
                          "action": {"kind": "camera_preview", "duration_seconds": 35}}


def bridge():
    b = host.BridgeTests().bridge()
    b.device_id = "owned-display"
    b.hass.states = host.States([host.State("camera.door", "idle"), host.State("camera.unlisted", "idle")])
    b.layout = host.document([card()], revision=4) | {"version": 3}
    b.entry.options["home_layout"] = deepcopy(b.layout)
    b.entry.runtime_data = b
    b.tile_cards = host.cards.normalize_cards(b.layout["cards"])
    b.saved_revision = b.sent_revision = 4
    b._context_press_version = b._press_enabled_version = 1
    b.sources = [c.CameraSource("camera.door", "Door", "https://local/opaque-proxy")]
    b.available = True
    b._camera_catalog_generation = 1
    b._push_lock = asyncio.Lock()
    b.current_option = "Door"
    b.async_schedule_tile_push = lambda **_: None
    b._async_build_sources = AsyncMock(return_value=b.sources)
    b._notify_listeners = lambda: None
    runtime = b.esphome_entry.runtime_data
    runtime.name = "test-node"
    runtime.client.execute_service = AsyncMock(return_value=NS(success=True, response_data=b'{"status":"opened"}'))
    arg = c.UserServiceArgType
    b.preview = NS(supports_response=c.SupportsResponseType.ONLY, args=[NS(name=n, type=t) for n,t in
        (("source_key",arg.STRING),("event_id",arg.STRING),("duration_seconds",arg.INT))])
    b.keyed = object()
    b.actions = {c.API_ACTION_DOORBELL_PREVIEW: b.preview, c.API_ACTION_SET_KEYED_SOURCES: b.keyed}
    b._find_api_action = b.actions.get
    b._keyed_camera_catalog = (runtime, runtime.client, 0, 1, ("camera.door",), tuple(b.sources), b.keyed)
    b._notifications.add_doorbell = AsyncMock()
    return b


def registration(b):
    """Compile the actual public handler, number validator and registration schema."""
    tree = ast.parse((host.ROOT / "custom_components/atmosfera_echo_hub/__init__.py").read_text("utf8"))
    nodes = [n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))
             and n.name in {"_report_number", "async_report_tile_context_press"}]
    schema = next(k.value for n in ast.walk(tree) if isinstance(n,ast.Call) and
                  isinstance(n.func,ast.Attribute) and n.func.attr=="async_register" and
                  len(n.args)>1 and isinstance(n.args[1],ast.Name) and n.args[1].id=="SERVICE_REPORT_TILE_CONTEXT_PRESS"
                  for k in n.keywords if k.arg=="schema")
    namespace = dict(hass=b.hass, vol=vol, cv=NS(string=str), ServiceCall=NS, DOMAIN=c.DOMAIN,
        ATTR_NODE_NAME="node_name", ATTR_SLOT="slot", ATTR_CARD_ID="card_id", ATTR_REVISION="revision",
        CAROUSEL_SLOT_COUNT=32, MAX_REVISION=2**53-1, parse_report_integer=host.layout.parse_report_integer,
        LayoutError=host.layout.LayoutError)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),"<actual-context-ingress>","exec"),namespace)
    return namespace["async_report_tile_context_press"],eval(compile(ast.Expression(schema),"<actual-context-schema>","eval"),namespace)


async def press(b, context=None):
    handler,schema=registration(b)
    data=schema({"node_name":"test-node","slot":str(card()["slot"]),"card_id":card()["id"],"revision":"4"})
    await handler(NS(data=data,context=context or NS(id="context-one",user_id="user",parent_id=None)))


@pytest.mark.parametrize("action", [
    {"kind":"camera_preview","duration_seconds":True}, {"kind":"camera_preview","duration_seconds":14},
    {"kind":"camera_preview","duration_seconds":91}, {"kind":"camera_preview","duration_seconds":35.0},
    {"kind":"camera_preview","duration_seconds":35,"url":"https://arbitrary"},
    {"kind":"camera_preview","duration_seconds":35,"service":"camera.turn_on"}, {"kind":"default"},
    {"kind":"service","service":"camera.turn_on","data":{}}, {"kind":"none","duration_seconds":35},
])
def test_camera_schema_closed(action):
    with pytest.raises(host.layout.LayoutError):
        host.layout.validate_layout(host.document([card() | {"action":action}]) | {"version":3})


def test_schema_catalogue_projection_and_save_are_passive():
    b=bridge()
    assert host.layout.validate_layout(b.layout)==b.layout
    with pytest.raises(host.layout.LayoutError):host.layout.validate_layout(b.layout | {"version":2})
    with pytest.raises(host.layout.LayoutError):host.layout.validate_layout(host.document([card() | {"type":"action"}]) | {"version":3})
    catalog=host.cards.entity_catalogue(b.hass,camera_entity_ids=b.camera_entity_ids)
    assert [x['entity_id'] for x in catalog['entities']]==['camera.door']
    assert catalog['entities'][0]['camera_preview']['allowlisted'] is True
    assert 'url' not in str(catalog) and host.cards.resolve_action(b.hass,card()) is None
    row=host.cards.presentation_payload(b.hass,[card()],press_enabled_supported=True,camera_preview_entities=b.camera_preview_entities)['cards'][2]
    assert row['press_enabled'] and row['icon']=='\ue04b' and 'control_kind' not in row
    assert host.cards.presentation_payload(b.hass,[card()],press_enabled_supported=True)['cards'][2]['press_enabled'] is False
    assert host.panel._legacy_cards(b.layout)[0]['action']=={'kind':'none'}
    host.panel._validate_actions(b.hass,b.layout,b.entry)
    with pytest.raises(host.layout.LayoutError):host.panel._validate_actions(b.hass,b.layout,NS(options={},data={}))
    b.esphome_entry.runtime_data.client.execute_service.assert_not_awaited()


@pytest.mark.parametrize('response',[b'{"status":"opened"}',b'{"status":"busy"}',b'{"status":"unexpected"}',None])
def test_actual_ingress_one_request_same_context_duplicate_no_service_or_notification(response):
    async def run():
        b=bridge();execute=b.esphome_entry.runtime_data.client.execute_service
        execute.return_value=NS(success=True,response_data=response)
        registry=NS(async_get_entity_id=lambda *_:'notify.owned_display')
        auth=AsyncMock(return_value=True)
        with patch.object(c.er,'async_get',return_value=registry),patch.object(c,'authorize_ha_context',auth):
            await press(b);await press(b)
        assert execute.await_count==1
        payload=execute.await_args.args[1]
        assert set(payload)=={'source_key','event_id','duration_seconds'} and payload['source_key']==b.sources[0].key
        assert len(payload['event_id'])==32 and payload['duration_seconds']==35
        assert [a.args[2] for a in auth.await_args_list]==['notify.owned_display','camera.door']
        assert not b.hass.services.calls
        b._notifications.add_doorbell.assert_not_awaited()
    asyncio.run(run())


@pytest.mark.parametrize('mutation', ['layout_aba','hidden','retarget','entry_before_listener','source_aba','reconnect','client','unload','allowlist','api','state','context','page_hidden'])
@pytest.mark.parametrize('boundary',[1,2])
def test_async_authorization_fences(mutation,boundary):
    async def run():
        b=bridge();calls=0
        async def authorize(_hass,context,_entity):
            nonlocal calls
            calls+=1
            if calls==boundary:
                if mutation=='layout_aba':b.saved_revision=6;b.entry.options['home_layout']['revision']=6
                elif mutation=='hidden':b.entry.options['home_layout']['cards'][0]['visible']=False
                elif mutation=='retarget':b.entry.options['home_layout']['cards'][0]['entity_id']='camera.unlisted'
                elif mutation=='entry_before_listener':b.entry.options['home_layout']['revision']=5
                elif mutation=='source_aba':b._invalidate_camera_catalog()
                elif mutation=='reconnect':b._connection_epoch+=1
                elif mutation=='client':b.esphome_entry.runtime_data=NS(available=True,client=NS())
                elif mutation=='unload':b._closed=True
                elif mutation=='allowlist':b.entry.options['cameras']=[]
                elif mutation=='api':b.actions[c.API_ACTION_DOORBELL_PREVIEW]=deepcopy(b.preview)
                elif mutation=='state':b.hass.states.items['camera.door'].state='unavailable'
                elif mutation=='context':context.user_id='other'
                elif mutation=='page_hidden':b.entry.options['home_layout']['home_order']=['home-1','home-3']
            return True
        original=b.esphome_entry.runtime_data.client.execute_service
        with patch.object(c.er,'async_get',return_value=NS(async_get_entity_id=lambda *_:'notify.owned_display')),patch.object(c,'authorize_ha_context',authorize):
            await press(b)
        original.assert_not_awaited()
        assert not b.hass.services.calls
    asyncio.run(run())


@pytest.mark.parametrize('mutation',['no_proof','legacy_context','no_press_enabled','optional_api','bad_args','no_source','offline','unknown','stale_revision'])
def test_missing_capability_never_dispatches(mutation):
    async def run():
        b=bridge()
        if mutation=='no_proof':b._keyed_camera_catalog=None
        elif mutation=='legacy_context':b._context_press_version=0
        elif mutation=='no_press_enabled':b._press_enabled_version=0
        elif mutation=='optional_api':b.preview.supports_response=c.SupportsResponseType.OPTIONAL
        elif mutation=='bad_args':b.preview.args=[]
        elif mutation=='no_source':b.sources=[]
        elif mutation=='offline':b.esphome_entry.runtime_data.available=False
        elif mutation=='unknown':b.hass.states.items['camera.door'].state='unknown'
        elif mutation=='stale_revision':b.sent_revision=3
        await press(b)
        b.esphome_entry.runtime_data.client.execute_service.assert_not_awaited()
    asyncio.run(run())


def test_keyed_ack_proof_retires_on_awaited_catalog_connection_change():
    async def run():
        b=bridge()
        async def execute(*_,**__):
            b._connection_epoch+=1
            return NS(success=True,response_data=b'{"accepted":true}')
        b.esphome_entry.runtime_data.client.execute_service=execute
        assert await b._async_push_sources()
        assert b._keyed_camera_catalog is None and not b.camera_preview_supported
    asyncio.run(run())


@pytest.mark.parametrize('boundary',['build','ack','selection'])
def test_same_runtime_client_replacement_cannot_inherit_old_keyed_ack(boundary):
    async def run():
        b=bridge();runtime=b.esphome_entry.runtime_data
        select=object();b.actions[c.API_ACTION_SELECT_SOURCE]=select
        replacement=NS(execute_service=AsyncMock(return_value=NS(success=True,response_data=b'{"accepted":true}')))
        async def build():
            if boundary=='build':runtime.client=replacement
            return b.sources
        async def execute(action,*_,**__):
            if boundary==('selection' if action is select else 'ack'):runtime.client=replacement
            return NS(success=True,response_data=b'{"accepted":true}')
        b._async_build_sources=build;runtime.client.execute_service=execute
        assert await b._async_push_sources()
        assert b._keyed_camera_catalog is None and not b.camera_preview_supported
    asyncio.run(run())


@pytest.mark.parametrize('reply,admitted',[(b'{"accepted":true}',True),(b'{"accepted":1}',False),(b'{"accepted":false}',False)])
def test_only_boolean_keyed_ack_publishes_fresh_manual_capability(reply,admitted):
    async def run():
        b=bridge();b._keyed_camera_catalog=None
        b.esphome_entry.runtime_data.client.execute_service.return_value=NS(success=True,response_data=reply)
        await b._async_push_sources()
        assert b.camera_preview_supported is admitted
        assert b.camera_preview_entities==(('camera.door',) if admitted else ())
    asyncio.run(run())


def test_denied_and_concurrent_manual_requests_never_queue():
    async def run():
        b=bridge();entered=asyncio.Event();release=asyncio.Event()
        async def auth(*_):entered.set();await release.wait();return False
        with patch.object(c.er,'async_get',return_value=NS(async_get_entity_id=lambda *_:'notify.owned_display')),patch.object(c,'authorize_ha_context',auth):
            task=asyncio.create_task(press(b));await entered.wait();await press(b);release.set();await task
        b.esphome_entry.runtime_data.client.execute_service.assert_not_awaited()
        assert not b._manual_preview_busy
    asyncio.run(run())


@pytest.mark.parametrize('denied',[None,'notify.owned_display','camera.door'])
def test_actual_ha_context_permission_policy_controls_both_targets(denied):
    class Context:
        id='real-context-shape';user_id='user';parent_id=None
    async def run():
        b=bridge()
        permissions=NS(check_entity=lambda entity,policy:policy=='control' and entity!=denied)
        b.hass.auth=NS(async_get_user=AsyncMock(return_value=NS(is_active=True,permissions=permissions)))
        with patch.object(sys.modules['homeassistant.core'],'Context',Context,create=True), \
             patch.dict(sys.modules,{'homeassistant.auth.permissions.const':NS(POLICY_CONTROL='control')}), \
             patch.object(c.er,'async_get',return_value=NS(async_get_entity_id=lambda *_:'notify.owned_display')):
            await press(b,Context())
        assert b.esphome_entry.runtime_data.client.execute_service.await_count==(1 if denied is None else 0)
        assert not b.hass.services.calls
    asyncio.run(run())


@pytest.mark.parametrize("language,ready,unavailable", [("pl", "Otwórz", "Niedostępna"), ("en", "Open", "Unavailable")])
def test_camera_caption_is_short_without_changing_title_action_or_readiness(language, ready, unavailable):
    b = bridge()
    saved = card() | {"title": "My custom camera name"}
    original = deepcopy(saved)
    for eligible, expected in [(True, ready), (False, unavailable)]:
        rows = host.cards.presentation_payload(b.hass, [saved], language=language,
            press_enabled_supported=True, camera_preview_entities=("camera.door",) if eligible else ())['cards']
        row = next(row for row in rows if row['slot'] == saved['slot'])
        assert row['subtitle'] == expected
        assert row['title'] == saved['title']
        assert row['press_enabled'] is eligible
        assert saved == original
    b.esphome_entry.runtime_data.client.execute_service.assert_not_awaited()
