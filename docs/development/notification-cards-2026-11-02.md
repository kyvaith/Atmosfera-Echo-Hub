# Notification list: native62 / HA96

The typography, backdrop and cache repair is implemented and has passed automated
checks on the real device. This is not a fresh human acceptance of finger smoothness.
New-feature migration remains paused. No Git staging, commit or push was performed.

## Result

- Source/title/body fonts are18/24/20px; a two-line excerpt has20px bottom clearance.
- Rounded accent-derived cards float over a50% black scrim. The app behind the list
  is frozen; bottom-up is the close/back gesture. There are no pagination/close buttons.
- Covered active/bottom/top layers are isolated while the system layer owns the modal;
  their exact visibility and both LVGL DIRECT buffers are restored coherently.
- The scrim is cached once. Packed low bits restore the exact original RGB bytes;
  word processing speeds this operation without a second full-screen allocation.
- Four bounded card caches avoid rerasterizing labels on every scroll frame. Each
  card is captured directly into independent ARGB bands, with no whole-card scratch.
- Under fragmentation a preferred2-band card retries only its unpublished slot with
  smaller4/8-band allocations. Successful shapes are reused. Total-memory shortages
  and renderer/cache-sync errors keep the safe native fallback; the1MiB reserve stays.
- JPEG-only idle application previews may yield on one pressure retry. Home/raw,
  active app, close/work, compression and prefetch readers remain protected.

Ownership, layer lifetime, partial-publication and release rules are documented in
[notifications](../architecture/notifications.md). RGB888 DIRECT, two LVGL buffers,
three MIPI DSI buffers and the proven PPA image path remain. Generic RGB888 PPA
fill/blend handlers stay disabled. No audio pipeline or camera transport was changed.

## Verification

31 actual-LVGL host scenarios passed (`native-host62-r2.log`), including exact pixels,
odd widths, rounded corners, negative entry coordinates, context restoration, partial
failures,100-record traversal, gesture intent, stale IDs and deterministic release.
A forced300kB maximum allocation selects2 bands;100kB selects8 and retains4 ready
cards without allocation churn. The first62 host failure was a fixture limiting the
unrelated240kB backdrop; the corrected fixture applies pressure after base capture.
Five schema tests,13 preview-admission checks and the separate all-low-bit-pattern
round-trip test also passed. Earlier product814-pass/2-skip and JS397-pass runs are
historical evidence, not new runs of this final binary.

Full native ESP-IDF compilation,536 generated-source checks,208 ESPHome compilation
units/2311 commands, unchanged11959 shared SDK files, artifact preservation and exactly
one OTA for native62 passed. Canonical/frozen parity covered12209 files before final
Markdown updates. The deployed marker is `2026-11-02 23:00:52 +0100` and full ELF is
`f045ee4ac908c241c9b40d57ddc2993c41429358473c188d8c171948a83028a0`. Artifact manifest is `ac5d67fe2459b8003789db85deeb123440a6d1b0eba8064015a010688fb9de83`;
source manifest is `45a66a919ac4c46fe7557729a963fd5a2e5483cd0dc4a648211294c4a51754c4`. Recovery artifacts are under
`C:/aeh-build/native-context-v62`; sources under `C:/aeh-build/native62-sources`.

Two complete device cycles passed: Camera, Voice visual, Settings and Gallery,
8 application returns/18 screenshots. Every open had4 ready card caches and every
close released card/base/low-bit bytes. Warm Home remained4/4 on both cycles; the
first used an actual4-band slot despite a2-band preference, proving adaptive recovery
on hardware. Camera presentation counters increased [[68, 107], [182, 218]].
Gallery only reached its loading view; this does not establish photo decoding.
Voice checks were visual and do not establish acoustic/Sendspin continuity.

## Performance

Same native62 binary, same20 movement samples/mode after the application cycles:

| Mode | API median | API P95 | Manual loop wall cost / flush |
| --- | ---: | ---: | ---: |
| Cache off | 47.4ms | 66.8ms | 91.2ms |
| Cache on | 25.5ms | 61.5ms | 63.0ms |

These are response and render-work measurements, **not physical panel FPS**. The
manual loop aggregate also includes calls without a flush. Native58's cached wall
cost was about64.5ms; native62 is 63.0ms,
with the warm fallback defect removed. Matched preferred2/4-band costs were
64.0/66.5ms;
small extra draw cost buys fragmented-heap admission, without a large memory increase.
The normal product prefers2 and adapts only when necessary. All 21 sampled
DSI underrun counts were0. DMA state warnings are diagnostic records, not underruns.

Historical modal API medians: rejected51=168.5ms,52=137.1,53=101.9,54b=69.9,
55=70.5,58=32.4 and final62=22.0ms.
They describe the repair trend across different firmware, not a matched FPS comparison.
Native59's packed-RGB card experiment was slower (~76.7ms wall/flush) and was removed.
Native60/61 exposed smaller remaining fragmentation and were not accepted as final.

## Final state and limits

The own-record detail opened and one bottom-edge contact returned to the list while
keeping it open. Cleanup removed only18 exact owned IDs, preserved foreign/new records,
and verified subsequent UI requests still worked. Ephemeral HA authentication was revoked.
The final archive is empty, Home is visible, and modal/card/low-bit bytes are0.
Final Home:4845KiB free PSRAM, largest2880KiB;14KiB free internal heap. Eight original
preferences were verified, including PL, AEE2FF and Performance/Swipe logs off.
Runtime manual profiling is off; detailed profiler is compiled out.

HA96's41 installed files, original data/options hashes, layout298/16 cards and3 cameras
were preserved. There is no fresh human finger review, panel-FPS measurement, subframe
optical capture, real Gallery photo or acoustic playback acceptance. Home touch tests
use the full diagnostic product path; application-return cases use the navigation
delegate. A successful source/build test alone would not establish these device results.

Evidence: `C:/aeh-build/notification-cards-20261102/acceptance62.json`, full mode/cycle
reports beside it, and28 original device JPEGs with hashes. All observations and limits
belong to this native62/HA96 checkpoint. Resume from the top of
[resume-2026-10-31](resume-2026-10-31.md); do not repeat the old research or restart migration.
