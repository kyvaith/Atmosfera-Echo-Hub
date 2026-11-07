"""Core's three repeat modes over the existing Choice session and service fence."""
import asyncio
from copy import deepcopy
from enum import IntFlag,StrEnum
import importlib
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import test_ha_layout as base
import test_choice_control as shared

model=importlib.import_module('_atmosfera_test.choice_domain')
ACTION={'kind':'control','control':'choice','property':'repeat'}
OPTIONS=['off','one','all']


class MediaRepeatModelTests(unittest.TestCase):
    def setUp(self):
        self.state=base.State('media_player.test','playing',{'supported_features':262144,'repeat':'off','media_title':'Track QA'})
        self.hass,_=base.environment(states=[self.state],services=['media_player.repeat_set'])

    def test_v3_only_and_exact_core_enum_ignore_invented_device_modes(self):
        self.assertEqual(base.layout.validate_action(ACTION,self.state.entity_id,layout_version=3),ACTION)
        self.assertTrue(base.layout.device_profile()['schema_media_repeat'])
        for entity,version in (('remote.test',3),(self.state.entity_id,2)):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action(ACTION,entity,layout_version=version)
        self.state.attributes['repeat_modes']=['vendor','forever']
        class Features(IntFlag):REPEAT_SET=262144
        self.state.attributes['supported_features']=Features.REPEAT_SET
        self.assertEqual(model.choice_domain(self.state.entity_id,self.state.attributes,'repeat').options,tuple(OPTIONS))
        for features in (0,True,-1,'262144',2**53+262144):
            with self.assertRaises(model.ChoiceDomainError):model.choice_domain(self.state.entity_id,self.state.attributes|{'supported_features':features},'repeat')

    def test_core_strenum_normalized_only_after_exact_membership_and_missing_never_off(self):
        class Mode(StrEnum):OFF='off';ONE='one';ALL='all'
        for value in Mode:
            self.state.attributes['repeat']=value
            raw=model.choice_state(self.state.entity_id,'playing',self.state.attributes,'repeat');self.assertIs(type(raw),str);self.assertEqual(raw,value.value)
        for value in (None,True,0,1,'OFF','missing',[],{}):
            self.state.attributes['repeat']=value
            self.assertIsNone(model.choice_state(self.state.entity_id,'playing',self.state.attributes,'repeat'))
            self.assertFalse(model.choice_is_empty(self.state.entity_id,'playing',self.state.attributes,'repeat'))
        for state in ('off','standby','unknown','unavailable'):
            self.state.state=state;self.assertEqual(base.cards._choice_control_metadata(self.hass,self.state,'repeat'),{})

    def test_exact_live_targets_and_caption_context_with_ha_labels(self):
        card=base.card(entity=self.state.entity_id,action=ACTION)
        for value in OPTIONS:base.cards.validate_live_action(self.hass,self.state,{'service':'media_player.repeat_set','data':{'repeat':value}})
        for value in ('absent',True,None):
            with self.assertRaises(base.layout.LayoutError):base.cards.validate_live_action(self.hass,self.state,{'service':'media_player.repeat_set','data':{'repeat':value}})
        self.assertEqual(base.cards._card_subtitle(self.hass,card,self.state,'en'),'Repeat: Off')
        self.assertEqual(base.cards._card_subtitle(self.hass,base.card(entity=self.state.entity_id),self.state,'en'),'Track QA')
        labels={'component.media_player.entity_component._.state_attributes.repeat.state.off':'HA bez powtórzeń'}
        with patch.object(base.cards,'async_get_cached_translations',return_value=labels):
            actual=base.cards._card_subtitle(self.hass,card,self.state,'pl')
            self.assertTrue(actual.startswith('Powt.: HA '))
            self.assertLessEqual(importlib.import_module('_atmosfera_test.caption_width').caption_width(actual),136)
        for data in ({},{'repeat':'one','entity_id':'media_player.other'},{'repeat':False}):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action({'kind':'service','service':'media_player.repeat_set','data':data},self.state.entity_id)

    def test_compact_native_caption_budget_and_editor_metadata_match_for_all_modes(self):
        metrics=importlib.import_module('_atmosfera_test.caption_width')
        for mode in OPTIONS:
            self.state.attributes['repeat']=mode
            meta=base.cards._choice_control_metadata(self.hass,self.state,'repeat')['media_repeat']
            for language in ('pl','en'):
                text=base.cards._media_repeat_caption(self.hass,self.state,language)
                self.assertLessEqual(metrics.caption_width(text),136);self.assertLessEqual(len(text),40)
                self.assertEqual(meta['captions'][language],text)
        self.state.attributes['repeat']='off'
        labels={'component.media_player.entity_component._.state_attributes.repeat.state.off':'Nie powtarzaj tego utworu'}
        with patch.object(base.cards,'async_get_cached_translations',return_value=labels):
            text=base.cards._media_repeat_caption(self.hass,self.state,'pl')
            self.assertTrue(text.startswith('Powt.: '));self.assertTrue(text.endswith('...'));self.assertLessEqual(metrics.caption_width(text),136)


class MediaRepeatOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f=shared.ChoiceOwnerTests();await self.f.asyncSetUp();f=self.f
        f.state=base.State('media_player.test','playing',{'supported_features':262144,'repeat':'off','volume_level':.42,'media_title':'Track QA','is_volume_muted':False,'shuffle':False})
        f.hass.states.items={f.state.entity_id:f.state};f.card.update(entity_id=f.state.entity_id,action=deepcopy(ACTION));f.hass.services.names={'media_player.repeat_set'}
        def change(value,power='playing',**attrs):
            f.state.state=power;f.state.attributes.update(repeat=value,**attrs)
            return f.owner.observe_state_event(NS(data={'entity_id':f.state.entity_id,'new_state':f.state}))
        async def service(*args,**kwargs):
            f.hass.services.calls.append((args,kwargs))
            if f.apply:change(args[2]['repeat'])
        f.change=change;f.hass.services.async_call=service

    async def asyncTearDown(self):await self.f.asyncTearDown()

    async def test_exact_modes_duplicate_fenced_and_no_other_media_state_changes(self):
        f=self.f;grant=await f.open();self.assertEqual((grant['options'],grant['index']),(['Off','One track','All tracks'],0))
        value=f.command(1);await f.send(value);await f.send(value)
        self.assertEqual(len(f.hass.services.calls),1)
        args,kwargs=f.hass.services.calls[0];self.assertEqual(args,('media_player','repeat_set',{'entity_id':'media_player.test','repeat':'one'}));self.assertIs(kwargs['context'],f.user)
        self.assertEqual(f.results()[-1]['status'],'state_matches');self.assertEqual(f.state.state,'playing')
        self.assertEqual((f.state.attributes['volume_level'],f.state.attributes['shuffle'],f.state.attributes['is_volume_muted'],f.state.attributes['media_title']),(.42,False,False,'Track QA'))

    async def test_repeat_ABA_during_authorization_and_flagloss_revoke(self):
        f=self.f;await f.open();f.auth_gate=asyncio.Event();f.auth_entered.clear()
        await f.owner.async_handle(f.owner._encode(f.command(1)),f.user);await asyncio.wait_for(f.auth_entered.wait(),.2)
        f.change('all');f.change('off');f.auth_gate.set();await asyncio.wait_for(f.owner._selection.command.task,.3)
        self.assertEqual(f.hass.services.calls,[]);self.assertEqual(f.results()[-1]['reason'],'stale_state')
        await f.owner.async_close();await f.open(seq=2)
        self.assertEqual(f.change('off',supported_features=0)['reason'],'capabilities_changed')

    async def test_unknown_and_offline_never_select_first_or_send(self):
        f=self.f;f.change(None);grant=await f.open();self.assertEqual((grant['index'],grant['available']),(None,False))
        await f.owner.async_close();f.change('off');await f.open(seq=2);f.change('off',power='unavailable')
        self.assertEqual(f.hass.services.calls,[])
