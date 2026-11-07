"""Explicit Stop uses Core STOP4096 and never predicts the observed state."""
from enum import IntFlag
from importlib import import_module
import unittest
from unittest.mock import patch
import test_ha_layout as base


def card():
    return base.card(entity='media_player.qa',action={'kind':'service','service':'media_player.media_stop','data':{}})


class MediaStopTests(unittest.TestCase):
    def setUp(self):
        self.state=base.State('media_player.qa','playing',{'supported_features':4096,'volume_level':.42,'source':'Radio','repeat':'off','shuffle':False,'is_volume_muted':False,'media_title':'Track QA'})
        self.hass,_=base.environment(states=[self.state],services=['media_player.media_stop'])

    def test_only_active_playback_states_dispatch_empty_data_without_predicting_feedback(self):
        before=self.state.attributes.copy()
        for state in ('playing','paused','buffering'):
            self.state.state=state;action=base.cards.resolve_action(self.hass,card())
            self.assertEqual((action.domain,action.service,action.data),('media_player','media_stop',{'entity_id':'media_player.qa'}))
            self.assertEqual(self.state.state,state);self.assertEqual(self.state.attributes,before)
        self.assertEqual(self.hass.services.calls,[])

    def test_known_inactive_states_remain_configurable_but_native_press_is_disabled(self):
        for state in ('on','idle','off','standby'):
            self.state.state=state
            self.assertIsNone(base.cards.resolve_action(self.hass,card()))
            self.assertEqual(base.cards.entity_actions(self.hass,self.state),[{'service':'media_player.media_stop','fields':{}}])
            self.assertIs(base.cards._media_stop_metadata(self.hass,self.state)['media_stop']['eligible'],False)
            self.assertIs(base.cards.presentation_payload(self.hass,[card()],press_enabled_supported=True)['cards'][2]['press_enabled'],False)

    def test_unknown_or_malformed_capabilities_and_missing_service_are_inert(self):
        for flags in (0,True,False,'4096',4096.0,-1,2**53+4096,None):
            self.state.attributes['supported_features']=flags
            self.assertIsNone(base.cards.resolve_action(self.hass,card()))
            self.assertEqual(base.cards._media_stop_metadata(self.hass,self.state),{})
            self.assertNotIn('media_player.media_stop',{a['service']for a in base.cards.entity_actions(self.hass,self.state)})
        self.state.attributes['supported_features']=4096
        for state in ('unknown','unavailable','unrecognized'):
            self.state.state=state;self.assertIsNone(base.cards.resolve_action(self.hass,card()))
            self.assertEqual(base.cards._media_stop_metadata(self.hass,self.state),{})
        self.state.state='playing';self.hass.services.names.clear()
        self.assertIsNone(base.cards.resolve_action(self.hass,card()));self.assertEqual(base.cards._media_stop_metadata(self.hass,self.state),{})

    def test_intflag_schema_and_strict_empty_data_contract(self):
        class Features(IntFlag):STOP=4096
        self.state.attributes['supported_features']=Features.STOP
        self.assertIsNotNone(base.cards.resolve_action(self.hass,card()))
        self.assertTrue(base.layout.device_profile()['schema_media_stop'])
        self.assertEqual(base.layout.validate_action(card()['action'],self.state.entity_id),card()['action'])
        for data in ({'entity_id':'media_player.other'},{'stop':True},{'state':'idle'}):
            with self.assertRaises(base.layout.LayoutError):base.layout.validate_action(card()['action']|{'data':data},self.state.entity_id)

    def test_caption_uses_ha_playback_state_and_compact_width_not_the_target_or_track(self):
        metrics=import_module('_atmosfera_test.caption_width')
        labels={'component.media_player.entity_component._.state.playing':'HA Playing'}
        with patch.object(base.cards,'async_get_cached_translations',return_value=labels), patch.object(base.cards,'async_translate_state',return_value='HA Playing'):
            self.assertEqual(base.cards._card_subtitle(self.hass,card(),self.state,'en'),'State: HA Playing')
            self.assertEqual(base.cards._card_subtitle(self.hass,card(),self.state,'pl'),'Stan: HA Playing')
        for state in ('playing','paused','buffering','on','idle','off','standby'):
            self.state.state=state
            for language in ('pl','en'):
                text=base.cards._media_stop_caption(self.hass,self.state,language)
                self.assertLessEqual(metrics.caption_width(text),136)
                self.assertEqual(base.cards._media_stop_metadata(self.hass,self.state)['media_stop']['text'][language],text)
                self.assertNotIn('Track QA',text)

    def test_ordinary_admission_and_default_play_pause_are_independent(self):
        self.assertTrue(base.cards.ordinary_action_availability(card()))
        self.assertTrue(base.cards.presentation_payload(self.hass,[card()],press_enabled_supported=True)['cards'][2]['press_enabled'])
        self.assertNotIn('press_enabled',base.cards.presentation_payload(self.hass,[card()],press_enabled_supported=False)['cards'][2])
        self.state.attributes['supported_features']=4097;self.hass.services.names.add('media_player.media_play_pause')
        ordinary=base.card(entity=self.state.entity_id)
        self.assertEqual(base.cards.resolve_action(self.hass,ordinary).service,'media_play_pause')
        self.assertFalse(base.cards.ordinary_action_availability(ordinary))
        self.assertEqual(base.cards._card_subtitle(self.hass,ordinary,self.state,'en'),'Track QA')

    def test_compact_play_pause_renders_observed_state_without_the_track_title(self):
        play_pause = base.card(entity=self.state.entity_id, action={
            "kind": "service", "service": "media_player.media_play_pause", "data": {},
        }) | {"slot": 24}
        for state, expected in (("playing", "Odtwarzanie"), ("paused", "Pauza"), ("unavailable", "Niedostępny")):
            self.state.state = state
            rows = base.cards.presentation_payload(self.hass, [play_pause], language="pl", slot_count=32)["cards"]
            self.assertEqual(rows[24]["subtitle"], expected)

    def test_hidden_information_and_actionless_cards_never_issue_stop(self):
        for update in ({'visible':False},{'type':'sensor'},{'action':{'kind':'none'}}):
            self.assertIsNone(base.cards.resolve_action(self.hass,card()|update))
