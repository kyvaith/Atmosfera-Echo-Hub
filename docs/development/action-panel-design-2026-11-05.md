# Action panel integration

Action:2 is an optional dedicated view inside the existing entity-control
application (App6). Product composition supplies the 800×800 geometry, four
official Material SVGs and PL/EN strings. The companion component owns the
selected entity, capabilities, gestures, pending command, retirement and render
readiness. The Home Assistant integration owns permissions and service calls.
Opening the view never executes an action.

Action:2 changes only negotiation of the terminal `service_dispatched` result
for Automation Trigger; the existing payload shape stays unchanged. HA115 offers
Action:2 only, so native94 cannot select Action while its other Extra profiles
remain available. Native95 also accepts Action:1 from HA114 and retains its
legacy service-completed result6; result7 is admitted only under Action:2.

`action_controller` binds exactly 18 existing LVGL objects: one root, seven
labels, four alternative domain icons and three button/label pairs. The three
buttons have fixed presentation roles (primary, left, right); their operations
come from the native owner rather than YAML callbacks. Button and input_button
share one SVG. Scene, script and automation each have a separate SVG. Only one
domain icon is visible. The root belongs to `light_control_root`, so the existing
theme and application navigation already cover it.

The text provider checks retained `is_action_view()` before Media, Extra and
Detail. IDs 0–44 retain their native roles; ID45 adds the Action:2 queued-dispatch
message. ID4 uses an Action-specific ready prompt. This precedence preserves
the correct retired/unknown message during an ownership handoff. Source values
and operational policy must fit completely; no marquee or ellipsis is allowed
for a timestamp, count, operation or policy. The last-used prefix occupies its
own line above the complete HA timestamp. Unknown, invalid and too-long dates
remain explicit. A running/queued count is optional telemetry, never an
eligibility or completion signal.

## Semantics

- Button and input_button offer Press; scene offers Activate. They have no
  invented on/off state, and a first-use unknown timestamp does not mean that
  the source is unavailable.
- Script shows Run or Stop according to its observed phase. Action:2 passes no
  variables. Required parameters or missing parameter metadata disable Run
  with different explanations. Service acceptance does not mean the script
  completed or a physical device reacted.
- Automation shows the saved condition policy and disable policy. Skip
  conditions and stop actions are strict booleans. Stop-and-disable remains a
  service operation even when the automation is already disabled, because
  earlier actions may still be running. Ordinary Disable does not stop them.
- Automation Trigger reports `service_dispatched` after HA schedules the
  request without waiting for the action sequence. The UI says "Request sent to
  HA"; this is neither service completion nor confirmation that actions ran.
  This result requires negotiated Action:2 and is not reinterpreted as success
  for other operations.
- The editor explicitly reviews conversion and policy changes. Legacy omitted
  `automation.trigger.skip_condition` and `automation.turn_off.stop_actions`
  preserve HA's true defaults; a new panel/default tile uses false/false.
  Unsupported legacy data is not silently discarded.
- The first intended migration is slot15. Slot30 remains its direct doorbell
  action: opening App6 first would conflict with the existing Camera handoff.
  Terminal actions need a separate reviewed close-before-dispatch design.

## Drawing and memory

Action adds no worker, animation, polling loop, Scalar region, JPEG cache or
full-screen buffer. It reuses App6's existing navigation and preview lifecycle.
The four static SVG path objects live with their LVGL objects. Only the visible
96×96 icon draws; `SvgIcon` bounds its temporary ARGB layer to that size
(36,864 pixel bytes before allocator/renderer overhead), rather than the screen.
This is not a claim that SVG rendering is allocation-free.

The native renderer owns foreground on immediate children of Action buttons.
Setting only the parent's text color is insufficient: ordinary SVG objects can
receive their own default-theme card color. Use the same scoped foreground
ownership as Media93a. Palette references come from configured default styles,
not retained disabled/pressed colors. No global SVG/theme behavior is changed.

The translation table remains the flash-backed i18n table. Button captions use centered 32px-high label boxes: every supported PL/EN
caption fits a single existing 29px font line. Hitboxes remain unchanged.
No font is added;
the view uses existing Roboto16/20/24/30. Actual linked memory, first boot,
device screenshots and a matched performance sample are separate acceptance
gates after configuration/component checks. Source font fit is only an early
layout check, not device evidence.
