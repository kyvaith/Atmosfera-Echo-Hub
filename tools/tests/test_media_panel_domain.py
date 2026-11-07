"""Pure unregistered Media candidate: actual source fixtures and hostile values.

No owner, native, firmware, browser or device acceptance is implied.
"""
from copy import deepcopy
from decimal import Decimal
from enum import IntFlag
import importlib
import json
import math
from pathlib import Path
import unittest

import test_ha_layout as base

m = importlib.import_module('_atmosfera_test.media_panel_domain')
FIXTURES = json.loads((Path(__file__).parent/'fixtures/media_panel/actual-media111.json').read_text(encoding='utf8'))


class MediaPanelDomainTests(unittest.TestCase):
    def test_malformed_device_class_is_generic_without_breaking_the_entity_catalogue(self):
        for value in ([], {}, True, 3, None, "custom"):
            hass, state, _ = self.fixture()
            state.attributes["device_class"] = value
            self.assertEqual(m.MediaDomain.from_ha(hass, state).device_type, "generic")
            self.assertEqual(m.media_metadata(hass, state)["media_panel"]["caps"]["device_type"], "generic")

    def fixture(self, suffix='music'):
        name = 'media_player.atmosfera_demo_'+suffix
        row = FIXTURES['states'][name]
        state = base.State(name, row['state'], deepcopy(row['attributes']))
        hass, _ = base.environment(states=[state], services=['media_player.'+s for s in FIXTURES['services']])
        return hass, state, m.MediaDomain.from_ha(hass, state, 'pl')

    def test_actual_music_capabilities_and_exact_volume(self):
        hass, state, domain = self.fixture()
        self.assertEqual(domain.facets, 1+4+8)
        self.assertNotIn('source', dict((x[0],x[1]) for x in domain.choices))
        self.assertEqual(domain.volume(state), m.VolumeObservation('1', '100', 10000))
        self.assertTrue(domain.eligible(state,'pause'))
        self.assertFalse(domain.eligible(state,'play'))
        self.assertEqual(hass.services.calls, [])

    def test_actual_tv_stray_volume_attributes_do_not_grant_controls(self):
        hass, state, domain = self.fixture('tv')
        self.assertEqual(state.attributes['volume_level'],1)
        self.assertFalse(state.attributes['is_volume_muted'])
        self.assertEqual(domain.device_type,'tv')
        self.assertEqual(domain.facets, 2+4)
        self.assertIsNone(domain.volume(state))
        self.assertIsNone(domain.boolean(state,'mute'))
        self.assertEqual(domain.choice(state,'source'),0)
        for operation in ('volume','volume_up','volume_down','mute'):
            self.assertNotIn(operation,domain.operations)
        self.assertEqual(hass.services.calls, [])

    def test_volume_shortest_roundtrip_and_exact_percent(self):
        values=(0,1,-0.0,.425,.12345678901234566,math.nextafter(1,0),math.nextafter(0,1),
                2.2250738585072014e-308,1e-100,1e-6)
        for value in values:
            with self.subTest(value=value):
                observed=m.volume_observation(value)
                self.assertEqual(float(observed.raw),value)
                self.assertEqual(Decimal(observed.percent),Decimal(observed.raw)*100)
                self.assertLessEqual(len(observed.raw.encode()),m.RAW_VOLUME_BYTES)
                self.assertLessEqual(len(observed.percent.encode()),m.PERCENT_BYTES)
                self.assertTrue(0<=observed.rail<=10000)
        self.assertEqual(m.volume_observation(.425).percent,'42.5')
        self.assertNotEqual(m.volume_observation(math.nextafter(1,0)).percent,'100')
        self.assertNotEqual(m.volume_observation(math.nextafter(0,1)).percent,'0')

    def test_volume_rejects_malformed_or_outside_values(self):
        for value in (None,True,False,'0.5',-.01,1.01,math.nan,math.inf,-math.inf,10**1000,[],{}):
            with self.subTest(value=type(value).__name__):
                self.assertIsNone(m.volume_observation(value))

    def test_source_value_and_ui_step_are_separate(self):
        hass,state,domain=self.fixture()
        state.attributes['volume_level']=.425
        before=deepcopy(state.attributes)
        view=domain.view(state,'volume',1)
        self.assertEqual((view['observed_raw'],view['percent_text'],view['ui_step_percent']),('0.425','42.5',1))
        self.assertEqual(domain.service(hass,state,'volume','volume',43),('media_player','volume_set',{'volume_level':.43}))
        self.assertFalse(domain.matches(state,'volume','volume',43))
        self.assertEqual(state.attributes,before)
        self.assertEqual(hass.services.calls,[])
        state.attributes['volume_level']=.43
        self.assertTrue(domain.matches(state,'volume','volume',43))

    def test_volume_target_rejects_bool_fraction_extra_or_unchanged(self):
        hass,state,domain=self.fixture()
        for value in (None,True,False,'43',43.5,-1,101,100):
            with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'volume','volume',value)
        with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'main','volume',43)

    def test_exact_observations_change_command_key_not_track_metadata(self):
        _,state,domain=self.fixture()
        original=domain.command_state(state)
        state.attributes.update(media_title='Next track',media_artist='New artist',media_position=22)
        self.assertEqual(domain.command_state(state),original)
        state.attributes['volume_level']=math.nextafter(1,0)
        self.assertNotEqual(domain.command_state(state),original)
        state.attributes['volume_level']=1
        self.assertEqual(domain.command_state(state),original)
        # An owner must increment generation at each event, including ABA.
        # This pure-domain test does not claim that owner behavior is installed.

    def test_unknown_and_unavailable_do_not_expose_retained_attrs(self):
        _,state,domain=self.fixture()
        for phase in ('unknown','unavailable','vendorphase'):
            state.state=phase
            view=domain.main(state)
            self.assertEqual(view['eligible'],0)
            self.assertIsNone(view['volume_raw'])
            self.assertIsNone(view['muted'])
            self.assertEqual(view['media_title'],'')
            self.assertEqual(view['source'],'unavailable' if phase=='unavailable' else 'unknown')

    def test_off_standby_distinct_with_only_turn_on_eligible(self):
        _,state,domain=self.fixture()
        for phase in ('off','standby'):
            state.state=phase
            view=domain.main(state)
            self.assertEqual(view['phase'],phase)
            self.assertEqual(view['source'],'known')
            self.assertEqual(view['eligible'],m.OP_BITS['turn_on'])
            self.assertIsNone(view['volume_raw'])

    def test_play_pause_are_explicit_and_current(self):
        hass,state,domain=self.fixture()
        self.assertEqual(domain.service(hass,state,'main','pause'),('media_player','media_pause',{}))
        with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'main','play')
        state.state='paused'
        self.assertEqual(domain.service(hass,state,'main','play'),('media_player','media_play',{}))
        with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'main','pause')
        with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'main','media_play_pause')

    def test_absolute_boolean_targets_are_not_toggles(self):
        hass,state,domain=self.fixture()
        for operation,field,service in (('mute','is_volume_muted','volume_mute'),('shuffle','shuffle','shuffle_set')):
            self.assertEqual(domain.service(hass,state,'main',operation,True),('media_player',service,{field:True}))
            self.assertFalse(domain.matches(state,'main',operation,True))
            for target in (False,1,0,'true',None):
                with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'main',operation,target)
            state.attributes[field]=True
            self.assertTrue(domain.matches(state,'main',operation,True))
            self.assertEqual(domain.service(hass,state,'main',operation,False)[2],{field:False})

    def test_invalid_boolean_never_becomes_false(self):
        hass,state,domain=self.fixture()
        for value in (None,0,1,'false',[],{}):
            state.attributes['is_volume_muted']=value
            self.assertIsNone(domain.boolean(state,'mute'))
            with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'main','mute',True)

    def test_service_and_capability_loss_are_distinct_and_revalidated(self):
        hass,state,domain=self.fixture()
        hass.services.names.remove('media_player.media_pause')
        self.assertNotEqual(m.MediaDomain.from_ha(hass,state),domain)
        with self.assertRaises(ValueError):domain.service(hass,state,'main','pause')
        hass.services.names.add('media_player.media_pause')
        state.attributes['supported_features'] &= ~1
        self.assertNotEqual(m.MediaDomain.from_ha(hass,state),domain)
        with self.assertRaises(ValueError):domain.service(hass,state,'main','pause')

    def test_strict_features_intflag_supported_bool_and_huge_rejected(self):
        class Features(IntFlag): PLAY=16384; VOLUME=4
        hass,state,_=self.fixture()
        state.attributes['supported_features']=Features.PLAY|Features.VOLUME
        domain=m.MediaDomain.from_ha(hass,state)
        self.assertIn('play',domain.operations)
        self.assertIn('volume',domain.operations)
        for value in (True,False,-1,2**53,'16384',None):
            state.attributes['supported_features']=value
            domain=m.MediaDomain.from_ha(hass,state)
            self.assertEqual(domain.operations,())
            self.assertEqual(domain.facets,0)

    def test_step_only_retains_steps_without_a_slider(self):
        hass,state,_=self.fixture()
        state.attributes['supported_features']=1024
        domain=m.MediaDomain.from_ha(hass,state)
        self.assertEqual(domain.operations,('volume_up','volume_down'))
        self.assertEqual(domain.facets,0)
        self.assertFalse(domain.eligible(state,'volume_up'))
        self.assertTrue(domain.eligible(state,'volume_down'))
        state.attributes['volume_level']=.425
        self.assertEqual(domain.service(hass,state,'main','volume_up')[1],'volume_up')

    def test_choices_canonical_and_one_active_catalogue(self):
        hass,state,domain=self.fixture('tv')
        for facet,target,key,value in (('source',1,'source','youtube'),('sound_mode',1,'sound_mode','Movie')):
            view=domain.view(state,facet,2)
            self.assertEqual(set(view),{'facet','view_seq','source','options','index','editable'})
            self.assertEqual(view['index'],0)
            self.assertEqual(domain.service(hass,state,facet,'choice',target)[2],{key:value})
        self.assertNotIn('options',domain.view(state,'main',0))

    def test_choices_reject_unknown_current_and_bad_target(self):
        hass,state,domain=self.fixture('tv')
        for target in (True,None,-1,2,0):
            with self.assertRaises(ValueError):domain.service(hass,state,'source','choice',target)
        state.attributes['source']='other'
        self.assertIsNone(domain.view(state,'source',2)['index'])
        with self.assertRaises(m.MediaPanelError):domain.service(hass,state,'source','choice',1)

    def test_catalogue_changes_are_domain_changes_and_labels_are_complete(self):
        hass,state,domain=self.fixture('tv')
        for options in (['x']*2,['x'*33],[],['x'+str(i) for i in range(9)],['x','unavailable']):
            state.attributes['source_list']=options
            changed=m.MediaDomain.from_ha(hass,state)
            self.assertNotEqual(changed,domain)
            self.assertFalse(changed.allowed_facet('source'))
        state.attributes['source_list']=['youtube','dvd']
        self.assertNotEqual(m.MediaDomain.from_ha(hass,state),domain)

    def test_descriptive_excerpts_explicit_and_scalars_never_clipped(self):
        _,state,domain=self.fixture()
        for text in ('ą'*150,'\\'*150,'"'*150):
            state.attributes['media_title']=text
            view=domain.main(state)
            self.assertEqual(view['title_status'],'excerpt')
            self.assertTrue(view['media_title'].endswith('…'))
            self.assertLessEqual(len(view['media_title'].encode()),128)
        state.attributes['media_title']='Complete short title'
        self.assertEqual(domain.main(state)['title_status'],'value')
        for value in ('bad\x00title','bad\ud800',True):
            state.attributes['media_title']=value
            self.assertEqual(domain.main(state)['title_status'],'invalid')
            self.assertEqual(domain.main(state)['media_title'],'')

    def test_stop_feedback_accepts_actual_demo_off_not_fabricated_idle(self):
        hass,state,domain=self.fixture()
        self.assertEqual(domain.service(hass,state,'main','stop')[1],'media_stop')
        self.assertFalse(domain.matches(state,'main','stop'))
        state.state='off'
        self.assertTrue(domain.matches(state,'main','stop'))
        state.state='paused'
        self.assertFalse(domain.matches(state,'main','stop'))
        self.assertFalse(domain.matches(state,'main','next'))
        self.assertFalse(domain.matches(state,'main','volume_up'))

    def test_no_services_on_domain_observations_navigation_or_resolution(self):
        hass,state,domain=self.fixture()
        original=deepcopy(state.__dict__)
        domain.main(state)
        for index,facet in enumerate(('main','volume','sound_mode','repeat')):
            domain.view(state,facet,index)
        domain.service(hass,state,'main','pause')
        self.assertEqual(state.__dict__,original)
        self.assertEqual(hass.services.calls,[])


if __name__=='__main__':unittest.main()
