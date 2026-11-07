"""Fixed media volume intent is independent of a rounded observation or vendor step."""
from copy import deepcopy
from enum import IntFlag
import math
import unittest
import test_ha_layout as base


def card(value=.5):
    return base.card(entity='media_player.qa', action={
        'kind':'service', 'service':'media_player.volume_set', 'data':{'volume_level':value}})


class MediaVolumeTargetTests(unittest.TestCase):
    def setUp(self):
        self.state=base.State('media_player.qa','playing',{
            'supported_features':4,'volume_level':.425,'media_title':'Track QA',
            'source':'Radio','is_volume_muted':False,'shuffle':False,'repeat':'off'})
        self.hass,_=base.environment(states=[self.state],services=['media_player.volume_set'])

    def test_exact_target_is_not_a_relative_step_and_does_not_predict_state(self):
        before=deepcopy(self.state.attributes)
        for power in ('on','idle','playing','paused','buffering'):
            self.state.state=power
            for target in (0,.001,.4725,.9999999,1):
                action=base.cards.resolve_action(self.hass,card(target))
                self.assertEqual((action.domain,action.service,action.data),
                    ('media_player','volume_set',{'entity_id':'media_player.qa','volume_level':target}))
                self.assertEqual(self.state.attributes,before)
        self.assertEqual(self.hass.services.calls,[])

    def test_core_set_flag_required_step_only_and_invalid_sources_are_inert(self):
        class Features(IntFlag): SET=4; STEP=1024
        for feature,allowed in ((Features.SET,True),(Features.STEP,False),
                (Features.SET|Features.STEP,True),(True,False),(-1,False),(2**53+4,False)):
            self.state.attributes['supported_features']=feature
            self.assertEqual(base.cards.resolve_action(self.hass,card()) is not None,allowed)
        self.state.attributes['supported_features']=4
        for value in (None,'0.425',True,False,-.1,1.1,math.nan,math.inf,10**1000):
            self.state.attributes['volume_level']=value
            self.assertIsNone(base.cards.resolve_action(self.hass,card()))
            self.assertEqual(base.cards._media_volume_target_metadata(self.hass,self.state),{})
        self.state.attributes['volume_level']=.425
        for power in ('off','standby','unknown','unavailable'):
            self.state.state=power
            self.assertIsNone(base.cards.resolve_action(self.hass,card()))
        self.state.state='playing';self.state.attributes['supported_features']=1024
        self.assertEqual(base.cards._card_subtitle(self.hass,card(),self.state,'en'),'Unknown')

    def test_typed_target_rejects_missing_extra_wrong_domain_and_invalid_values(self):
        self.assertTrue(base.layout.device_profile()['schema_media_volume_target'])
        for value in (None,'0.5',True,False,-.0001,1.0001,math.nan,math.inf,10**1000):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(card(value)['action'],self.state.entity_id)
        for data in ({},{'volume_level':.5,'entity_id':'media_player.other'},
                     {'volume_level':.5,'is_volume_muted':False}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(card()['action']|{'data':data},self.state.entity_id)
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_action(card()['action'],'number.other')

    def test_matching_target_disables_tap_without_losing_configuration(self):
        for target in (0,.425,1):
            self.state.attributes['volume_level']=target
            self.assertIsNone(base.cards.resolve_action(self.hass,card(target)))
            self.assertFalse(base.cards.presentation_payload(self.hass,[card(target)],
                press_enabled_supported=True)['cards'][2]['press_enabled'])
            self.assertEqual(base.cards.entity_actions(self.hass,self.state)[0]['service'],'media_player.volume_set')
        self.assertTrue(base.cards.ordinary_action_availability(card()))

    def test_caption_and_metadata_show_observation_not_target_and_keep_other_actions(self):
        meta=base.cards._media_volume_target_metadata(self.hass,self.state)['media_volume_target']
        self.assertEqual(meta['value'],.425)
        self.assertEqual(base.cards._card_subtitle(self.hass,card(.8),self.state,'pl'),'Głośn.: 42,5 %')
        self.assertEqual(base.cards._card_subtitle(self.hass,card(.8),self.state,'en'),'Volume: 42.5 %')
        self.assertEqual(meta['text']['pl'],'Głośn.: 42,5 %')
        self.assertEqual(base.cards._media_volume_metadata(self.hass,self.state),{})
        self.hass.services.names.remove('media_player.volume_set')
        self.assertIsNone(base.cards.resolve_action(self.hass,card()))
        self.assertEqual(base.cards._media_volume_target_metadata(self.hass,self.state),{})

