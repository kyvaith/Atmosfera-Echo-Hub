"""Bounded Remote activities over the existing Choice owner, including off."""
import asyncio
from copy import deepcopy
from enum import IntFlag
import importlib
from types import SimpleNamespace as NS
import unittest
import test_ha_layout as base
import test_choice_control as shared

model=importlib.import_module('_atmosfera_test.choice_domain')
ACTION={'kind':'control','control':'choice','property':'activity'}
OPTIONS=['Telewizja','Radio',' Żółty ']


class RemoteActivityModelTests(unittest.TestCase):
    def setUp(self):
        self.state=base.State('remote.test','off',{'supported_features':4,'activity_list':OPTIONS.copy(),'current_activity':'Telewizja'})
        self.hass,_=base.environment(states=[self.state],services=['remote.turn_on','remote.turn_off'])

    def test_explicit_v3_only_and_bounded_catalogue(self):
        doc=base.document([base.card(entity='remote.test',action=ACTION)])|{'version':3}
        self.assertEqual(base.layout.validate_layout(doc),doc)
        self.assertTrue(base.layout.device_profile()['schema_remote_activity'])
        for entity,version in (('fan.test',3),('remote.test',2)):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action(ACTION,entity,layout_version=version)
        for values in ([],['A']*2,['a']*9,['ą'*17],['bad\n'],['unknown']):
            with self.assertRaises(model.ChoiceDomainError):model.choice_domain('remote.test',self.state.attributes|{'activity_list':values},'activity')
        self.assertEqual(len(model.choice_domain('remote.test',self.state.attributes|{'activity_list':[str(i)for i in range(8)]},'activity').options),8)
        class Features(IntFlag):ACTIVITY=4
        self.assertEqual(model.choice_domain('remote.test',self.state.attributes|{'supported_features':Features.ACTIVITY},'activity').options,tuple(OPTIONS))
        for flags in (0,True,-1,'4',2**53+4):
            with self.assertRaises(model.ChoiceDomainError):model.choice_domain('remote.test',self.state.attributes|{'supported_features':flags},'activity')

    def test_off_ignores_retained_activity_but_unknown_on_never_becomes_empty(self):
        attrs=self.state.attributes
        self.assertIsNone(model.choice_state('remote.test','off',attrs,'activity'))
        self.assertTrue(model.choice_is_empty('remote.test','off',attrs,'activity'))
        self.assertEqual(base.cards._choice_control_metadata(self.hass,self.state,'activity'),{'remote_activity':{'options':OPTIONS,'index':None,'empty':True}})
        self.state.state='on';self.assertEqual(model.choice_state('remote.test','on',attrs,'activity'),'Telewizja')
        for value in (None,'unknown','missing'):
            attrs['current_activity']=value
            self.assertFalse(model.choice_is_empty('remote.test','on',attrs,'activity'))
            self.assertIsNone(model.choice_domain('remote.test',attrs,'activity').observed_index(model.choice_state('remote.test','on',attrs,'activity')))
        for state in ('unknown','unavailable'):
            self.state.state=state
            self.assertEqual(base.cards._choice_control_metadata(self.hass,self.state,'activity'),{})

    def test_trusted_live_gate_rechecks_target_feature_state_and_service(self):
        action={'service':'remote.turn_on','data':{'activity':'Radio'}}
        for power in ('on','off'):
            self.state.state=power;base.cards.validate_live_action(self.hass,self.state,action)
        for target in ('Absent',True,0,None):
            with self.assertRaises(base.layout.LayoutError):base.cards.validate_live_action(self.hass,self.state,{'service':'remote.turn_on','data':{'activity':target}})
        self.state.attributes['supported_features']=0
        with self.assertRaises(base.layout.LayoutError):base.cards.validate_live_action(self.hass,self.state,action)
        self.state.attributes['supported_features']=4;self.state.state='unavailable'
        with self.assertRaises(base.layout.LayoutError):base.cards.validate_live_action(self.hass,self.state,action)
        self.state.state='on';self.hass.services.names.clear()
        with self.assertRaises(base.layout.LayoutError):base.cards.validate_live_action(self.hass,self.state,action)
        with self.assertRaises(base.layout.LayoutError):base.layout.validate_action({'kind':'service',**action},'remote.test')


class RemoteActivityOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f=shared.ChoiceOwnerTests();await self.f.asyncSetUp();f=self.f
        f.state=base.State('remote.test','on',{'supported_features':4,'activity_list':OPTIONS.copy(),'current_activity':'Telewizja'})
        f.hass.states.items={f.state.entity_id:f.state};f.card.update(entity_id=f.state.entity_id,action=deepcopy(ACTION));f.hass.services.names={'remote.turn_on','remote.turn_off'}
        def change(value,power='on',**attrs):
            f.state.state=power;f.state.attributes.update(current_activity=value,**attrs)
            return f.owner.observe_state_event(NS(data={'entity_id':f.state.entity_id,'new_state':f.state}))
        async def service(*args,**kwargs):
            f.hass.services.calls.append((args,kwargs))
            if f.apply:change(args[2]['activity'])
        f.change=change;f.hass.services.async_call=service

    async def asyncTearDown(self):await self.f.asyncTearDown()

    async def send(self,value):
        f=self.f;result=await f.owner.async_handle(f.owner._encode(value),f.user)
        if f.owner._selection and f.owner._selection.command:await asyncio.wait_for(f.owner._selection.command.task,.5)
        return result

    async def test_exact_activity_on_running_remote_and_duplicate_is_not_repeated(self):
        f=self.f;grant=await f.open();self.assertEqual(grant['options'],OPTIONS)
        value=f.command(2);await self.send(value);await self.send(value)
        self.assertEqual(len(f.hass.services.calls),1)
        args,kwargs=f.hass.services.calls[0];self.assertEqual(args,('remote','turn_on',{'entity_id':'remote.test','activity':' Żółty '}));self.assertIs(kwargs['context'],f.user)
        self.assertEqual(f.results()[-1]['status'],'state_matches')

    async def test_off_needs_empty_negotiation_and_retained_name_does_not_skip_apply(self):
        f=self.f;f.change('Telewizja',power='off');grant=await f.open();self.assertEqual((grant['index'],grant['available']),(None,False))
        await f.owner.async_close();f.owner.accept_empty_choice_features(f.owner.channel,1)
        grant=await f.open(seq=2);self.assertEqual((grant['index'],grant['available']),(None,True))
        await self.send(f.command(0));self.assertEqual(len(f.hass.services.calls),1)
        self.assertEqual(f.hass.services.calls[0][0],('remote','turn_on',{'entity_id':'remote.test','activity':'Telewizja'}))

    async def test_held_authorization_ABA_and_reordered_catalogue_cancel(self):
        f=self.f;await f.open();f.auth_gate=asyncio.Event();f.auth_entered.clear()
        await f.owner.async_handle(f.owner._encode(f.command(1)),f.user);await asyncio.wait_for(f.auth_entered.wait(),.2)
        f.change('Radio');f.change('Telewizja');f.auth_gate.set();await asyncio.wait_for(f.owner._selection.command.task,.3)
        self.assertEqual(f.hass.services.calls,[]);self.assertEqual(f.results()[-1]['reason'],'stale_state')
        await f.owner.async_close();await f.open(seq=2)
        close=f.change('Telewizja',activity_list=['Radio','Telewizja',' Żółty ']);self.assertEqual(close['reason'],'capabilities_changed')

    async def test_unknown_on_does_not_enable_apply_and_outage_revokes(self):
        f=self.f;f.state.attributes.pop('current_activity');grant=await f.open();self.assertEqual((grant['index'],grant['available']),(None,False))
        await f.owner.async_close();f.change('Telewizja');await f.open(seq=2)
        old=f.command(1);f.change('Telewizja',power='unavailable')
        with self.assertRaises(shared.codec.ProtocolError):await self.send(old)
        self.assertEqual(f.hass.services.calls,[])
