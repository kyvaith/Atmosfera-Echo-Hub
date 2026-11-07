"""Exact bounded source inputs, using the existing Choice owner and fence."""
import asyncio
from copy import deepcopy
from enum import IntFlag
import importlib
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import test_ha_layout as base
import test_choice_control as shared

model=importlib.import_module('_atmosfera_test.choice_domain')
ACTION={'kind':'control','control':'choice','property':'source'}
OPTIONS=['HDMI 1','Radio',' Żółty ']


class MediaSourceModelTests(unittest.TestCase):
    def setUp(self):
        self.state=base.State('media_player.test','playing',{'supported_features':2048,'source_list':OPTIONS.copy(),'source':'HDMI 1','media_title':'Track QA'})
        self.hass,_=base.environment(states=[self.state],services=['media_player.select_source'])

    def test_explicit_v3_typed_target_and_exact_bounded_catalogue(self):
        self.assertEqual(base.layout.validate_action(ACTION,'media_player.test',layout_version=3),ACTION)
        self.assertTrue(base.layout.device_profile()['schema_media_source'])
        for entity,version in (('remote.test',3),('media_player.test',2)):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action(ACTION,entity,layout_version=version)
        for values in ([],['A']*2,['a']*9,['ą'*17],['bad\n'],['unknown'],[True]):
            with self.assertRaises(model.ChoiceDomainError):model.choice_domain(self.state.entity_id,self.state.attributes|{'source_list':values},'source')
        self.assertEqual(model.choice_domain(self.state.entity_id,self.state.attributes,'source').options,tuple(OPTIONS))
        class Features(IntFlag):SELECT_SOURCE=2048
        self.assertEqual(len(model.choice_domain(self.state.entity_id,self.state.attributes|{'supported_features':Features.SELECT_SOURCE,'source_list':[str(i)for i in range(8)]},'source').options),8)
        for flags in (0,True,-1,'2048',2**53+2048):
            with self.assertRaises(model.ChoiceDomainError):model.choice_domain(self.state.entity_id,self.state.attributes|{'supported_features':flags},'source')

    def test_live_target_and_power_rechecked_and_foreign_fields_rejected(self):
        valid={'service':'media_player.select_source','data':{'source':' Żółty '}}
        base.cards.validate_live_action(self.hass,self.state,valid)
        descriptors=base.cards.entity_actions(self.hass,self.state)
        self.assertEqual(descriptors,[{'service':'media_player.select_source','fields':{'source':{'type':'select','required':True,'options':OPTIONS}}}])
        for value in ('Absent',True,None):
            with self.assertRaises(base.layout.LayoutError):base.cards.validate_live_action(self.hass,self.state,valid|{'data':{'source':value}})
        for data in ({'source':'Radio','entity_id':'media_player.other'},{'source':1},{}):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action({'kind':'service','service':'media_player.select_source','data':data},self.state.entity_id)
        for state in ('off','standby','unknown','unavailable'):
            self.state.state=state;self.assertEqual(base.cards._choice_control_metadata(self.hass,self.state,'source'),{})
            with self.assertRaises(base.layout.LayoutError):base.cards.validate_live_action(self.hass,self.state,valid)

    def test_unknown_source_never_becomes_first_or_empty_and_caption_is_observed(self):
        card=base.card(entity=self.state.entity_id,action=ACTION)
        self.assertEqual(base.cards._card_subtitle(self.hass,card,self.state,'pl'),'HDMI 1')
        for value in (None,'Missing',True):
            self.state.attributes['source']=value
            self.assertIsNone(model.choice_domain(self.state.entity_id,self.state.attributes,'source').observed_index(model.choice_state(self.state.entity_id,self.state.state,self.state.attributes,'source')))
            self.assertFalse(model.choice_is_empty(self.state.entity_id,self.state.state,self.state.attributes,'source'))
            self.assertEqual(base.cards._card_subtitle(self.hass,card,self.state,'en'),'Unknown')
        self.assertEqual(base.cards._card_subtitle(self.hass,base.card(entity=self.state.entity_id),self.state,'en'),'Track QA')
        self.state.attributes['source']='Radio'
        self.assertEqual(base.cards._choice_control_metadata(self.hass,self.state,'source')['media_source']['index'],1)
        with patch.object(base.cards,'async_get_cached_translations',return_value={'component.media_player.entity_component._.state_attributes.source.state.Radio':'HA Radio'}):
            self.assertEqual(base.cards._card_subtitle(self.hass,card,self.state,'pl'),'HA Radio')

    def test_long_home_caption_and_preview_fit_compact_budget_but_service_keeps_full_name(self):
        name='Bluetooth Living Room Speaker'
        self.state.attributes.update(source_list=[name,'HDMI 2 - Salon - Telewizor'],source=name)
        metrics=importlib.import_module('_atmosfera_test.caption_width')
        self.assertGreater(metrics.caption_width(name),136)
        text=base.cards._media_source_caption(self.hass,self.state,'pl')
        self.assertTrue(text.endswith('...'));self.assertLessEqual(metrics.caption_width(text),136)
        meta=base.cards._choice_control_metadata(self.hass,self.state,'source')['media_source']
        self.assertEqual(meta['captions']['pl'],text);self.assertEqual(meta['options'][0],name)
        base.cards.validate_live_action(self.hass,self.state,{'service':'media_player.select_source','data':{'source':name}})


class MediaSourceOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f=shared.ChoiceOwnerTests();await self.f.asyncSetUp();f=self.f
        f.state=base.State('media_player.test','playing',{'supported_features':2048,'source_list':OPTIONS.copy(),'source':'HDMI 1','volume_level':.42,'media_title':'Track QA','is_volume_muted':False})
        f.hass.states.items={f.state.entity_id:f.state};f.card.update(entity_id=f.state.entity_id,action=deepcopy(ACTION));f.hass.services.names={'media_player.select_source'}
        def change(value,power='playing',**attrs):
            f.state.state=power;f.state.attributes.update(source=value,**attrs)
            return f.owner.observe_state_event(NS(data={'entity_id':f.state.entity_id,'new_state':f.state}))
        async def service(*args,**kwargs):
            f.hass.services.calls.append((args,kwargs))
            if f.apply:change(args[2]['source'])
        f.change=change;f.hass.services.async_call=service

    async def asyncTearDown(self):await self.f.asyncTearDown()

    async def send(self,value):
        f=self.f;result=await f.owner.async_handle(f.owner._encode(value),f.user)
        if f.owner._selection and f.owner._selection.command:await asyncio.wait_for(f.owner._selection.command.task,.5)
        return result

    async def test_one_exact_absolute_source_duplicate_fenced_no_other_state_changes(self):
        f=self.f;grant=await f.open();self.assertEqual((grant['options'],grant['index']),(OPTIONS,0))
        value=f.command(2);await self.send(value);await self.send(value)
        self.assertEqual(len(f.hass.services.calls),1)
        args,kwargs=f.hass.services.calls[0];self.assertEqual(args,('media_player','select_source',{'entity_id':'media_player.test','source':' Żółty '}));self.assertIs(kwargs['context'],f.user)
        self.assertEqual(f.results()[-1]['status'],'state_matches');self.assertEqual(f.state.state,'playing')
        self.assertEqual((f.state.attributes['volume_level'],f.state.attributes['is_volume_muted'],f.state.attributes['media_title']),(.42,False,'Track QA'))

    async def test_source_ABA_during_authorization_and_reorder_revoke(self):
        f=self.f;await f.open();f.auth_gate=asyncio.Event();f.auth_entered.clear()
        await f.owner.async_handle(f.owner._encode(f.command(1)),f.user);await asyncio.wait_for(f.auth_entered.wait(),.2)
        f.change('Radio');f.change('HDMI 1');f.auth_gate.set();await asyncio.wait_for(f.owner._selection.command.task,.3)
        self.assertEqual(f.hass.services.calls,[]);self.assertEqual(f.results()[-1]['reason'],'stale_state')
        await f.owner.async_close();await f.open(seq=2)
        self.assertEqual(f.change('HDMI 1',source_list=OPTIONS[::-1])['reason'],'capabilities_changed')

    async def test_unknown_disables_apply_and_flag_loss_revokes(self):
        f=self.f;f.change(None);grant=await f.open();self.assertEqual((grant['index'],grant['available']),(None,False))
        await f.owner.async_close();f.change('HDMI 1');await f.open(seq=2)
        self.assertEqual(f.change('HDMI 1',supported_features=0)['reason'],'capabilities_changed')
        self.assertEqual(f.hass.services.calls,[])
