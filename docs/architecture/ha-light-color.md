# Light Detail Color1

Color1 extends the existing selected Light Detail owner and channel with one
optional `color` facet (mask bit 4). It does not consume an Extra profile or
create another service queue, task, display buffer or carousel action. Product
UI remains declarative; the native owner retains a bounded local H/S draft.

`entity_detail_color_query` and `entity_detail_color_bind` are response-only
APIs using type `entity_detail_color_v1`, version 1. A supported query response
and a successful current-channel bind are required after Light Detail1. Missing APIs, rejected ACKs, reconnects and
client replacements leave the old Detail behavior intact. MAIN grant/state
only gains the facet bit; the `light_color` object exists solely in a selected
color STATE. The closed command carries H/S milli-units, view sequence and
expected state generation, without brightness, entity ID or service names.

The HA adapter accepts lights supporting HS, RGB or XY (HS then RGB then XY
service conversion priority). RGBW/RGBWW are excluded because their independent
white channels need a separate contract. Existing Kelvin and effect controls
are unchanged. A powered light in color-temperature mode can enter Color using
HA's published derived H/S and RGB. Apply explicitly switches to color even
when this seed has not moved; its label is “Przełącz na kolor”. In an existing
RGB/HS/XY mode, untouched, returned-to-seed or projection-equal edits produce
no service call, even if the preferred write route differs from the active mode.

H is 0..359999 and S is 0..100000; UI's 360-degree endpoint wraps to zero.
The untouched or returned-to-seed swatch uses authoritative source RGB. Only
a changed local H/S draft uses V=255 for its preview; its hex value is read-only.
Displayed H/S values have one localized decimal without rounding the retained
milli-unit values. Brightness stays in the existing separate control. Off,
unavailable, malformed source color and unknown/zero
brightness disable Apply; off/unavailable state never exposes retained color.
The user first powers on through the existing control.

Apply sends one `light.turn_on` with `hs_color` and the exact observed integer
brightness (1..255). It never converts brightness through a percentage or
changes an effect. The source generation includes mode, power, raw H/S and XY,
RGB, raw brightness and effect. A state ABA cancels the old input even if the
values return. Name/icon changes do not. Existing principal authorization,
card/revision identity, view generation, deduplication and service fences apply;
a Color-only fresh read also fences the service-task scheduling boundary.

Confirmation requires a newer authoritative generation, the expected mode,
unchanged exact brightness and the RGB projection produced by installed HA's
color conversion helpers. Different provider gamut/quantization remains
`ha_accepted` then `not_confirmed`; there is no retry or claim of physical color
accuracy. Cancel and navigation send no light service command.

## Native ownership and product composition

Color is facet 9 of the existing [Detail owner](entity-control.md#light-detail-and-climate-facets),
not another application or lease. The optional `light_color_profile` defaults
to disabled and requires Light Detail. Its product composition supplies 15
widget references: 13 for the facet and the MAIN launcher with its label.
Geometry, fonts and translations live in `modules/lvgl/pages/light_color.yaml`
and the product text provider; reusable components contain no screen dimensions
or product colors. See the [extension rules](../development/extending-ui.md#light-color-facet).

The neutral root owns pointer capture with `PRESS_LOCK`. Sliders are visual,
non-clickable children: the native owner admits a press before changing the
draft, fixes one axis for that contact and validates the same pointer, view and
semantic generation on updates and release. Rail movement and release change
only the local draft. Cancel discards it; an admitted Apply release submits at
most one command. Facet changes, revocation and authoritative generation changes
retire the draft and held gesture. The existing Detail handoff still drains the
Scalar presenter before revealing this facet.

Color uses the existing App6 preview and navigation lifecycle, with no new task,
poller, animation, snapshot slot or full-screen buffer. The visible swatch owns
its background color and contrasting black/white text. Immediately after
`lvgl_material.theme.apply`, the product calls
`refresh_light_color_palette()` before snapshot refresh so theme recoloring
cannot replace the source/draft swatch; this does not mutate the draft or emit
a command. Control appearance reuses shared styles rather than allocating one
disabled style per button.

## Validation boundary

The isolated ESP32-P4 ABI probe measured a 16-byte Color snapshot variant and
a 20-byte draft. Snapshot and Message remain 728 and 960 bytes; the owner grows
from 1136 to 1160 bytes and the component from 11584 to 11664 bytes, including
its embedded owner. Do not add those two growth figures together. These are
target type sizes, not measurements of total live RAM: the 15 LVGL objects,
style/text allocations and retained cache contribute separately to live usage.

For candidate native103, focused host tests include 13 public-LVGL scenarios
using the product geometry and generated font metrics, plus configuration,
glyph/fit and protocol/owner checks. The complete native103 ESP-IDF build,
one OTA and scoped device acceptance with HA125 passed on 6 November 2026.
Two explicit native commands each produced one HA service; one guarded restore
returned the owned demo light to its original CT/brightness state and cancelled
held input. Eight original screenshots were reviewed. Exact evidence and limits
are in the [current checkpoint](../development/resume-2026-11-05-datetime.md).

Settings maintained 55 FPS in one bounded route. The Color manual loop sampler
measured actual loop execution costs of 13.544 ms average and 61.873 ms maximum,
with 10 loops above 30 ms. The overall measurement window also includes API
waits; it does not establish continuous touch/frame cadence or 60 FPS, and
those waits do not explain the measured loop peaks. A source review found no
full-tree refresh per preview sample; the peaks remain unexplained. The first boot is qualified by the
known recovered mixer allocation retry. Neither host nor device evidence
establishes acoustic output, physical lamp color accuracy or absence of leaks.

The host corpus is `tools/tests/fixtures/light_color/wire.json`. Focused tests
exercise actual service ingress, all source reasons, default-off negotiation,
client/epoch changes, H/S precision, CT mode switch, unchanged/Cancel behavior,
authoritative ABA and task-boundary cancellation, context and duplicate writes.
Compilation, hardware touch/visuals, memory, audio and physical output are
separate acceptance steps, not implied by host tests.

For the owned demo light used for hardware acceptance, capture its full public
mode, H/S or Kelvin, raw brightness, effect (only if supported) and power before
testing. Restore through one public `light.turn_on` with the original active
mode and brightness, then `turn_off` only if originally off. Do not send
`effect: null`, fabricate hidden off-state color, or overwrite an independently
changed source. Current demo light_2 is on in Kelvin mode and has no effects;
restoring its captured Kelvin and brightness is sufficient.
