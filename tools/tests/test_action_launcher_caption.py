"""Home projection regression: a momentary Action launcher is not a timestamp."""
from copy import deepcopy
import unittest

import test_action_panels as action_tests
import test_ha_layout as base


class ActionLauncherCaptionTests(unittest.TestCase):
    def render(self, subtype, value, language='pl', *, action=None, profiles=('action',), missing=False, labels=None):
        hass, state, saved = action_tests.environment(subtype, value)
        card = dict(id='test-caption', slot=15, type='entity', entity_id=state.entity_id,
                    title='Fixture', icon='action', palette='primary', visible=True,
                    action=deepcopy(saved if action is None else action))
        if labels is not None: card['state_labels'] = labels
        if missing: hass.states.items.pop(state.entity_id)
        rows = base.cards.presentation_payload(hass, [card], language=language,
            panel_extra_profiles=profiles, press_enabled_supported=True)['cards']
        self.assertEqual(hass.services.calls, [])
        return next(row for row in rows if row['slot'] == 15), hass, state, card

    def test_timestamp_and_first_use_are_open_in_both_locales(self):
        for subtype in ('button', 'input_button', 'scene'):
            for value in ('unknown', '2026-11-05T19:01:07.748340+00:00'):
                for language, expected in (('pl', 'Otwórz'), ('en', 'Open')):
                    with self.subTest(subtype=subtype, value=value, language=language):
                        row, *_ = self.render(subtype, value, language)
                        self.assertEqual(row['subtitle'], expected)
                        self.assertEqual(row.get('control_kind'), 'panel')

    def test_unavailable_and_missing_keep_existing_availability_captions(self):
        for subtype in ('button', 'input_button', 'scene'):
            row, *_ = self.render(subtype, 'unavailable')
            self.assertEqual(row['subtitle'], base.cards.state_label('unavailable', 'pl'))
            row, *_ = self.render(subtype, 'unknown', missing=True)
            self.assertEqual(row['subtitle'], 'Urządzenie bez obsługi')
            self.assertFalse(row['press_enabled'])

    def test_explicit_mapping_and_legacy_action_precedence_are_unchanged(self):
        stamp = '2026-11-05T19:01:07.748340+00:00'
        # Custom labels remain restricted to supported sensor cards.
        row, *_ = self.render('button', stamp, labels={stamp: 'Moja etykieta'})
        self.assertEqual(row['subtitle'], 'Otwórz')
        state = base.State('sensor.test', 'ready')
        hass, _ = base.environment(states=[state])
        card = base.card(entity=state.entity_id, type='sensor', action={'kind': 'none'})
        card['state_labels'] = {'ready': 'Moja etykieta'}
        self.assertEqual(base.cards._card_subtitle(hass, card, state, 'pl'), 'Moja etykieta')
        row, *_ = self.render('button', stamp, action={'kind': 'default'})
        self.assertEqual(row['subtitle'], 'Naciśnij')
        row, *_ = self.render('button', stamp, action={'kind': 'service', 'service': 'button.press', 'data': {}})
        self.assertEqual(row['subtitle'], 'Naciśnij')

    def test_absent_profile_still_disables_launcher(self):
        row, *_ = self.render('button', 'unknown', profiles=())
        self.assertEqual(row['subtitle'], 'Urządzenie bez obsługi')
        self.assertFalse(row['press_enabled'])
        self.assertNotIn('control_kind', row)

    def test_script_and_automation_keep_observed_state_caption(self):
        for subtype in ('script', 'automation'):
            for value in ('off', 'on', 'unknown', 'unavailable'):
                row, hass, state, card = self.render(subtype, value)
                self.assertEqual(row['subtitle'], base.cards._state_subtitle(hass, state, 'pl'))


if __name__ == '__main__': unittest.main()
