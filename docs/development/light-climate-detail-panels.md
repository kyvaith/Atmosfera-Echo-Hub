# Light details and Climate composition

Candidate native90d / HA111, 4 November 2026. This document describes the
product composition under implementation. Source/configuration checks,
firmware compilation and physical display acceptance are separate evidence;
this document does not claim a completed device test.

The explicit Light detail launcher keeps the current brightness renderer,
power buttons and their geometry. A transparent add-on supplies White
temperature and Effects buttons only when Home Assistant reports those
capabilities. Existing Light cards retain the original view. Climate gets
its own full panel while the old Number/temperature thermostat remains
unchanged. Both use the same selected entity, control owner and App6 lifecycle.

## Visual reference and behavior

The original [HA Light control](https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-light.ts)
separates brightness, white temperature and effects according to capability.
The [HA Climate control](https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-climate.ts)
separates actual temperature/humidity from the target and exposes supported
HVAC choices. Those are the functional references, with
[Material 3 button hierarchy](https://m3.material.io/components/buttons/overview)
and the product's existing large thermostat dial. HA's bitmap color-wheel
asset is not imported. This package does not add an RGB picker.

Climate keeps the accepted 600px native arc, 46px knob, large target,
separate measurement and compact precision controls. Its new mode button
opens the actual HVAC catalogue; there is no generic power button that
guesses a heating mode. Parameters opens a local menu containing only
supported Humidity, Preset, Fan, Vertical swing and Horizontal swing facets.
The menu displays names, not speculative cached values. Opening a facet
fetches its actual observation and one bounded catalogue/domain from HA.

White temperature and humidity share one numeric view. Each has a distinct
SVG, a prominent target, separate optional current measurement, actual domain
endpoints and a linear rail with precise adjacent-step buttons. One drag
previews locally and submits one absolute lattice index on release. Effects
and HVAC choices share one eight-option modal with an explicit candidate
and Apply. Complete labels wrap; they are not truncated into ambiguous choices.

Back within these views is a read-only navigation operation. Closing App6
continues to use the existing gesture from the bottom edge. Opening a view,
opening Parameters or choosing a candidate does not execute a device service.

## Geometry

Coordinates below are product-specific, on the 800×800 display. Reusable
components read widget geometry and contain no corresponding constants.

| Region | Product geometry |
| --- | --- |
| Existing Light direct scalar | x118/y410, 564×112; unchanged track and preview bubble |
| Existing Light On/Off | x174/418, y560, 208×80; unchanged |
| Explicit Light add-on | 40px bulb at380/66; centered 508×56 row at146/650, buttons244px with20px gap |
| Explicit Light status | x220/y714, 360×40; replaces the legacy status only for this profile |
| Climate dial | Existing group70/66, arc100/110, 600×600; existing target/current/activity/precision coordinates; only the new limits label widens282→440px to show complete range observations |
| Climate observed mode | x200/y207, 400×30, separate from actual HVAC activity |
| Climate actions | Centered508×56 row at146/646; Mode and Parameters, single remaining action centered |
| Climate status | x200/y706, 400×40; never overlaps the legacy654px status |
| Parameters | Five244×96 cards, centered wrapping group146/280,508×312; one 96px thermostat SVG |
| Shared numeric | Title104; icon158; target296; optional current366;508×72 rail at146/394; precision centers292/508,538 |
| Shared choice | Eight264×84 options at130/406 and220/320/420/520; complete Roboto18 labels240px wide, maximum72px high |
| Back and Apply | Numeric/Parameters Back400,686; choice Back295,686 and Apply505,686 |

The bottom 750–800 gesture region stays available. The Light add-on is
transparent and does not intercept taps outside its controls. Numeric,
choice and Parameters roots are opaque and clickable so gaps in their
contents cannot activate the view beneath them.

## Ownership and bounded resources

The existing control session owns selection, authorization, view generations
and the single pending command. Native components own pointer capture,
integer-lattice math and presentation handoff; product YAML binds widgets
and localized strings. The direct Light region must suspend and drain before
a facet replaces it, and resume only after a coherent native base is restored.
Climate reuses thermostat math through a typed active facet rather than
pretending to be a legacy Number control.

Only one numeric facet or one catalogue of up to eight 32-byte labels is
active. The Parameters menu does not retain five catalogues or subscribe to
separate sessions. No new framebuffer, direct renderer, animation worker or
polling timer is introduced by these compositions. Static SVG geometry uses
the existing bounded SVG widget. Its transient ARGB draw layers are limited
to icon dimensions: the Parameters view has one 96px icon plus up to five 32px
icons (57,344 bytes of pixel area if all are simultaneously queued); the
numeric view has one visible96px icon (36,864 bytes). No full-screen raster
asset or per-facet raw preview is added.

The two product packs contain730 entries after the explicit observed-mode,
activity and passive-source captions. The fixed translation pointer table
is8,760 bytes on32-bit ESP32-P4. Existing Roboto fonts are reused. The static
audit checks all 74 profile bindings, unique widget IDs, actual font widths,
six SVG sources and the retained dial geometry before full configuration
validation. It does not establish frame rate or physical touch behavior.

## Compatibility and honest unknowns

Light detail is explicit (`control: light`, `detail: 1`). Climate is an
independently negotiated family of existing Panel kind7. Supplementary detail
query/bind APIs leave the old Light codec and Panel-v1 Timer/Remote/Power
feature response unchanged. The dedicated Light tile callback captures
slot/card/revision together; it never consults a mutable current slot to
decide which profile was pressed.

Only actual domains and catalogues admit editing. Unknown Kelvin while a
light is off or in RGB mode is not a default temperature. Missing climate
step/unit cannot produce an editable target. Range-only and mode-only climate
devices retain their genuine observations and supported choices; the range
is not silently converted to a single target. Missing glyphs disable the
affected facet with a visible reason and working Back.

No generic hysteresis editor is implemented. Target step, actual low/high
range and hysteresis are different concepts. A provider-specific hysteresis
setting still requires a separately authorized mapping and its real bounds.
Existing RGB/range service cards and protected Player, Camera, Gallery and
Voice applications remain outside this change.

Device acceptance must use owned fixtures, original screenshots, the exact
immutable firmware identity and a batched performance/lifecycle comparison.
The real boiler and unrelated lights are not service-test fixtures.

## Current acceptance boundary

Native90c/HA111 passes real facet navigation and a held-input capability
revocation followed by a fresh reopen. Full acceptance remains incomplete:
one confirmed brightness command exposes unnecessary native invalidation
from the detail profile's restoration of dynamic value visibility. The
minimal90d correction leaves known/unknown value visibility with the normal
Light updater and suppresses an invisible disabled-color transition on the
two add-on buttons. The Scalar base-generation guard is unchanged. Actual
public-LVGL/Scalar reproduction precedes the required90d device rerun.
