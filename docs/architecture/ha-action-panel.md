# Dedicated Action panel: optional `action:2`

This profile extends the existing `entity_panel_extra_v1` negotiation. A native
peer must advertise and accept `action:2`; the saved action alone does not enable
it. Old Panel, Info/Lock, Media, Light and Climate envelopes remain unchanged.
The backend uses the existing single selected owner, App6 lifecycle, caller
authorization, command sequence and one-service fence. There is no new polling
task, second session owner, framebuffer, or action queue.

The explicit v3 action is `{kind: control, control: panel, property: action}` for
`button`, `input_button`, `scene` and `script`. For `automation`, strict booleans
`skip_condition` and `stop_actions` are also required. Entity and Action card
types are accepted; passive Sensor cards are not. Nothing migrates implicitly.

## Closed operations and truthful outcomes

| Subtype | Operations | State shown |
| --- | --- | --- |
| button/input_button | Press | Stateless; separate last-use timestamp |
| scene | Activate | Stateless; separate last-use timestamp |
| script | Run while idle, Stop while running | Running/idle, optional active/queued count |
| automation | Enable, Disable, Trigger | Enabled/disabled, separate optional active count |

Capabilities come only from registered HA services. Unknown first-use timestamps
on existing momentary entities do not make those entities unavailable. Unknown
script/automation state disables controls; unavailable always clears old metadata.

For ordinary Action2, Press, Activate and Run report only successful completion
of the HA service callback. Ordinary Script Run uses `script.turn_on`, which
does not wait for the script sequence. ActionParams1 Run has the separate
dispatch-only outcome described below. Stop, Enable and ordinary Disable require a new authoritative
phase after dispatch before reporting `state_matches`. Callback success alone is
not a physical-effect claim. Failure or timeout never triggers a retry.

HA115 uses the public `hass.services.async_call(blocking=False)` only for
Automation Trigger. Core validates the service/schema, schedules its background
handler, and returns without waiting for the automation sequence. The existing
owner holds its service fence until that dispatch call returns, then emits the
terminal `service_dispatched` (native result7). This says only that HA accepted
dispatch; it does not claim the condition passed, actions started, or the
sequence completed. The user can issue another explicit control, including
Disable, without waiting for the sequence to finish. No new integration queue
or background provider task is created; Core owns execution and logs subsequent
provider failures. An error before scheduling is still `rejected/service_error`.
Late provider failure cannot change that truthful dispatch receipt, publish
completion, reopen a retired view, or cause a retry.

This new terminal requires negotiated Action2. HA115 offers no Action1 fallback;
older native firmware can retain Info/Lock/Media while Action stays unsupported.
Native95 still accepts old HA114's Action1 with its unchanged callback-completion
semantics. Snapshot shape, command `action_version:1`, metadata catalogue version1,
and all non-Action profiles remain unchanged. This version boundary prevents an
older owner from interpreting result7 as successful execution. Other ordinary Action2 service calls retain the default blocking mode and
existing timeout/fence behavior. ActionParams1 is a separately negotiated
extension, not a change to the ordinary Script Run receipt.

With `stop_actions: true`, Disable remains eligible even if the automation is
already off or `current` is zero/unknown. It always calls `automation.turn_off`
with that exact policy and reports only `service_completed`; it cannot infer
that every action stopped from the enabled flag. With false, Disable never asks
HA to stop existing action runs. Trigger passes the saved `skip_condition`
explicitly. New panels default both policies to false; explicit conversion of a
legacy service preserves its actual HA policy, including omitted-field defaults.

Ordinary Action2 Script Run has no variables. It reads HA's public cached named-script
service description, using the script registry `unique_id`, not a potentially
renamed entity suffix. Required fields block Run even if a UI default exists.
Missing, malformed, unregistered or oversized metadata is explicitly unavailable;
no configuration reload or global metadata-fetch task is introduced. The field
map is bounded to 128 fields with names of at most 128 UTF-8 bytes. Unsupported
grouped metadata fails closed. Stop does not need parameters.

## Freshness and bounds

The action snapshot has closed capability and observation dictionaries. Timestamp
and optional count are display-only: they do not invalidate a held action.
Source/phase transitions, including ABA, advance semantic generation. Service
set, subtype, script gate or saved policy changes retire the selection. Every
command includes `action_version: 1`, full existing selection identity and exact
expected generation. Entity IDs, service names, variables, policy changes, target
values and facets cannot be supplied by an ordinary Action2 command. The explicit
ActionParams1 extension below adds only one Boolean value to its Run command.

Last-use text is a complete timezone-aware ISO value, at most 48 UTF-8 bytes, or an
explicit unknown/invalid/too-long status. Extended fractional precision is not
silently rounded. `current` is null or an integer 0..65535, never clamped. Native
validates bounded printable text and status consistency; HA owns date semantics.
The existing 2048-byte envelope remains the ceiling.

## Optional required-Boolean form: `ActionParams1`

The product introduced this extension in native116/HA131 and qualified it in
native117/HA131. The reusable option
`action_controller.parameters` defaults to false. It requires the existing
Action2 profile and an independent channel-bound
`entity_action_parameters_query` / `entity_action_parameters_bind` exchange;
the eight Extra profiles are unchanged. A missing or rejected feature leaves
ordinary Action2 intact and the new form unavailable.

A form is selected explicitly with this v3 action:

```json
{"kind":"control","control":"panel","property":"action","parameters":"boolean_v1"}
```

Only a real `script.*` entity with exactly one declared field is supported. The
field must have `required: true` and a Boolean selector. An optional field,
additional field, unsupported selector, invalid default or unrepresentable label
makes the form unsupported. No existing card is migrated. The saved card never
contains the Boolean draft, field name or service name.

The device reuses the existing Action view and three buttons. No and Yes edit a
local draft; only Run sends a command. Missing default starts at UNSET and blocks
Run. An exact Boolean default prefills a visibly identified choice, including
false. Stop keeps the ordinary guarded `script.turn_off` path with no parameter
fields. Existing status/current-run text remains visible. Button rows swap only
for the form, using configured geometry; ordinary geometry is restored after
retirement, without changing the closing preview.

The selected owner keeps the draft and its revision. A new grant, revoked or
lost selection, or view retirement clears it. Telemetry updates with unchanged
semantic generation preserve it. A Run press captures both authoritative state
generation and local draft revision, so changing No/Yes/No while holding Run
cannot dispatch the old press. Losing form readiness cancels a held gesture
and resets an explicit choice to the current default or UNSET on the readiness
edge. An unchanged unready render does not repeatedly advance the revision.
Full labels and selected/default captions must fit; an incomplete caption blocks
form Run and choices without blocking an otherwise valid Stop.

HA resolves the direct script service through the entity registry unique ID.
Its private binding retains registry identity, the actual registered Service
object, captured field name and validated field semantics. The wire adds flat
`parameters_version`, `parameter_status`, `parameter_label` and
`parameter_default` capability fields; labels are complete printable UTF-8 up to
96 bytes. A new-form Run adds only `action_parameters_version: 1` and an exact
Boolean `parameter_value`. Unknown/null is never converted to false.

The existing authorization, selected session, lease, command sequence and
single-service fence remain responsible for dispatch. Inside the scheduled Run
job, HA checks the selection, principal, current state/generation, captured
metadata and Service object again. Without yielding between that check and the
public call, it dispatches `script.<unique_id>` with only the captured field and
Boolean, using `blocking=False`. It does not add `entity_id` to script variables.
A successful response is `service_dispatched`; script completion and physical
effects are not inferred. Scoped service/registry lifecycle events retire stale
forms. A failure causes no retry.

The native117 correction admits `service_dispatched` only for a pending Run of
the negotiated ActionParams1 script selection, with the existing exact identity
and command-sequence checks. It clears that pending command and reports result7,
without claiming execution or waiting for a running-to-idle transition. Ordinary
Action2 Script Run still rejects this receipt; Params Stop still uses the
ordinary authoritative `state_matches` contract. The native116 parser accepted
the receipt but its owner omitted this specific dispatch-only branch, leaving
one successfully dispatched False command pending on the device. That failed
acceptance record remains preserved.

The native117 visual correction gives unavailable form Run the existing neutral
button palette, including UNSET and command-pending states. Active coloring is
recomputed from final readiness and owner admission, after any draft reset.
Colors are written only when changed. Ordinary Action2 and Stop retain their
previous styling. No display handoff, framebuffer, repaint path, widget, task
or timer is added by either 117 correction.

No new LVGL object, framebuffer, render worker, action queue or polling task is
added. The P4 type-size check with the feature enabled reports:

| Type | Native115 | Params enabled |
| --- | ---: | ---: |
| Complete `MaterialEntityControlComponent` | 11,728 B | 11,760 B |
| Contained `MaterialEntityControl` owner | 1,184 B | 1,200 B |
| `ControlSnapshot` / `ControlMessage` | 728 / 960 B | 728 / 960 B |
| Codec object / parser arena | 5,152 / 5,120 B | 5,152 / 5,120 B |

The total component increase is 32 bytes, including the owner's 16-byte increase.
The Action member grows from 68 to 168 bytes within an already larger variant;
it does not enlarge the enclosing snapshot/message. Disabled builds retain the
115 sizes. These are P4 compile-time measurements, not a claim about runtime free
heap, flash size or FPS. The envelope/feature limits remain 2048/512 bytes.

HA131 is installed and its actual public fixture metadata, catalogue and editor
were reconciled. The browser exposed the form after native116 negotiated Params1;
review/Undo restored the original unsaved card without a layout Save. Native116
was built and uploaded once, but acceptance failed: one explicit False Run had
the correct HA effect while its terminal receipt remained pending, and the
blocked Run button was not visually distinct. Later passive health does not
rewrite the unclassified first-boot failure. The isolated 117 fixes pass focused
host/P4 translation-unit checks, and the full 117 build and linked guard passed.
One117 OTA completed; its first-boot qualifier remains failed with an unclassified
Sendspin resource-error window. A separate passive health observation passed,
without a restart or retry. The bounded device route verified three explicit Run
commands and one ordinary Stop, followed by a clean bounded Home/Settings route.
Root reviewed the original images separately. The
canonical accepted runtime is now native117/HA131: root adopted exactly 25 final
firmware files and 18 HA files with preimage backups and journals. The last closed
device observation has original slot13 Info restored at layout410/Home1, with
the owned effect helper still false. The earlier Stop
screenshot is consistent with the preceding presented frame (neutral Run/HA accepted)
while the owner already reports terminal state_matches. Source review and a
focused real-LVGL117 test show Run returns active after terminal receipt and
after lifecycle resume; the image is not proof of persistent Run disablement.
Exact physical presentation latency was not measured. A separate same-firmware
check then sent exactly one default-False Run and one ordinary Stop. After a
one-second settle, root reviewed the original screenshot: Run is active and the
terminal state-matches caption is visible. The final Home original is coherent.
The check had no DSI/hard faults or cleanup errors and restored the original
card through revisions408→409→410. There was no additional OTA or full-route
repeat. First-boot qualification remains failed; scoped feature acceptance and
canonical adoption do not erase that limitation.

## Existing application handoffs

A notification-producing Press may retire App6 through the existing notification
mechanism. The service fence survives retirement; late callbacks cannot reopen
or paint the old panel. Existing Camera, notification, local Player, assistant
and gallery lifecycles are unchanged.

The direct doorbell at slot 30 is deliberately not converted. A normal Action
panel would occupy App6 during its service call and turn the established Camera
opening into busy/history behavior. Its future conversion requires a separate
bounded terminal-action/close-before-dispatch contract and hardware acceptance.

## Validation and future migration

Native95/HA115 passed the scoped hardware control scenarios on 5 November:
11 observed native commands, notification delivery, and 19 original screenshot
reviews. The initial batch stopped at a missing diagnostic argument in the host
tool; its original FAIL is preserved, with separate fixture/layout recovery and
three completed Settings measurements (55 FPS each). Evidence is recorded in
`C:/aeh-build/device-panels-20261104/action95-combined-runtime/report.json`.
Layout376 changes only slot15 to the Action launcher. A subsequent final Home
screenshot exposed its raw timestamp caption; the separate HA116 caption fix
is deployed and reviewed on the device and actual HA browser. Momentary Action
launchers now say Open; their history remains inside the panel. This does not
change the control protocol. Qualification
of boot audio and existing DSI warnings remains separately documented in the
current resume checkpoint.

The frozen wire fixtures cover all five subtypes,
seven operations, service-only/observed results and maximum identity fields.
Domain/owner tests cover required parameters, real service-capability admission,
source ABA, telemetry renewal, caller context, duplicate commands, service
failure, and notification retirement without late paint.

Initial migration scope is only slot 15 after a fresh actual source/layout
inventory and optional-profile negotiation. Hardware scenarios must use actual
owned, registered providers and services; REST state injection alone cannot
represent a working button, scene, script or automation. Prefer a minimal owned
provider/fixture extension. Do not broadly reload scripts/automations: if Core
requires it, first inventory unrelated running sequences and identify the exact
effect. The acceptance batch may temporarily bind the five test subtypes to
guarded slot 15, with CAS, intent journal and conflict-preserving cleanup. It must
not target physical slots 4/7 or direct doorbell slot 30.

Primary semantic references: [HA script integration](https://www.home-assistant.io/integrations/script/),
[HA automation actions](https://www.home-assistant.io/docs/automation/basics/),
[Core service metadata API](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/helpers/service.py),
[Core script service registration](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/script/__init__.py).
