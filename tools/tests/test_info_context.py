"""Person/Sun contracts over fake HA states; no network or presence simulation."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

import test_extra_panels as old
import test_ha_layout as base

context = importlib.import_module('_atmosfera_test.info_context_domain')
extra = old.extra
codec = old.codec
NOW = datetime(2026, 11, 5, 19, 16, 32, tzinfo=timezone.utc)
WIRE = json.loads((Path(__file__).parent/'fixtures/info_context/wire.json').read_bytes())


def environment(kind='person', raw=None, attrs=None):
    if raw is None: raw = 'home' if kind == 'person' else 'below_horizon'
    if attrs is None: attrs = {} if kind == 'person' else {
        'next_rising': '2026-11-06T05:38:19.357650+00:00',
        'next_setting': '2026-11-06T14:53:55.387535+00:00', 'elevation': -36.43, 'azimuth': 293.83}
    state = base.State(kind+'.test', raw, attrs)
    state.last_updated = NOW; state.last_changed = NOW-timedelta(hours=2)
    hass, _ = base.environment(states=[state]); hass.config.time_zone = 'Europe/Warsaw'
    return hass, state


def observe(hass, state, language='pl'):
    domain = extra.ExtraDomain.from_ha(hass, state)
    with patch.object(context, '_utcnow', return_value=NOW):
        return domain, extra.ExtraObservation.from_ha(hass, state, domain, language)


class ContextModelTests(unittest.TestCase):
    def test_person_semantics_full_zone_translation_and_private_fields(self):
        for raw, phase, label in [('home','home','W domu'),('not_home','away','Poza domem'),('Pracownia_Łódź','zone','Pracownia_Łódź')]:
            hass, state = environment(raw=raw, attrs={'latitude':'private', 'longitude':'private', 'entity_picture':'private', 'source':'private', 'user_id':'private'})
            domain, value = observe(hass, state)
            self.assertEqual((value.fields['phase'], value.fields['state_text']), (phase,label))
            self.assertEqual(value.fields['changed_text'], '2026-11-05T18:16:32+01:00')
            self.assertNotIn('private', json.dumps(extra.extra_metadata(hass,state)))
            self.assertEqual(value.eligible(domain), 0)
            with self.assertRaises(extra.ExtraPanelError): domain.service_action(state.entity_id,'press')
        hass,state=environment()
        with patch.object(base.cards,'_translate_state_for_locale',return_value='Ż'*49):
            self.assertEqual(observe(hass,state)[1].fields['text_status'],'too_long')

    def test_unknown_clears_values_but_preserves_current_observation_time(self):
        for kind in ('person','sun'):
            for raw in ('unknown','unavailable'):
                hass,state=environment(kind,raw);domain,value=observe(hass,state)
                self.assertFalse(value.available);self.assertEqual(value.fields['phase'],'unknown')
                self.assertEqual(value.fields['updated_text'],'2026-11-05T20:16:32+01:00')
                self.assertEqual(value.fields['zone_text'],'')
                self.assertTrue(all(v=='unknown' for k,v in value.fields.items() if k.endswith('_status')))
                self.assertTrue(all(v=='' for k,v in value.fields.items() if k.endswith('_text') and k!='updated_text'))

    def test_date_normalization_dst_midnight_missing_zone_and_future_precision(self):
        zone=ZoneInfo('Europe/Warsaw')
        for source,expected in [('2026-10-25T00:30:00Z','2026-10-25T02:30:00+02:00'),('2026-10-25T01:30:00Z','2026-10-25T02:30:00+01:00'),('2026-12-31T23:30:00Z','2027-01-01T00:30:00+01:00')]:
            self.assertEqual(context.date_text(source,zone),('value',expected))
        for raw in ('2026-11-05T19:16:32', '2026-02-30T00:00:00Z', True, '2026-11-05T19:16:32.1234567Z', '2026-11-05T19:16:32+00:99', '2026-11-05T19:16:32+24:00'):
            self.assertEqual(context.date_text(raw,zone),('invalid',''))
        self.assertFalse(context.valid_date('2026-11-05T19:16:32+00:99'))
        self.assertEqual(context.date_text(NOW,None),('invalid',''))
        self.assertEqual(context.date_text(None,zone),('unknown',''))
        self.assertEqual(context.date_text(NOW,zone,future=True,now=NOW),('stale',''))
        self.assertEqual(context.date_text(NOW+timedelta(microseconds=1),zone,future=True,now=NOW),('value','2026-11-05T20:16:32+01:00'))
        hass,state=environment('sun');hass.config.time_zone='invalid/zone';fields=observe(hass,state)[1].fields
        self.assertEqual((fields['zone_text'],fields['next_rising_status'],fields['elevation_status']),('','invalid','value'))

    def test_sun_independent_missing_stale_and_exact_numeric_fields(self):
        hass,state=environment('sun');domain,value=observe(hass,state)
        self.assertEqual(value.fields['next_rising_text'],'2026-11-06T06:38:19+01:00')
        self.assertEqual(value.fields['elevation_text'],'-36.43')
        before=domain.fingerprint
        state.attributes.update(next_rising=NOW-timedelta(seconds=1),next_setting=None,elevation=True,azimuth=float('nan'))
        _,value=observe(hass,state)
        self.assertEqual([value.fields[k+'_status'] for k in ('next_rising','next_setting','elevation','azimuth')],['stale','unknown','invalid','invalid'])
        self.assertEqual(extra.ExtraDomain.from_ha(hass,state).fingerprint,before)
        for raw,minimum,maximum,expected in [('5e-324',-90,90,('value','5e-324')),('-0.0',-90,90,('value','-0.0')),('90.00000000000000000000001',-90,90,('invalid','')),('0.12345678901234567890123',0,360,('too_long','')),(float('inf'),0,360,('invalid',''))]:
            self.assertEqual(context.angle_text(raw,minimum,maximum),expected)

    def test_exact_numeric_grammar_cross_layer_cases(self):
        template=WIRE['sun-night']
        for raw in ('.5','1.','0.5','1.0','5e-324'):
            self.assertEqual(context.angle_text(raw,-90,90),('value',raw))
            value=template|{'panel_state':template['panel_state']|{'elevation_status':'value','elevation_text':raw}}
            self.assertEqual(codec.decode(codec.encode(value,extra_profiles=('info','info_context')),extra_profiles=('info','info_context')),value)
        for raw in ('36,43',' 0.5','1e','90.000000000000000000001'):
            self.assertEqual(context.angle_text(raw,-90,90),('invalid',''))
            value=template|{'panel_state':template['panel_state']|{'elevation_status':'value','elevation_text':raw}}
            with self.assertRaises(codec.ProtocolError):codec.encode(value,extra_profiles=('info','info_context'))

    def test_explicit_launchers_require_both_profiles_and_keep_passive_placement(self):
        for kind in ('person','sun'):
            hass,state=environment(kind)
            for card_type in ('sensor','entity'):
                card=base.card(slot=13,entity=state.entity_id,type=card_type,action=extra.INFO_ACTION)
                self.assertEqual(base.layout.validate_layout(base.document([card])|{'version':3})['cards'][0]['action'],extra.INFO_ACTION)
                self.assertIsNone(base.cards.resolve_action(hass,card))
                for profiles in ((),('info',),('info_context',),('info','info_context')):
                    with patch.object(context,'_utcnow',return_value=NOW):
                        row=base.cards.presentation_payload(hass,[card],panel_extra_profiles=profiles,press_enabled_supported=True)['cards'][13]
                    self.assertEqual(row.get('control_kind'),'panel' if len(profiles)==2 else None)
                passive=card|{'action':{'kind':'none'}}
                with self.assertRaises(base.layout.LayoutError):base.layout.validate_layout(base.document([passive])|{'version':3})

    def test_frozen_wire_and_closed_cross_field_failures(self):
        for value in WIRE.values():
            encoded=codec.encode(value,extra_profiles=('info','info_context'))
            self.assertEqual(codec.decode(encoded,extra_profiles=('info','info_context')),value)
            self.assertLessEqual(len(encoded.encode()),2048)
            for profiles in ((),('info',),('info_context',)):
                with self.assertRaises(codec.ProtocolError):codec.decode(encoded,extra_profiles=profiles)
        for name in ('person-home-pl','sun-night'):
            value=WIRE[name]
            for invalid in ({'zone_text':''},{'source':'unknown'},{'updated_text':'2026-11-05T19:16:32Z'},{'unexpected':None}):
                with self.assertRaises(codec.ProtocolError):codec.encode(value|{'panel_state':value['panel_state']|invalid},extra_profiles=('info','info_context'))
            with self.assertRaises(codec.ProtocolError):codec.encode(value|{'eligible_actions':1},extra_profiles=('info','info_context'))
        for profiles in ([{'name':'info_context','version':1}],[{'name':'info','version':2},{'name':'info_context','version':1}]):
            self.assertFalse(old.features.valid_profiles(profiles))


class ContextOwnerTests(unittest.IsolatedAsyncioTestCase):
    send=old.ExtraOwnerTests.send;change=old.ExtraOwnerTests.change;results=old.ExtraOwnerTests.results
    asyncTearDown=old.ExtraOwnerTests.asyncTearDown;bind=old.ExtraOwnerTests.bind
    open=old.ExtraOwnerTests.open;command=old.ExtraOwnerTests.command;configure=old.ExtraOwnerTests.configure

    async def asyncSetUp(self):
        await old.ExtraOwnerTests.asyncSetUp(self)
        self.hass,self.state=environment();self.owner.hass=self.hass
        self.card.update(entity_id=self.state.entity_id,type='entity',action=extra.INFO_ACTION)

    async def test_read_permission_observation_renewal_commands_and_prior_bind_preserved(self):
        self.allowed=False
        grant=await self.open();self.assertEqual(grant['panel_caps']['info_type'],'person');self.assertEqual(grant['eligible_actions'],0)
        self.state.state='not_home';self.state.last_updated+=timedelta(seconds=1)
        await self.owner.async_state_changed()
        self.assertEqual(self.owner._selection.domain_state[1].fields['phase'],'away')
        await self.send(self.command());self.assertEqual(self.results()[-1]['reason'],'unsupported')
        self.assertEqual(self.hass.services.calls,[])
        accepted=self.owner.panel_extra_profiles
        with self.assertRaises(codec.ProtocolError):self.owner.accept_extra_features(self.owner.channel,[{'name':'info_context','version':1}])
        self.assertEqual(self.owner.panel_extra_profiles,accepted)


if __name__=='__main__':unittest.main()
