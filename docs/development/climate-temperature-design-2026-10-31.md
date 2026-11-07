# One climate target temperature

W07 starts with explicit v3
`{"kind":"control","control":"number","property":"temperature"}` on a Climate
Entity card. Existing Number/input_number actions and default Climate actions
retain semantics. Reuse app6, numeric_steps_v1, its two step buttons, single
owner, semantic generation, authorization and absolute service fence.

HA owns TARGET_TEMPERATURE1, live set_temperature, min_temp/max_temp and an
explicit positive target_temp_step. Read the target attribute `temperature`, not
current_temperature or the HVAC mode string. Unknown/missing/off-grid is null;
no invented22. Require a recognized live HVAC mode; auto and heat_cool remain
outside this first single-target adapter. Do not send hvac_mode or a power action
as a side effect. Exactly one supported adjacent step becomes one absolute
temperature command, only after fresh state/domain checks.

Check installed Core before deriving units: Core2026.7.1 converts state min/max/
target into the HA unit but exposes the native target_temp_step unchanged.
Read the loaded climate entity's native unit as well as HA's configured unit.
Initially admit matching Celsius/Celsius or Fahrenheit/Fahrenheit only. A native
unit mismatch or unavailable entity metadata disables this adapter rather than
inventing a converted step. Newer Core may supply an explicit converted
temperature_unit state attribute; support must be grounded in its step contract.
Cross-unit conversion and dual range are separate remaining work.

Keep the numeric domain exact and bounded, including decimals, endpoints,
metadata/state ABA, service/feature loss and unit changes. Editor admission is
explicit, reviewed, draft-only, undoable; preview sends nothing. The browser
receives canonical metadata from HA and compares current state/metadata before
review confirmation; the backend remains service authority.

No new native task, timer, buffer, codec or firmware is needed. Use an owned real
MQTT climate with separate target/mode topics. Observe the target command before
publishing state feedback, assert no mode command, capture PL/EN and adverse
states, then exact cleanup and matched Home/Settings performance. Physical HVAC
and long audio/cold-start acceptance remain separate.

Sources: [HA Climate](https://contributors.home-assistant.io/core/entities/climate/),
checked31 October2026, and installed Core climate/__init__.py SHA
69f7b794cf4e76ab814898eb2d6cc908d9a7315e684c4c697ce346df990eb312,
MQTT climate.py SHA98420e70bba64294aa86cdbc1878dc48d33dcadb70504fbc3aadde72281ccb04.

Scoped acceptance HA50/native40:564Python(3skipped)/289Node,35 installed/pinned
files, real MQTT21.5→22→21.5 with exactly two target commands before feedback
and no mode command. Held target ABA,16/30 endpoints, explicit None/off-grid,
auto/outage, step change, native/display unit mismatch and Celsius recovery
passed on device. Sixteen original captures plus browser review/Confirm/twoUndo/
noSave were inspected; exact cleanup133 preserved16cards/3cameras/eight prefs.
Normal route79frames/53sourceFPS/avg16340us/max23134us/failed0; PSRAM5028KiB,
largest3712/internal26/JPEG917, app_work/scroll/close0. Firmware40/full ELF
reverified; no native rebuild. Receipt `ha50-temperature-scoped-acceptance.json`
in the 31 October evidence directory.

Initial48/v1 and49/v2-v3 rejected metadata before binding any layout. The actual
boundary was Core's UnitOfTemperature StrEnum versus NumericDomain's intentional
plain-string contract;50 normalizes str only after verified unit equality.
DATA_COMPONENT remains idiomatic, but its HassKey subclasses str and was not
the cause. A temporary diagnostic field was retired before50 was frozen or
installed. First post-performance enumeration timed out before input; preserved
as FAILED, while the fresh second run passed. No unsupported whole-product or
physical HVAC acceptance is implied. Matching Fahrenheit is host-tested;
cross-unit conversion, range/auto targets and the shared retained-result caption
after an unavailable state remain explicit follow-up work.
