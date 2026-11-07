# Cover panel v1 contract — candidate87 / HA107

Approved for coordinated implementation after native86 source capture.
The HA backend and focused host tests are implemented. Firmware compilation,
deployment, layout migration and device acceptance are separate checkpoints;
this document does not claim hardware acceptance.

## Decision and ownership

Keep `control_kind: "cover"` (kind3), the existing Cover state machine,
ControlSessionOwner, App6, lease, authorization, state sequence and one service
fence. Add an optional channel-bound `cover_panel_version: 1` extension, rather
than another kind or another owner. Legacy Cover v1 remains byte-for-byte exact:
same three outer capabilities, grant/state fields and open/stop/close commands.

Both native and UI agents agree with this approach. No new task, queue, timer,
full-screen image, or framebuffer. Product layout remains the existing explicit
`{"kind":"control","control":"cover"}` action; a negotiated peer renders
the richer view. Old peers retain the existing view. A metadata flag in the HA
editor distinguishes actual detailed-panel support from legacy support.

## Independent feature negotiation

New one-shot API query `entity_cover_get_features` has no arguments and returns:

```json
{"v":1,"type":"entity_cover_features_v1","cover_panel_version":1}
```

New API `entity_cover_bind_features(channel: string, cover_panel_version: int)`:

```json
{"v":1,"type":"entity_cover_features_v1","cover_panel_version":1,"channel":"<32 lowercase hex>","accepted":true}
```

Reject response uses version0, empty channel and accepted=false. Query may
advertise0 when configuration is disabled. Require existing Cover capability
and successful `cover_stop_version:1` binding first. Bind only the exact current
channel, before any opening/selection. Reset panel peer state on reconnect,
rebind and mode changes. Missing/malformed APIs leave legacy Cover available;
they do not weaken its Stop requirement. Optional native configuration defaults
off. Feature payload limit remains512 bytes; entity envelope remains2048 bytes.

Structural public ingress may recognize the new command shape, but the matched
owner must reject it unless this channel negotiated panel version1. It must
never admit a detail command merely because the process supports the feature.

## Exact grant/state extension

Keep every legacy field, including:
`cover_state`, `position`, `available`, `cover_caps:{open,stop,close}`,
`state_generation`. A panel-bound selection adds exactly one object:

```json
"cover_panel": {
  "version": 1,
  "device_class": "blind",
  "tilt_position": 45,
  "caps": {
    "set_position": true,
    "open_tilt": true,
    "close_tilt": true,
    "stop_tilt": true,
    "set_tilt_position": true
  }
}
```

All inner keys are mandatory. Version is a strict integer; capabilities are
strict booleans. `tilt_position` is an integer0..100 or null. It represents
`current_tilt_position`; outer `position` represents `current_position`.
Unknown/unavailable entity clears both observations and disables controls.
Known primary state with missing tilt leaves only tilt position unknown.
Never infer0 from absent data or derive tilt from primary position.

Device class is one of `awning`, `blind`, `curtain`, `damper`, `door`, `garage`,
`gate`, `shade`, `shutter`, `window`, or `unknown`. Missing/invalid class is
neutral unknown, not an inferred blind. Class and capabilities are immutable
selection metadata: changes, including A-B-A while opening, revoke selection.
Position/tilt/state A-B-A increments the existing semantic generation.

Each capability requires both its actual Core feature and registered service:

| Capability | Bit | HA service |
|---|---:|---|
| open | 1 | cover.open_cover |
| close | 2 | cover.close_cover |
| set_position | 4 | cover.set_cover_position |
| stop | 8 | cover.stop_cover |
| open_tilt | 16 | cover.open_cover_tilt |
| close_tilt | 32 | cover.close_cover_tilt |
| stop_tilt | 64 | cover.stop_cover_tilt |
| set_tilt_position | 128 | cover.set_cover_tilt_position |

Use the bounded class/feature definitions from
[Core 2026.7.1](https://raw.githubusercontent.com/home-assistant/core/2026.7.1/homeassistant/components/cover/const.py).
Do not change feature bits on actual entities to make a test pass.

A panel may support only tilt or only numeric position. Therefore the new
panel domain must allow all three outer capabilities false if an inner
capability is true; preserve the legacy domain's existing rejection of an
entirely unsupported legacy Cover. No capability at all remains unsupported.

## Commands and exact targets

Identity and command sequencing stay unchanged. Legacy operations retain their
exact shape. Additional button operations `open_tilt`, `close_tilt`, `stop_tilt`
carry `op` and `expected_state_generation`, with no target. Additional numeric
operations `set_position`, `set_tilt_position` carry those fields plus strict
integer `target_index`0..100. Resolve to HA `position` or `tilt_position`, never
to both. The numeric model is the existing0..100, step1 percent lattice; do not
invent device granularity, inversion, or orientation from its icon.

Numeric controls require a known matching current axis position; preview stays
local and emits one absolute target on release. Open/close buttons can operate
with an unknown position if the entity itself is known and the specific
capability exists. Unknown position has no highlighted fabricated endpoint.
Non-Stop actions keep exact captured generation checks before and after await.

## Stop semantics — preserve the existing hard guarantee

- Primary Stop may replace one pending open/close/set_position operation.
- StopTilt may replace one pending open_tilt/close_tilt/set_tilt_position.
- Never replace across these families, never chain a second priority successor,
  and never map StopTilt to stop_cover or primary Stop to stop_cover_tilt.
- Reuse the existing bounded predecessor wait and service fence. A dispatched
  predecessor is not cancelled, retried or executed in parallel. An undispatched
  predecessor is cancelled before it can execute after Stop.
- Both Stop operations accept a captured generation that is not in the future;
  retain held Stop across known position feedback. Unknown state, metadata loss,
  expired selection or authorization loss still cancel it. Normal movement
  gestures remain strict and are cancelled by semantic A-B-A.
- Primary Stop keeps existing predicates and requires fresh post-dispatch
  stationary feedback. Never use the predecessor's earlier stationary snapshot
  as proof that a dispatched Stop worked.
- Standard HA exposes no separate tilt movement/stopped observation. StopTilt
  is enabled for a known entity with its own capability, even if tilt position
  is unknown. Do not infer stopped tilt from unchanged position, primary
  open/closed state, or a service return. Preserve existing result protocol:
  ha_accepted followed by not_confirmed/state_timeout when physical confirmation
  is unavailable. Present this neutrally as an unconfirmed command, not proof
  of a jam or of successful stopping. No synthetic tilt-motion field in v1.
- Closing the view never dispatches either Stop or any inverse command.

The separate tilt position and absence of a tilt-motion state follow the
[Core Cover entity contract](https://raw.githubusercontent.com/home-assistant/core/2026.7.1/homeassistant/components/cover/__init__.py).
An endpoint already observed can satisfy open_tilt/close_tilt or an exact target;
that confirms the reported position only, not physical movement of the motor.

## Implementation seams and acceptance

HA: extend Cover policy/domain in place; add feature handshake, exact optional
codec branch, metadata and transport projection. Keep legacy Cover tests intact.
Do not duplicate ControlSessionOwner. Outer metadata can expose `cover_panel`
alongside existing `cover_control`; no old metadata field changes meaning.

Native: extend existing Cover snapshot and pending-operation enum, same pointer
capture and rail behavior as existing scalar controls. One detail root or
subsection renders primary position and optional lamelles, SVG illustration
chosen by actual class, visibly separate primary/tilt controls. Reject extra
fields in legacy mode and unexpected absence of the extension after binding.

Focused host cases: all256 feature combinations crossed with service loss;
tilt-only/position-only; malformed positions and class; independent targets;
unknown primary vs missing tilt; held drag A-B-A; same-axis pending target then
Stop before/after dispatch; Stop without position; no cross-axis successor;
duplicate sequence, future generation, lost permission/lease, reload, and
unchanged legacy wire fixtures. StopTilt must never yield a false state_matches.

Hardware: existing distinct garage/blind mocks; migrate blind slot17 to Cover
and hide redundant tilt slot18 after acceptance, retain garage slot5. Exercise
actual primary and tilt targets, both Stop controls only when advertised,
close/reopen and every capability state with original screenshots. Capture
before/after source state and layout, service order, memory and shared route
performance. Mock feedback is not physical motor evidence.

## Implementation checkpoint — 2026-11-04

Backend implementation lives in `cover_panel_domain.py`, the existing
`cover_control.py`, codec, feature negotiation and transport/catalogue projection.
There is one existing service fence and one selection owner; no copied session
implementation. `test_cover_panel.py` covers all256 feature masks crossed with
service loss, separate observations/dispatch, legacy/new envelope isolation,
negotiation, held ABA, matching-axis Stop priority and authorization/close races.

Full HA host suite:890 passed,2 skipped,3877 subtests in21.49s. Receipt:
`C:/aeh-build/device-panels-20261104/ha107-full-tests.txt`.
The prepared opt-in device harness is
`C:/aeh-build/device-panels-20261104/cover_device87.py`; it records real service
calls on a separate authenticated event subscription, exact-source identity,
HA observations, original device screenshots and layout preservation. It has
not been executed by the backend implementation agent. Device flash, screenshots,
performance and physical motor behavior are not established by these host tests.

The installed-tag Core demo garage supports only open/close, with no numeric
position. The owned blind demo exposes both axes but no device class; keep its
neutral unknown icon. Core demo targets round to tens internally, so the harness
uses exact multiples of10 without changing the public step1 contract. Demo Stop
methods do not immediately publish state, and tilt has no stopped field. Report
service acceptance and stable simulated feedback separately from confirmation.
