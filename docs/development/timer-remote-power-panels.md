# Timer, Remote and Power panels

These product views share the existing App6 lifetime, ControlSessionOwner,
navigation preview and work buffer. Their reusable optional renderer is
`panel_controller`, with separate `timer`, `remote` and `power` profiles.
The negotiated kind7/family contract gates launchers; opening a view is passive.
Player, Gallery, Camera, Voice and notification behavior are unchanged.

## Visual design

The [Home Assistant Timer view](https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-timer.ts)
separates its duration draft from the live remaining time and exposes actions
for the current phase. Atmosfera follows that distinction with a large
HH:MM:SS readout, a small stopwatch SVG, separate hours/minutes/seconds controls
and explicit Start, Resume, Pause, Cancel and Restart actions. Local editing
does not dispatch a service. Resume preserves remaining time; Restart applies
the draft. Reaching zero while HA still reports active is not a finished event.

The [Home Assistant Remote view](https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-remote.ts)
uses the device's actual activity catalogue. Here, a remote SVG and the current
activity are prominent, with Power and Activity controls below. The picker
shows up to eight exact names; choosing a row is a local preview and Apply
dispatches once. No fabricated keypad, volume controls or TV state is shown.

The [Home Assistant Switch view](https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-switch.ts)
emphasizes state and power. Atmosfera uses a larger, actual-class SVG for an
outlet or switch, a separate observed state and one absolute power action.
Unknown class uses a neutral power symbol. Unknown state never looks switched
off. Capability-driven control groups center the remaining supported actions.

Rounded tonal buttons, clear primary actions and restrained typography follow
the [Material 3 button guidance](https://m3.material.io/components/buttons/overview).
Existing theme roles color the child trees. Disabled controls use the native
neutral palette, including labels, instead of a dark on-accent label on grey.
There is no continuous decorative animation. SVG source attribution and exact
adaptations are in [panel-icons.md](../../assets/icons/panel-icons.md).

## Product geometry

All coordinates refer to the round 800×800 product. The reusable renderer reads
configured widgets and does not contain these coordinates.

| View | Layout and input centers |
| --- | --- |
| Timer | Kind at y68, title y104, 64px SVG y158, phase y236, 53px countdown y276. Draft columns at x146/322/498, y400. Minus centers x182/358/534 and plus x266/442/618, all y514. Three action centers (268,594), (532,594), (400,666); a lone Start centers at (400,630). |
| Remote | 96px SVG y168; state y292 and wrapped activity y366. With both controls, Power (400,534), Activity (400,610); a single Power (400,570). The eight-option modal uses columns x262/538, rows y262/362/462/562, Back (295,686), Apply (505,686). |
| Power | Actual-class 128px SVG y210, state y384; 280×88px action at (400,548). |

Status copy stays within x200..600, y706..746. The existing bottom close gesture
zone y750..800 remains available. Modal backgrounds consume gap taps and native
input admission rejects underlying controls. Option labels use Roboto18 WRAP,
240px width and 72px maximum height within fixed 84px buttons.

## Resource and validation boundaries

The three panels add 86 product objects and five bounded static SVG paths,
using existing fonts. Only one panel is visible. SVGs reuse the existing
bounded vector draw path; they allocate no persistent bitmap or full-screen
buffer. Timer repaint is limited to a changed countdown once per second in
the existing component loop while its view owns pixels. Hidden/captured views
do not maintain their own ticking task or LVGL timer.

The 31 new keys in each language pack bring the current table to 688 entries:
8256 bytes of 32-bit translation pointers, 744 bytes above candidate88. This
is exact compile-time capacity; localized strings remain flash-backed.

Configuration and static checks are recorded separately from firmware and
device acceptance. The product audit checks every profile reference, SVG
subset and translation key. Actual configured font advances fit the Polish
Restart label in 220px and an observed `596523:14:07` countdown in 540px.
The Remote picker reuses the Robot font/wrapping bounds already tested with
32 wide characters. Final firmware, source identity, real-device screenshots,
service behavior and batched performance/memory checks remain required before
claiming hardware acceptance.
