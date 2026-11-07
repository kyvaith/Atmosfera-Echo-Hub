# Select/input_select — bounded choice control under implementation

Status: **first bounded slice installed and accepted**, HA31/native35,
original cards restored at layout58. This does not close pagination, arbitrary
fonts, physical GT911, audio or long-duration acceptance. Existing controls
retain their previous owner, display lifecycle and compatibility.

Update during continuous work: HA31 and native34 are installed and separately
identified. The shared owner, five native Apply commands and actual HA states,
stale-contact suppression, 1/8/9-option limits, unavailable glyph, browser
review/Undo and cleanup have device evidence in `choice-v4`; settled revoked
frames and warm Choice/Light cycles are in `choice-v5`. Existing Light opens
with a ready Scalar and no Light services. Warm Choice cycles0..3 hold
7101KiB free; Light cycles remain7096..7102KiB with largest2240KiB unchanged.
Before/after normal Settings routes are54/55FPS, failed0. Physical GT911,
audio and long lifetime are separate open gates.

Native35 corrects the product current-option header with DOT instead of center
CLIP at the extreme32-wide-character value. `choice-v6` passes actual Apply,
exact HA value, original-image review and cleanup. The highlighted option wraps
the full value; service bytes remain exact. Frozen35 reuses the identical
immutable native34 fork. Its config, full firmware build, source audit, preserved
artifacts, OTA and actual running ELF are separately verified.

`choice-v8` also uses the actual `select` domain: the device language changes
PL→EN→PL, confirmed by native preference reports and original picker images.
The existing `ui_set_locale_safely` deliberately revokes and closes app6 before
changing locale; reopen reads the new current selection. This path is actual
preference application, not a retained terminal-result acknowledgement from the
retired session. The earlier v7 harness incorrectly required that session to
survive; its failure and successful restoration remain preserved.

## Ownership and limits

Extend the existing generic session owner and application6, not a new owner,
application, task or raw framebuffer. HA owns the option catalogue, exact values,
live permissions, selection lease, dispatch fence and authoritative observation.
The native owner holds one bounded current/candidate selection. Existing NAV,
snapshot pool and renderer lifecycle own the display handoff.

Initial eligibility is explicit v3 `control: choice` on an Entity card targeting
select/input_select. The complete options array must have 1..8 distinct,
nonempty printable strings, each at most32 UTF-8 bytes. Reject malformed,
oversized or unsupported lists completely; never silently truncate, rewrite,
deduplicate or clip a value sent to a service. Unknown/unavailable, absent or
off-list current state is unknown, not option0. A single option is valid but
cannot issue a redundant change.
The complete list also excludes the exact reserved state strings `unknown` and
`unavailable`: selecting them could never receive known-state confirmation under
this control contract. Differently capitalized ordinary option labels stay exact.

This first slice uses existing app6 with a bounded native set of eight M3
option buttons and one explicit Apply button, allocated once. Candidate taps
only choose locally. Apply emits at most one absolute choice, never a service
per preview change. Selected/current distinction and pending/error feedback
must be visible and translated. The existing accent and contrast policy colors
the controls. Long labels clip only visually; canonical identity stays exact.
No raw image cache is allocated per option or per entity.

## Protocol and stale data

An opt-in native feature advertises an additional generic `choice` kind. Old
light/number capability lists and legacy Light codec remain accepted without
gaining choice support. Saved choice cards stay passive on older firmware;
they cannot fall back to a toggle. New reusable configuration defaults off.

Choice grant/state carries a complete bounded `options` array, nullable current
index, availability and monotonic semantic state generation. Existing token,
open sequence, channel, card identity/revision, state sequence and lease remain
mandatory. Maximum wire size remains2048 bytes; fixed parser/output memory
must be checked against worst-case UTF-8/escaping before enabling the feature.

Apply captures selected target index, observed current index and semantic
generation. HA rechecks them and the exact list again after authorization and
immediately before the existing single service fence. An option-list mutation
revokes an opening/active selection even if it changes A→B→A. State A→B→A
increments generation twice. A held/released old candidate cannot be revived
by lease renewal, reconnected transport, reordered state or changed capability.
Unknown data disables Apply, without inventing an index. Service acceptance and
matching HA state remain distinct from physical actuation.

## Delivery sequence and acceptance

1. Pure exact option domain and focused rejection tests, without deployment.
2. Extend both generic codecs/session owners and negotiation, preserving old
   golden cases. Verify bound sizes, stale list/state ABA, pending/close and
   failed authorization/service behavior.
3. Native fixed widgets and product text/theme/lifecycle registration; keep
   scalar and Light/Number regressions intact. Configuration + focused tests.
4. Freeze exact sources, compile native ESP-IDF image, audit inputs, flash once
   and verify actual running identity.
5. Owned real input_select: open/cancel with zero services, choose without
   dispatch, Apply with exactly one select_option and matching state, no-op,
   list/current changes while held, unavailable and cleanup. Review original
   screenshots, normal Home/Settings responsiveness, memory, display errors
   and existing Light/Number behavior. Preserve user layout and preferences.

Only accepted slices update the roadmap's implementation status. No GitHub
publication or commit is authorized for this continuation.
