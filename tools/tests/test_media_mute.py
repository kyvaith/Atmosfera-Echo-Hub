"""Explicit mute is a boolean state transition, independent of playback."""
from enum import IntFlag
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import test_ha_layout as base


def card(muted=True):
    return base.card(entity='media_player.qa',action={'kind':'service','service':'media_player.volume_mute','data':{'is_volume_muted':muted}})


class MediaMuteTests(unittest.TestCase):
    def setUp(self):
        self.state=base.State('media_player.qa','playing',{'supported_features':8,'is_volume_muted':False,'volume_level':.42,'media_title':'Track QA'})
        self.hass,_=base.environment(states=[self.state],services=['media_player.volume_mute'])

    def test_exact_boolean_target_and_observed_feedback_do_not_predict_pause_or_volume(self):
        for power in ('on','idle','playing','paused','buffering'):
            self.state.state=power
            for current in (True,False):
                self.state.attributes['is_volume_muted']=current
                for target in (True,False):
                    resolved=base.cards.resolve_action(self.hass,card(target))
                    self.assertEqual(resolved is not None,current!=target)
                    if resolved:self.assertEqual((resolved.domain,resolved.service,resolved.data),('media_player','volume_mute',{'entity_id':'media_player.qa','is_volume_muted':target}))
                    self.assertEqual(self.state.state,power);self.assertEqual(self.state.attributes['is_volume_muted'],current)
                    self.assertEqual(self.state.attributes['volume_level'],.42);self.assertEqual(self.state.attributes['media_title'],'Track QA')
        self.assertEqual(self.hass.services.calls,[])

    def test_missing_invalid_feature_or_boolean_and_unpowered_states_are_inert(self):
        for value in (None,0,1,'true','false',[],{}):
            self.state.attributes['is_volume_muted']=value
            self.assertIsNone(base.cards.resolve_action(self.hass,card()))
            self.assertEqual(base.cards._media_mute_metadata(self.hass,self.state),{})
        self.state.attributes['is_volume_muted']=False
        for features in (0,1,True,-1,'8',2**53+8):
            self.state.attributes['supported_features']=features
            self.assertIsNone(base.cards.resolve_action(self.hass,card()))
        self.state.attributes['supported_features']=8
        for state in ('off','standby','unknown','unavailable','error'):
            self.state.state=state;self.assertIsNone(base.cards.resolve_action(self.hass,card()))
            self.assertNotIn('media_player.volume_mute',{v['service']for v in base.cards.entity_actions(self.hass,self.state)})
        self.state.state='playing';self.state.attributes.pop('is_volume_muted')
        self.assertIsNone(base.cards.resolve_action(self.hass,card()))

    def test_true_core_intflag_service_and_explicit_field_contract(self):
        class Features(IntFlag):VOLUME_MUTE=8
        self.state.attributes['supported_features']=Features.VOLUME_MUTE
        self.assertEqual(base.cards.entity_actions(self.hass,self.state),[{'service':'media_player.volume_mute','fields':{'is_volume_muted':{'type':'boolean','required':True}}}])
        self.assertTrue(base.layout.device_profile()['schema_media_mute'])
        for data in ({},{'is_volume_muted':0},{'is_volume_muted':'true'},{'is_volume_muted':True,'entity_id':'media_player.other'},{'mute':True}):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action({'kind':'service','service':'media_player.volume_mute','data':data},'media_player.qa')
        self.hass.services.names.clear();self.assertIsNone(base.cards.resolve_action(self.hass,card()))

    def test_negotiated_press_tracks_mute_only_and_legacy_wire_has_no_new_field(self):
        self.assertTrue(base.cards.ordinary_action_availability(card()))
        for current,allowed in ((False,True),(True,False),(False,True)):
            self.state.attributes['is_volume_muted']=current
            rendered=base.cards.presentation_payload(self.hass,[card()],press_enabled_supported=True)['cards'][2]
            self.assertIs(rendered['press_enabled'],allowed);self.assertNotIn('control_kind',rendered)
        self.assertNotIn('press_enabled',base.cards.presentation_payload(self.hass,[card()],press_enabled_supported=False)['cards'][2])
        for changed in ({'type':'sensor'},{'visible':False},{'action':{'kind':'none'}}):
            self.assertIsNone(base.cards.resolve_action(self.hass,card()|changed))

    def test_existing_play_pause_default_and_media_title_are_unchanged(self):
        self.state.attributes['supported_features']=9;self.hass.services.names.add('media_player.media_play_pause')
        ordinary=base.card(entity='media_player.qa')
        self.assertEqual(base.cards.resolve_action(self.hass,ordinary).service,'media_play_pause')
        self.assertFalse(base.cards.ordinary_action_availability(ordinary))
        self.assertEqual(base.cards._card_subtitle(self.hass,ordinary,self.state,'en'),'Track QA')

    def test_captions_follow_real_mute_not_target_and_use_ha_attribute_translations(self):
        self.assertEqual(base.cards._card_subtitle(self.hass,card(),self.state,'pl'),'Dźwięk wł.')
        self.state.attributes['is_volume_muted']=True
        self.assertEqual(base.cards._card_subtitle(self.hass,card(False),self.state,'en'),'Muted')
        self.hass.entity_registry.entries[self.state.entity_id]=NS(platform='demo',translation_key='unit')
        labels={'component.demo.entity.media_player.unit.state_attributes.is_volume_muted.state.true':'HA wyciszono'}
        with patch.object(base.cards,'async_get_cached_translations',side_effect=lambda _h,_l,category:labels if category=='entity' else {}):
            self.assertEqual(base.cards._media_mute_metadata(self.hass,self.state)['media_mute']['text']['pl'],'Wyciszenie: HA wyciszono')
        self.state.state='off'
        self.assertEqual(base.cards._card_subtitle(self.hass,card(),self.state,'en'),'Off')

    def test_core_boolean_translations_have_context_instead_of_bare_yes_no(self):
        labels={'component.media_player.entity_component._.state_attributes.is_volume_muted.state.false':'nie'}
        with patch.object(base.cards,'async_get_cached_translations',side_effect=lambda _h,_l,category:labels if category=='entity_component' else {}):
            self.assertEqual(base.cards._media_mute_caption(self.hass,self.state,'pl'),'Wyciszenie: nie')
