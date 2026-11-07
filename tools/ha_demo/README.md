# Atmosfera demo devices

`atmosfera_demo` is an opt-in Home Assistant integration. Copy its directory
into HA's `custom_components` directory, restart HA and add **Atmosfera Demo
Devices**. It uses selected simulation providers from the installed HA Core
demo package, plus a local activity remote and mower. Provider capabilities
depend on the installed HA Core version.

The fan platform keeps the percentage fan and a separate preset-only fan:
`fan.atmosfera_demo_fan` and `fan.atmosfera_demo_fan_presets`. The latter uses
Core's actual preset provider rather than changing the first fan's feature
flags. Core 2026.7.1 provides these at indices 2/4 with unique IDs fan3/fan5 and
feature masks 55/56. Recheck those provider identities when upgrading Core.

The demo notice and doorbell buttons target the sole configured Atmosfera
display. Add `camera.atmosfera_demo_camera` to that display's camera catalog
before using the doorbell button. Create the timer, date/time and text helpers
using the names in `demo_layout.py`. The optional vacuum area mapping uses a
demo-only HA area and the simulated `living_room` segment.

`demo_layout.py` builds a primary layout and two alternative layouts. The
primary layout retains the existing thermostat and light controls when
available. The secondary layouts exercise additional control modes, media
actions, information cards and automations. Import a layout through the HA
editor, review the draft, then save. Cards refer to named simulation entities
and the existing HA sun provider. Scenes, scripts and automations for the
demo should target simulation entities only.
