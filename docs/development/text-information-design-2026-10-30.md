# Passive text-helper cards — CTL-017

Status: HA36 installed;473 Python checks (3skip), focused formatter4 checks
and265 editor tests pass. **Device/browser acceptance is in progress.**

Plain `input_text` helpers can be discovered in the existing library and become
passive Information cards. User text is not translated or evaluated. Whitespace
collapses to spaces and the displayed value is bounded to40 codepoints, matching
the preview. Optional exact per-card state descriptions remain available. There
is no text input keyboard or write action on the device.

Only explicit `mode: text` is discoverable. A previously configured helper that
switches to password or an unknown mode shows a localized hidden-text message,
before any custom state mapping. Both the native projection and a cached browser
library entry enforce this. Missing/unknown/unavailable keep normal availability
messages. No HA credential or new device transport is introduced.

HA defines text/password modes and publishes mode as an entity attribute:
[helper documentation](https://www.home-assistant.io/integrations/input_text/),
[installed Core2026.7.1 implementation](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/input_text/__init__.py).
Masking the card and excluding password-mode discovery are Atmosfera policy.

HA owns text and validation. Existing entity subscriptions, finite card pool and
changed-slot snapshots handle updates. There is no new native task, framebuffer
or firmware field. The same change removes irrelevant actuator hints from
Information-card properties.

Acceptance uses one isolated, owned input_text helper: raw/mapped text,
unknown/unavailable, text→password→text, empty password catalogue, passive taps,
off-screen change, real library assignment/Undo, original screenshots, cleanup,
and normal Settings/memory measurements. Existing user helpers are not modified.
