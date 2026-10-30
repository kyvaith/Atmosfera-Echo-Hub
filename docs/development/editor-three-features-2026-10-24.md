# First three editor features — 2026-10-24

Local implementation on `feature/ha-dashboard-2026-10-24`. These are bounded
increments of CFG-010, CFG-012 and CFG-020, not completion of their entire
feature families. See the [implementation plan](implementation-plan-2026-10-24.md)
and [feature registry](feature-roadmap-2026-10-24.md).

The [live HA record](live-ha-deployment-2026-10-24.md) tracks subsequent real
deployment and the HTTP-only UUID defect found there. The version/test/package
counts below describe the preserved original dev1 increment.

## Implemented behavior

| Feature | Result |
| --- | --- |
| Copy one card | Copy in properties, select an empty compatible place on either editable page, then paste. Each paste creates a new ID and independently copies the action data. One undo removes that paste. Copying does not save or execute an action. |
| Delivery readout | Show saved, sent and received revisions plus snapshot-cache readiness. Pending off-screen places are normal; offline, an older revision or absent telemetry cannot claim current readiness. Physical Applied remains unconfirmed. |
| Profile and limits | A collapsed profile panel shows its resolution, total/editable/reserved places and pages, and explicit capability flags. This is the HA layout definition, not a detected firmware version or a native capability probe. |

English and Polish strings cover the new controls. Copy/paste also has
Ctrl/Cmd+C/V handlers. Text fields retain normal browser copy/paste. The
clipboard is bounded to one card, remains in editor memory and is invalidated
when the user, device, profile or component lifecycle changes. It is not written
to the OS clipboard, local storage or backup. Occupied places, including hidden
cards, are never overwritten by paste.

The review also fixed an existing asynchronous race: a poll begun before Save
or Reload could finish afterward and replace the newer saved layout with an
older clean draft. Transaction invalidation, request ordering and revision
guards now reject that response and its late error.

## Ownership and compatibility

The frontend owns the one-card clipboard and readouts. The HA options/model
remain authoritative; normal Save still validates the complete document and
uses `expected_revision`. The layout stays version 2 and the native projection
stays version 1. No firmware component, worker, framebuffer, timer or allocation
policy changes in this increment.

Integration and asset cache version: `0.4.0.dev1`. The local deterministic package
contains the same seventeen allow-listed integration source files. Previous
packages are preserved. Installation requires an authenticated HA session and
access to its configuration directory; host tests do not establish deployment.

## Validation

Evidence root: `C:\aeh-build\feature-research-20261024`.

- **61 editor tests pass**, including independent action clones, fresh IDs,
  atomic refusal, one undo, context changes, malformed/old/offline telemetry,
  unchanged-status DOM stability and three delayed poll/transaction regressions.
- **112 Python model/HA-adapter tests pass**; these use narrow HA shims.
- Independent source review, JavaScript syntax and scoped whitespace checks pass.
- Browser mock: copy slot 2 to an emptied slot 15 across pages, undo/redo,
  explicit Save and new-ID readback. Ready/pending/stale/offline/legacy cases
  were observed separately. English/Polish profile and a 390×620 iframe viewport
  were inspected. This is synthetic HA, not a real mobile touch device.
- Modified-key automation did not trigger the Ctrl+C handler although unmodified
  ArrowRight navigation worked. Shortcut logic has host-test evidence only;
  browser button copy/paste succeeded. No physical-keyboard claim is made.

The saved mock layout is retained as `editor-three-copied-layout-final.json`.
Source `fixture-2` remains at slot 2; its clone at slot 15 has a new ID and all
other configuration fields match. The guarded device demonstration and cleanup
have their own reports, separate from HA deployment acceptance.

First device attempt `editor-three-device-copy-v1` remains **failed**: the test
incorrectly required native RGB values to equal HA preview RGB. The existing
native contract owns actual colors through palette roles and the selected
accent. Source/copy semantic fields and native colors matched each other, but
preview/native RGB differed. No sticky device fault occurred, and the original
presentation and logging were restored. A corrected test must preserve this
normalization boundary and the failed evidence rather than change the firmware
to satisfy a preview assertion.

The corrected `editor-three-device-copy-v2` campaign passed its machine checks
on the unchanged v7 ELF
`5ae1454fdf2f1d6354d78803a9afee9f8a9ac6f8ea6fff8066d0644dde956c72`.
It retained source ID at slot 2 and the new copy ID at slot 15, verified native
source/copy equality except ID/slot, used three adjacent acknowledged listener
swipes and captured both pages after their visual/context masks were ready.
The fixture was active for 14.17 seconds. There were zero tile taps, zero observed
native service reports, no sticky fault, no budget expiry and no cleanup errors;
original presentation and independently owned logging were restored.

Both original 800×800 screenshots were inspected:

| Capture | SHA-256 | Review |
| --- | --- | --- |
| `editor-three-device-copy-v2/editor-copy-page2.jpg` | `0cbb720dc71c91eb85824fc5e145ca80229eecc752c72b470ceb1bd8e0dadca0` | Original card, correct text and light-background/dark-text colors |
| `editor-three-device-copy-v2/editor-copy-page4.jpg` | `b1bfe5c8e4039cde42a956737d51972428dd31923032228d7c167d52ca9ad421` | Copy present with matching content/colors; long wrapped title overlaps icon in the existing compact template |

This is **not a clean general visual acceptance**. Compact template title/value
bands need bounded text geometry; a scene's ISO timestamp also wraps into its
title. Those pre-existing presentation limitations are exposed by this fixture
and remain a separate firmware task. Existing HA preview RGB and native pastel
RGB also differ; this increment does not claim pixel-identical preview.
The machine pass does not establish physical touch, audio or FPS behavior.

`editor-three-cleanup-oneboot/single-clean-warm-boot-report.json` records one
controlled restart, exact retained v7 ELF, 30 seconds of uninterrupted boot
health, two clean presentation exports and all five diagnostic preferences
unchanged. No configuration or preference writes occurred in that cleanup.
Its original Home1 screenshot was inspected. This is a warm software reset,
not a physical cold-start campaign.

## Reproducible source and package

| Artifact | SHA-256 |
| --- | --- |
| `www/tile-editor.js` | `983183b26a98ec4b2a1c270e60cb6d9c3652d717d2844bd2880fb1669f5f534f` |
| `tools/tests/test_tile_editor.js` | `1a23d5148df52483af75b364a38edd8355ab470a6df88a87b043ad331873e2f4` |
| `ha-integration-package-v3/atmosfera_echo_hub-0.4.0.dev1.zip` | `1c3f51db04aaf81872d2e72e70a219567be9af522368dd1905041e9962fe7c4d` |

ZIP: 239107 bytes, 17 members, deterministic rebuild and CRC/source equality
verified. No credentials, runtime options, logs or QA fixtures are included.
This is a local development snapshot; no commit or push was performed.

## Remaining acceptance

Real HA installation, integration reload/import and execution through the
installed sidebar panel remain unverified. The HA browser requires login; SMB
configuration access is unavailable and existing SSH authorization was refused.
The package is ready for deployment after those access requirements are met.
Multi-card selection/cut/paste, runtime pages, dynamic native controls and a
physical presentation ACK remain separate work.
