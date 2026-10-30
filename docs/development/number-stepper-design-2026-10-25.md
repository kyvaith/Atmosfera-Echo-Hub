# W04 Number stepper — implemented contract and scoped acceptance

Current accepted deployment is native25/HA16 with clean layout10. Its new-GRANT
feedback reset has isolated Number HA/state/original-image acceptance, one
31-source-FPS Settings comparison and exact fixture cleanup. Native26 source
adds only the display separator described below; configuration/build/flash and
its own hardware language scenarios are pending. Earlier checkpoints retain
their original scope. See [current validation](validation-2026-10-25.md).

The opt-in contract is implemented locally in native23/HA14. Canonical checks
pass39 native tests/481 subtests,301 Python HA cases,209 Node editor cases and
full default-disabled product configuration. Native22 compilation, input audit,
OTA and one isolated0→0.25 step with paired HA state feedback and original-image
review passed. Native23 preserves that runtime and fixes only early boot locale
initialization; full build/input audit/OTA/ELF and60-second Home1 checks passed.
Original Polish Number open/close and Home4 review also passed with zero commands.

The user subsequently saved layout revision5; humidity6/Light7/card15 positions
were preserved during testing and the final six-field inverse Save to6. The
Number boundary campaign passed disabled endpoint contacts and1→0.75/−1→−0.75,
with two native commands, exact paired HA feedback and five reviewed originals.
The isolated Generic Light regression and two31-FPS Settings benchmark cycles
passed their own scopes. Four owned QA fixtures were removed after restoration.
Held unknown/domain-change interaction, audio, lifetime and physical GT911 remain
open; two stable-memory cycles do not establish broad performance acceptance.
The first diagnostic phase/context refusals and the Light quiescence-operator
failure remain retained. See [validation](validation-2026-10-25.md).

## Implementation phases

1. Refactor the existing native captured-view lifecycle without behavior change.
   A component-owned `ControlViewLifecycle` bridge owns the admitted, closing,
   close-cancel and overlay generations and the existing NAV admission logic.
   Scalar retains pixel buffers, workers, source leases and quiesce/resume hooks.
   Preserve the existing registered Scalar guard pointer and public forwarding
   entrypoints. Validate old Light behavior by full firmware build, flash,
   original screenshots, five open/close pairs and a truthful already-matched
   On no-op. A no-op must produce no HA actuator service and is not a physical
   Light success claim.
2. Deploy and verify the behavior-preserving HA shared-session refactor separately.
   Keep the existing Light codec, transport and saved layout unchanged. Preserve
   one service fence even while old requests finish after a view closes.
3. Add the explicitly negotiated Number protocol, adapter and native stepper.
   Reuse app6's existing labels and two buttons. No Number drag or hold-repeat
   belongs in this first slice. Validate on an explicitly configured HA numeric
   helper and the real display; do not infer that this fixes the unavailable
   Light's positive physical test.

## Negotiation and compatibility

- Add opt-in `entity_control_get_status`, `entity_control_bind` and
  `entity_control_update`, with raw `report_entity_control` reports.
- Generic wire type is `entity_control_v1`; capability lists
  `control_kinds: ["light", "number"]`.
- There is one connection mode, bound channel, HA session owner, native owner,
  active selection and ordinary pending command. Do not instantiate an owner
  or command queue per domain. A protocol/kind change cannot bypass the old
  outstanding HA service-task fence.
- Legacy `light_brightness_v1` and its API/action names remain exact fallback.
  New options default off in the reusable component.
- A saved v3 card explicitly chooses `control: "number"`. Initially only
  `input_number.*` is eligible. No implicit migration of ordinary tile actions;
  old or unsupported firmware shows Unsupported rather than a toggle fallback.

Generic selection identity includes `control_kind` alongside channel, open
sequence, slot, stable card ID, revision and selection token. Identity and schema
are validated before state or command handling. Codec/identity-field hooks must
preserve all existing legacy Light fixtures.

## Number data and commands

| Message | Number-specific fields |
| --- | --- |
| Grant/state snapshot | `state_seq`, `ttl_ms`, `title`, `domain`, nullable `index`, `available`, `value_text`, `state_generation` |
| Command, plus selection identity and `command_seq` | `op: "step"`, `direction: -1\|1`, `expected_index`, `expected_state_generation` |

`domain` is the canonical `numeric_steps_v1` descriptor implemented by
`numeric_domain.py`: decimal-string `min/max/step`, unit and maximum index.
The minimum anchors the lattice. A nonaligned maximum does not create an extra
short final step. Numeric zero is a real value and never means Off.

Bounds: absolute values at most 1e12, at most six fractional places and one
million complete intervals; units at most 32 UTF-8 bytes and value text at most
64. Payload remains at most 2048 UTF-8 bytes, fixed parser arena 4096 bytes and
output buffer 2049 bytes. Unknown, unavailable or off-grid values disable both
step inputs; they do not become index zero. A singleton range disables both ends.
Reject lossy conversion to HA's numeric service boundary.

### Optional native display separator (native26)

Number text-provider role15 is an optional decimal separator: the product
language packs provide quoted `.` for English and `,` for Polish. The native
view substitutes only an exact single comma supported by the active value font
with a non-placeholder glyph. Missing/invalid roles or missing glyphs retain
the canonical dot. Value, index, domain, generations, commands and wire text
remain canonical and are never parsed from the localized label.

The existing native LVGL label update owns a transient65-byte copy and glyph
descriptor on its calling task's stack. `lv_label_set_text` copies the result
synchronously; no new field, heap/pixel buffer, task, feature define, font asset,
protocol or public setter is introduced. The two translation registrations use
the existing332-of512-entry fixed pointer table. Existing refresh-text behavior
and the product's close-before-locale-change policy remain unchanged. Focused
host tests pass, including placeholder/missing glyph fallback, signed values,
refresh deduplication, Light restoration and canonical-wire refusal of commas.
Complete build and compiler-input audit, one OTA/full running identity and
PL0,25/EN0.25/PL0,25 original-image review now pass separately. The isolated
value remains0.25 with zero Number/provider commands, three distinct grants,
six released pointer ACKs and finalPL/closed ownership. One Settings cycle
retains31 source FPS/failed0 and releases its work buffers. These do not measure
peak stack, physical panel FPS, audio or lifetime. Locale fixture cleanup now
passes with fresh native unbinding, exact owned helper absence and restored
Home4/browser at layout12; see the current validation record.

The device captures selection, index and semantic generation on press. Release
produces at most one step command; endpoints, cancel and unchanged intent send
nothing. HA rechecks permission, current identity, live descriptor, expected
index and generation immediately before one absolute `input_number.set_value`.
No retry or inverse is inferred from timeout or a late result.

## Semantic generations and result ordering

`state_seq` orders messages and lease renewals. Number's separate token-scoped
`state_generation` advances only for real numeric index/availability changes.
An identical lease renewal or title update must not invalidate a valid tap.

Observe each HA entity event synchronously before existing task coalescing.
Value A→B→A advances generation twice even when only final A is sent. Metadata
A→B→A revokes the token at B. The native side cancels a pressed intent after a
real semantic, selection or generation change. Recheck after permission awaits;
do not introduce another task or per-entity cache to preserve these observations.

After dispatch, matching uses the captured target rather than reapplying its
pre-dispatch generation predicate to the command's own state change. HA sends
authoritative Number state before its terminal result. Native clears pending
only after applying the result's referenced `state_seq`. Older results cannot
acknowledge a newer selection or restore an old candidate.

## View, memory and acceptance

Number uses the same captured NAV/view bridge with a native LVGL participant.
It does not create Scalar requests, publish Numeric frames through the old byte
mailbox or start a second worker. Hiding a rail alone does not establish view
readiness or coherent snapshot ownership.

Reuse the existing hero label, state/unit label and On/Off button objects as
Number value/unit and minus/plus. The Light 112 font contains digits/percent
only, so product policy selects an existing fitting full-glyph font for Number
and restores Light's font/labels on kind change. Product owns geometry, text,
locale and colors; reusable code receives configured metadata. Refresh app6's
preview for the captured new selection/kind through the existing owner.

Budget: zero new pixel buffers, workers, caches or widgets. Native22 P4 DWARF
measures Component7152 bytes (+208 versus21), Scalar2696 and view bridge40
(unchanged). Static RAM is+608 bytes and flash+43184 versus21. These compiled
figures do not prove retained heap, leak behavior or runtime speed; the scoped
health samples and pending benchmark are recorded separately.

Required tests include legacy codec/API fixtures, renewal during press and
authorization, value/domain ABA, stale input, endpoints, unknown/off-grid,
duplicates, cross-kind service fencing, state-before-terminal order,
close/cancel/overlay capture and allocation bounds. Full compile, exact running
image, original PL/EN screenshots, hardware lifecycle and comparable performance
measurements remain required after runtime implementation.
