# Stateless tile events — next vertical slice (CTL-031)

Status: HA33/native35 bounded runtime, original-image, browser and cleanup
acceptance passed. Six presses drove six isolated helper transitions, including
two after a saved card move. Layout restored at73; 54FPS/failed0.
[Evidence and remaining gates](validation-2026-10-30-continuation.md).

## Product behavior and ownership

An explicit Action card can emit a press event for Home Assistant automations
without targeting a light or other household entity. It has a stable card ID,
user title/icon and the existing accent palette. Moving it preserves identity.
An empty entity binding is mandatory, so an event cannot also dispatch a hidden
service. Information cards and reserved slots cannot emit events.

Prefer a real HA Event entity per configured event card, with one `press` type,
linked to the existing ESPHome device. This makes the button discoverable in HA
and separates the last-event timestamp from an on/off state. Do not introduce a
new device-automation trigger platform: [current HA guidance](https://contributors.home-assistant.io/core/integrations/events/)
prefers event entities. The installed [Core2026.7.1 Event implementation](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/event/__init__.py)
is the compatibility reference; do not assume future trigger APIs are installed.

The existing bridge remains the report/authentication/revision owner. After its
current slot/card/revision checks, it fires one fixed integration event with
entry ID, device ID, card ID, slot and revision, preserving the caller Context.
No arbitrary event name, payload, template, URL, token or service is accepted.
Event entities receive a private registered callback for their matching card
and publish the standard event timestamp. The public event is informational and
cannot forge an Event entity press. An opaque registration token fences rebinds.
Authorization is single-flight and current binding/client/revision are rechecked
after it completes. Historical presses are deliberately not restored on reload. They never send household services. There is no retry or new
event queue. Existing native press arbitration/debounce remains authoritative.

Only explicit v3 `{kind: event}` on an editable, visible Action card is enabled.
Require negotiated context reports and press availability. Older native paths
must stay passive, with no default-action fallback. The frontend offers an
explicit reviewed conversion, preview/Undo and a clear HA-automation explanation;
preview emits nothing. Import/export preserves the declaration, not event history.

## Bounded lifecycle

At most fourteen event cards can be active in the fixed product layout. HA adds
entities only for configured event cards and reuses their unique IDs across
moves. Hiding/removing/changing a card unregisters and removes its active entity;
the normal registry history and unavailable placeholder are retained for user
configuration recovery. Registry-disabled additions resolve through the Core
add-abort lifecycle; removal waits for addition to finish. The Event entity is
last-press history, so native connection changes do not generate availability
state transitions. Automation state triggers should exclude unknown/unavailable
so rename/removal/reload do not simulate a press. A test
may delete only the exact registry record it created after proving no active
layout/automation references remain. Entity listeners and entry update listeners
must detach on unload; no new poller or timer.

Firmware continues to receive the existing title/subtitle/press-enabled
projection. No native widget, task, session, raw framebuffer or snapshot slot is
added. HA owns policy and dynamic entities; the LVGL task and current changed-slot
snapshot lifecycle own pixels.

## Acceptance before deployment claims

Validate strict v3 shape, visibility/type/empty-binding restrictions, roundtrip,
old-native passive behavior, stale/missing context rejection and exact Context.
Check entity add/move/rename/remove/unload and no synthetic event on restore.
Exercise the actual browser review, preview and Undo without dispatch.

On device, bind one guarded temporary Action card, attach an isolated HA
automation to its event entity, and prove exact taps/events and actual helper
changes. Reject old context and held contacts after layout change; scrolling
must not emit a press. Inspect original screenshots and compare normal Settings
FPS/memory. Restore all original cards, remove only owned QA configuration,
verify source/camera/preferences and record limitations separately.
