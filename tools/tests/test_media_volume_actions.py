"""Relative media actions keep Core's step and never derive an absolute grid."""
from enum import IntFlag
from importlib import import_module
import math
import unittest
import test_ha_layout as base


def card(operation='volume_up'):
    return base.card(entity='media_player.qa',action={'kind':'service','service':'media_player.'+operation,'data':{}})


class MediaVolumeActionTests(unittest.TestCase):
    def setUp(self):
        self.state=base.State('media_player.qa','playing',{'supported_features':4,'volume_level':.42,'is_volume_muted':False,'repeat':'off','shuffle':False,'media_title':'Track QA'})
        self.hass,_=base.environment(states=[self.state],services=['media_player.volume_up','media_player.volume_down'])

    def test_relative_services_have_only_entity_id_and_do_not_predict_any_media_state(self):
        before=self.state.attributes.copy()
        for power in ('on','idle','playing','paused','buffering'):
            self.state.state=power
            for operation in ('volume_up','volume_down'):
                action=base.cards.resolve_action(self.hass,card(operation))
                self.assertEqual((action.domain,action.service,action.data),('media_player',operation,{'entity_id':'media_player.qa'}))
                self.assertEqual(self.state.attributes,before);self.assertEqual(self.state.state,power)
        self.assertEqual(self.hass.services.calls,[])

    def test_endpoints_disable_only_runtime_direction_and_remain_configurable(self):
        for value,up,down in ((0,True,False),(.0000001,True,True),(.420000007,True,True),(.425,True,True),(.9999999,True,True),(1,False,True)):
            self.state.attributes['volume_level']=value
            self.assertEqual(base.cards.resolve_action(self.hass,card())is not None,up)
            self.assertEqual(base.cards.resolve_action(self.hass,card('volume_down'))is not None,down)
            self.assertEqual({v['service']for v in base.cards.entity_actions(self.hass,self.state)},{'media_player.volume_up','media_player.volume_down'})
            self.assertEqual(base.cards._media_volume_metadata(self.hass,self.state)['media_volume']['value'],value)

    def test_malformed_or_unknown_source_and_capabilities_are_inert(self):
        for value in (None,True,False,'0.5',-1,1.1,math.nan,math.inf,-math.inf,10**1000,[],{}):
            self.state.attributes['volume_level']=value
            self.assertIsNone(base.cards.resolve_action(self.hass,card()))
            self.assertEqual(base.cards._media_volume_metadata(self.hass,self.state),{})
        self.state.attributes['volume_level']=.42
        for flags in (0,True,-1,'4',2**53+4):
            self.state.attributes['supported_features']=flags;self.assertIsNone(base.cards.resolve_action(self.hass,card()))
        self.state.attributes['supported_features']=4
        for state in ('off','standby','unknown','unavailable'):
            self.state.state=state;self.assertIsNone(base.cards.resolve_action(self.hass,card()))

    def test_core_intflags_set_or_step_and_strict_empty_service_data(self):
        class Features(IntFlag):VOLUME_SET=4;VOLUME_STEP=1024
        self.assertTrue(base.layout.device_profile()['schema_media_volume_actions'])
        for flags in (Features.VOLUME_SET,Features.VOLUME_STEP,Features.VOLUME_SET|Features.VOLUME_STEP):
            self.state.attributes['supported_features']=flags
            self.assertIsNotNone(base.cards.resolve_action(self.hass,card()))
        for data in ({'volume_level':.7},{'direction':1},{'entity_id':'media_player.other'}):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action({'kind':'service','service':'media_player.volume_up','data':data},self.state.entity_id)
        self.hass.services.names.remove('media_player.volume_up');self.assertIsNone(base.cards.resolve_action(self.hass,card()))
        self.assertEqual(base.cards._media_volume_operations(self.hass,self.state),('volume_down',))

    def test_caption_is_observed_percent_with_compact_bounds_and_no_false_endpoint(self):
        metrics=import_module('_atmosfera_test.caption_width')
        for value in (0,.0000001,.420000007,.425,.9999999,1):
            self.state.attributes['volume_level']=value
            for language in ('pl','en'):
                text=base.cards._media_volume_caption(self.hass,self.state,language)
                self.assertLessEqual(metrics.caption_width(text),136)
                self.assertEqual(base.cards._media_volume_metadata(self.hass,self.state)['media_volume']['text'][language],text)
        self.state.attributes['volume_level']=.425
        self.assertEqual(base.cards._card_subtitle(self.hass,card(),self.state,'pl'),'Głośn.: 42,5 %')
        self.assertEqual(base.cards._card_subtitle(self.hass,card('volume_down'),self.state,'en'),'Volume: 42.5 %')

    def test_press_admission_and_default_play_pause_media_title_unchanged(self):
        self.assertTrue(base.cards.ordinary_action_availability(card()))
        self.state.attributes['volume_level']=1
        self.assertFalse(base.cards.presentation_payload(self.hass,[card()],press_enabled_supported=True)['cards'][2]['press_enabled'])
        self.assertNotIn('press_enabled',base.cards.presentation_payload(self.hass,[card()],press_enabled_supported=False)['cards'][2])
        self.state.attributes.update(volume_level=.42,supported_features=5);self.hass.services.names.add('media_player.media_play_pause')
        ordinary=base.card(entity=self.state.entity_id)
        self.assertEqual(base.cards.resolve_action(self.hass,ordinary).service,'media_play_pause')
        self.assertFalse(base.cards.ordinary_action_availability(ordinary))
        self.assertEqual(base.cards._card_subtitle(self.hass,ordinary,self.state,'en'),'Track QA')
        for update in ({'visible':False},{'type':'sensor'},{'action':{'kind':'none'}}):self.assertIsNone(base.cards.resolve_action(self.hass,card()|update))
