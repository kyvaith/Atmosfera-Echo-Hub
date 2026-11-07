# Dedicated device panels

The user requested recognizable Material 3 device views, beginning with Fan,
and carousel tiles that open a view instead of executing a device command.
The Player, Gallery, Voice and Camera application implementations remain outside
this change. Each new panel is accepted on hardware before the next package.

## Fan design and ownership

The reference is Home Assistant's [Fan more-info view](https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-fan.ts):
primary speed and power, with preset, oscillation and direction controls only
when the integration supports them. The compact connected speed buttons follow
the [Material 3 Expressive button group](https://github.com/material-components/material-components-android/blob/master/docs/components/ButtonGroup.md).
The circular product layout has its own fixed geometry and SVG fan illustration.
No bitmap asset or continuous decorative animation is introduced.

One existing entity-control selection owns the entire fan, including its
presets. HA retains authorization, exact capability mapping, command sequence,
state generation and source confirmation. Opening never executes a fan service.
A command captures the observed generation on press and sends one absolute
target on release. Meaningful changes, including A-B-A, invalidate held input.
Unknown values remain unknown and disable only the affected controls.

The new native kind is optional `fan`, enum4 in `entity_control_v1`. The envelope
remains limited to 2048 bytes. Speeds use the existing exact Core mapping for
one to seven actual speeds plus off. Presets use a complete list of at most
eight names. Larger lists are not truncated; their control is unavailable while
other supported fan functions remain accessible.

App6 contains the new fixed widget tree. The main LVGL task owns its state and
input. It uses the existing navigation admission, close gesture and single
shared application work buffer. There is no fan framebuffer, extra display
worker or second entity session. The illustration is a bounded static SVG path;
its renderer must never allocate an RGB888 display-sized vector scratch buffer.

## Verification

The unchanged native84 baseline on 4 November reported 54 source FPS for the
standard Settings route, 80 frames, 16306us average, 22044us maximum and zero
failed submissions. Home had 4441184 bytes free PSRAM and 13395 bytes internal
RAM after the route. This is source cadence, not panel scanout FPS.

Current development evidence is in `C:/aeh-build/device-panels-20261104`.
Firmware compilation, flash, device screenshots, physical input and actual
motor movement are separate acceptance claims.

Native86 device acceptance passed for full Fan, preset-only Fan and both
Humidifier simulations. Evidence directories are `fan86-device-final`,
`fan-presets86-device` and `humidifier86-device`, each with `report.json` and
original800x800 device screenshots. Touch input was injected through the
diagnostic GT911 path; no physical motor or finger acceptance is claimed.
Opening is passive, native input changes HA state, held stale commands are
cancelled, and unavailable/recovered/reopened scenarios pass. Native86 also
accepts a valid observed67% outside the selectable33/66/100 catalogue without
rounding it or disabling valid targets. Preset-only coverage uses a distinct
provider that genuinely advertises preset support.

The native86 matched Settings route reports54 source FPS,79 frames,16351us
average,23066us maximum and0 failures. Its post-route free PSRAM is4533788B
and internal free RAM20107B. These snapshots are not a controlled RAM leak
test; view histories and compressed caches vary. Native87 is being compiled
with Cover axes and an i18n capacity fix: the512-entry table silently omitted
late Polish keys, despite correct generation. The new exact574-entry table
adds744bytes on ESP32-P4. Hardware Polish-label acceptance remains pending87.

## Following panels

After Fan, consolidate Humidifier and Cover controls into their own recognizable
views, then the robot, mower, remote and remaining function domains. Keep the
same owner and fixed resource pools. A launcher replaces duplicate per-action
tiles only after the corresponding panel has passed its device scenarios.
Do not reimplement the protected media, photo, voice or camera applications.
