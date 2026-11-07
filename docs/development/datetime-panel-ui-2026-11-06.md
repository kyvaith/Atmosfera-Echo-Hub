# Native date and time panel

The optional `datetime_controller` uses the existing entity-control application
(App6), owner, view lifecycle, and shared application snapshot buffer. Product
YAML supplies widgets, static geometry, translations and admission policy;
the reusable ESPHome owner validates the six-field tuple and all input fences.
It introduces no framebuffer, direct region, timer or worker.

The product opts in through `datetime_control_product_admitted`; upstream
`enabled` defaults to false and an omitted controller emits no datetime define.
The independently negotiated profile is `datetime:1` (bit64). Existing HA118
peers continue negotiating their previous five profiles.

## Widget and gesture ownership

One root contains overview and editing arrangements of the same six fields.
Only the fields admitted by date/time/combined mode are visible. A single
numeric keypad edits the selected field. The owner keeps the bounded draft;
LVGL labels are presentation, never the authority for submitted values.

The presenter stores49 widget references and small geometry/visibility flags.
The product creates63 ordinary objects (34 labels,22 buttons,4 SVG,3 roots).
Fonts reuse Roboto20/30/36. The calendar/timer glyphs reuse existing SVGs;
check/backspace use Google Material SVG paths normalized to supported commands.
These counts do not replace measurement of actual P4 static and heap costs.

The LVGL main task owns these widgets. Public pointer press/release captures
the current selection, source generation and draft revision. A consumed or
retired input cannot act on a replacement view. Leaving App6 retires the owner
and pointer capture through the existing lifecycle; no second close mechanism
is introduced. The bottom50 pixels remain clear for the normal upward close
gesture. Standard navigation owns snapshot creation and framebuffer handoff.

## Editing behavior

Selecting a field opens the keypad with its current digits. The first digit
replaces them; Backspace deletes one digit. +/- changes the active numeric
field within its valid range. Selecting another field accepts valid digits
locally, while an empty or out-of-range field stays visible for correction.
A calendar-invalid tuple such as31February remains editable and disables Save.

The optional check key accepts only the active field locally. Save also accepts
valid active digits atomically and sends one complete absolute tuple on release.
Cancel discards the local draft without closing the panel or sending a command.
Date-only/time-only fields remain null when absent; seconds are always retained.
No UTC conversion or date clamping occurs.

A semantic source change, including A-to-B-to-A, cancels a stale draft and held
Save. Changes to title, timezone or observation timestamp alone do not. The
observed HA tuple remains separate from pending values until confirmation.

## Geometry and validation boundaries

On the800x800 product, combined overview rows have centers y430/526; date-only
and time-only use y478. The keypad uses three columns and large numeric keys;
Save and Cancel sit above the reserved close-gesture region. Product coordinates
are declarative metadata; reusable C++ contains no product dimensions.

Focused public LVGL tests cover all modes, direct Save, invalid-date repair,
field switching, Cancel, external semantic changes, metadata hold, retirement
to the existing Light view, contrast, fit rejection, unchanged-state refresh,
and real profile query/bind messages. Separate source font checks use the actual
Roboto font files and verify Polish/English text and geometry. Host tests use
controlled display/font/SVG substitutes and do not prove hardware pixels,
presentation FPS, DSI ownership or sound. Full native firmware and physical
device acceptance must be recorded separately before calling this feature done.
