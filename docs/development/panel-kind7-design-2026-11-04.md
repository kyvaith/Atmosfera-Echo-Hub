# Timer, Remote and Power panels — candidate89 / HA109

Backend implementation and host checks are complete. This document is not a
firmware, deployment, screenshot or physical-device acceptance. Parent owns
the immutable source capture, build/flash, layout migration and hardware QA.
No Git publication was performed.

## Contract and ownership

The optional `panel` kind7 shares the existing entity-control channel,
ControlSessionOwner, authorization slot, command fence and App6 lifecycle.
Timer, Remote and Power have separate product compositions and SVGs. This
backend adds no framebuffer, native task, polling subscription or independent
command queue. The existing state subscription observes authoritative changes;
the existing lease renewal supplies fresh Timer samples.

Family negotiation is separate from the unchanged capability field shape:
`entity_panel_get_features`, followed by
`entity_panel_bind_features(payload:string)`. Strict512-byte JSON names
`entity_panel_features_v1`, version1, an ordered nonempty subset of timer,
remote,power and the current channel. Bind resets on reconnect/mode change;
unsupported/malformed negotiation disables only Panel. A configured renderer
without successful channel binding is insufficient for admission.

Explicit v3 actions use control:panel and property:timer|remote|power.
Timer optionally retains an integer initial_duration1..86400, preserving
slot14's120-second preset as a local initial draft. Other families cannot carry
this field, service names or data. Legacy service/default/Choice actions retain
their prior behavior until explicit reviewed migration.

Grant/state has the common identity/lease/sequence/title plus panel_type,
panel_caps, panel_state, available, eligible_actions and state_generation.
Variant objects are exact and the total envelope remains2048 UTF-8 bytes.
Caps changes revoke selection; semantic state ABA cancels a held command.
Open, preview and close do not dispatch services. No optimistic source state.

The full coordinated wire contract is preserved with the build evidence at
`C:/aeh-build/device-panels-20261104/panel-kind7-wire.md`.

## Timer

Only existing timer.start/pause/cancel services are used. Start and Resume
without duration preserve Core semantics. A separate set_duration operation
uses an exact integer1..86400 and is an explicit repeatable restart, including
when the previous duration already matches. It receives service_completed only
after the awaited HA callback finishes. That means accepted by HA, not that a
timer completed or that the countdown reached its target.

Start/Resume/Pause/Cancel require a fresh relevant observed phase transition
for state_matches. Repeated active feedback cannot prove a restart. Exceptions
and timeouts remain rejected/not_confirmed and are not retried.

Observations use Core whole-second duration/remaining and an aware UTC
finishes_at. Both sampled_at_utc_s and finishes_at_utc_s have explicit seconds
units. A malformed/missing deadline disables only the countdown facet.
Observations beyond24h remain truthful; they are not clamped into the editor's
24h bound. Implausibly large countdown differences disable the facet.

Native receives the existing HA time component by configured time_id and may
update visible text at most once per second in its existing loop. It must stop
pixel updates during capture/suspension/handoff and respect its existing lease.
Display0 while HA remains active is waiting for HA, never a fabricated finished
event. Sample clock and decreasing active remaining do not advance command
generation. Phase, duration, active deadline and paused remaining do.

## Remote and Power

Remote uses real on/off and existing ACTIVITY4/activity_list/current_activity
validation. The complete catalogue is bounded8x32 UTF-8 bytes without trimming
or truncation. Missing activity support does not hide supported power.
Off ignores a retained previous activity; On with unknown activity disables
only activity selection. Modal row selection is local, Apply sends one exact
remote.turn_on(activity=...) and confirmation requires On plus that activity.
No IR/RF commands, learned-key catalogue or invented keypad are introduced.

Power accepts Switch/input_boolean and only absolute domain turn_on/turn_off.
There is no toggle fallback. Actual switch device_class selects outlet/switch
or a neutral symbol; unknown source is not interpreted as Off. Both families
confirm only authoritative HA state; a mock does not prove a physical load or
IR/RF target responded.

## Scope deliberately left pending

Lock/Action/Info are not advertised or implemented by Panel v1. Slot30's
wideodzwonek currently depends on Camera's Home-idle admission. Opening App6
first would turn its preview into busy/notification_saved; migrating it needs
the separately reviewed single-owner handoff before service dispatch.
Slot15 notifications already close App6 through ui_notification_after_light;
they do not currently present a toast over the active detail panel. Neither
Camera nor notification policy changes in this package. Player/Gallery/Voice
remain untouched.

## Host validation

Focused Panel tests cover strict variants and negotiation, family/capability
admission, exact callbacks, unknown states, repeated restarts, stale gestures,
countdown-versus-semantic generation, authorization loss, metadata ABA,
callback failure/timeout, unsupported-family fallback and legacy results.

Combined focused/shared-owner run:138 tests and2913 subtests passed.
Full HA backend suite:931 passed,2 skipped,4405 subtests,24.46s.
Receipt: `C:/aeh-build/device-panels-20261104/ha109-full-tests.txt`.
These are host/fake-service checks, not hardware acceptance. Next hardware
scope is the existing owned Timer, Remote and Switch fixtures, exact frozen
firmware/HA identities, original screenshots and a batched memory/performance
comparison; live migration must use a fresh layout baseline/revision.
