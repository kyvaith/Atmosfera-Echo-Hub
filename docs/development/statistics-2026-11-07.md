# Hourly statistics: firmware115 and HA128/129

## Scope

An explicit sensor card action opens a read-only view of the last 24 completed
UTC hours: arithmetic mean and minimum–maximum. Existing Info cards retain
their action. Statistics uses the existing Info owner and App6 lifecycle, one
childless vector draw surface, and no additional full-screen framebuffer, timer
or task. Recorder data is read through Home Assistant; the device receives a
bounded, quantized series and labels.

## Firmware115 evidence (7 November)

- Full native ESP-IDF build and configuration validation passed. Source manifest:
  `C:/aeh-build/notification-cards-20261102/source-v115-build.json`, SHA256
  `d28c16063906318e9407797fc5b7e445ce3a4639951a342705d6ddb999868eb4`.
- ELF SHA256:
  `a446ef88ab7bb9c99a46ae2da8efcb5dfff67d8b94441ab58d13ca3e51e1f161`.
  Artifact manifest: `D:/aeh-build/native-context-v115/manifest.json`, SHA256
  `b0326304af6b93ab441090b4d51b761df3f8cf37a09796db4909a2fb6862ba3d`.
- Linked verification passed in
  `C:/aeh-build/blue-flash-20261107/native115-final-link/report.json`.
  Actual P4 sizes: Statistics356, Snapshot728, Message960, Owner1184,
  Codec5152 bytes; codec arena remains5120 bytes. Static RAM is311838 bytes,
  an increase of184 over114; image size8709106 bytes, increase27726.
- One OTA attempt succeeded. The first boot transmitted all230399 startup PCM
  frames and maintained wake readiness for36.007 seconds, with zero DSI events,
  crash or rollback. This is **not a strict clean boot**: the known pre-chime
  mixer allocation recovery and one owned Sendspin protocol-task retry occurred.
  Digital transmission was observed; acoustic listening was not performed.
  Original receipt: `C:/aeh-build/blue-flash-20261107/native115-firstboot/first-boot.json`.

## Device and editor observations

The existing slot13 Info card was temporarily changed by revision-checked CAS
to Statistics for the real `sensor.tp_link_router_cpu_used`. Revision399 became
400; after testing, the exact original card was restored at revision401.
There were no provider commands, Recorder mutations or unrelated layout edits.

`C:/aeh-build/blue-flash-20261107/statistics115-cpu-first/report.json` records two
opens, two standard bottom-edge closes and three original device JPEGs. Both
opens returned ready with all24 hourly aggregates present. Root inspected both
graph images and final Home: graph, axes, dates and zone were visible, with no
clipping or stale plot on Home. UART contained no DSI event or hard fault.
This uses injected device contacts; physical touch and long-term operation are
separate acceptance boundaries.

The comparable Home/Settings route is in
`C:/aeh-build/blue-flash-20261107/interaction115-first/report.json`: eight Home
swipes, two Settings cycles, the existing scroll benchmark and three original
JPEGs. There were zero DSI events or hard faults. Settings remained54 FPS.
Root inspected Home5, Settings and final Home1; weather and clock remained
visible. Motion counters describe compositor timing, not camera-measured scanout.

Actual HA128 testing found two remaining integration issues before acceptance:

1. Measurement sensors using Core string-enum units (including demo temperature)
   were omitted from Statistics qualification despite available arithmetic
   Recorder metadata. Core sources were retrieved read-only for diagnosis.
2. The inspector showed the saved Statistics action as “Bez działania” and
   repeated its explanation, even though the card and device opened Statistics.

## HA129 and final acceptance

HA129 was installed with one requested/completed HA restart and no layout,
provider, configuration or Recorder writes. Its three changed runtime files
normalize existing string subclasses, repair the saved Statistics selection and
single hint, and update the version. The fresh live discovery qualified the
owned-demo temperature sensor and the real temperature sources. The earlier
HA128 failure is preserved; no encoding defect was present.

`C:/aeh-build/blue-flash-20261107/statistics115-demo-ha129-first/report.json`
records two further opens/closes and three original JPEGs for the owned-demo
temperature sensor. All24 completed-hour values were present. Root reviewed all
three images: correct degree unit, flat15.6-degree line, readable labels and
restored Home; no DSI event, hard fault or provider command. The temporary card
was restored at revision403. Physical lamp or thermostat actions were not used.

The browser showed the saved Statistics choice and exactly one explanation.
Info remained available under its translated label “Otwórz widok informacyjny”.
A root inspection filter initially omitted that label; this was not an Info
availability defect and caused no patch. The actual Info→Statistics review,
draft and Undo workflow passed. Save returned to disabled and the editor showed
all changes saved; no browser layout write was performed.

The Home median was37.5 FPS in both114 and115; Settings remained79 frames/54 FPS.
Two larger individual Home frame times (97.725/98.279ms) and one107.313ms loop
sample remain recorded. The old and new batches used different weather scenes;
these are not sufficient evidence to attribute the peaks to Statistics or to
claim every latency regression resolved.

The same-firmware comparison in
`C:/aeh-build/blue-flash-20261107/weather115-memory-first/report.json` measured:

| Retained scene | Free PSRAM bytes | Free internal bytes |
| --- | ---: | ---: |
| Actual partly-cloudy-day | 4052156 | 8075 |
| Temporary clear-night | 4877832 | 21747 |
| Restored actual partly-cloudy-day | 4052288 | 8047 |

Changing only the weather freed825676/13672 bytes and returning restored the
initial level within+132/−28 bytes. Named frame/cache buffers remained unchanged;
the difference was in residual scene memory. This supports the animation-scene
explanation, not an exact accounting of all ThorVG allocations. Largest free
PSRAM block changed from2162688 to1605632 bytes during the pair, so fragmentation
and total free memory remain separate measurements.

The weather helper retains **STOPPED_ERROR_NO_RETRY**: after requesting Settings
to restore logging policy, its first observation saw transitional app0/nav1 and
asserted too early. Its bounded cleanup restored live weather and Home. The
separate read-only final observer
`C:/aeh-build/blue-flash-20261107/weather115-final-health-first/report.json`
confirmed coherent Home1, unchanged preferences,230399 transmitted frames,
amplifier/wake ready and zero DSI/hard faults. Root reviewed its original Home
JPEG. This does not relabel the original helper failure as passed.

The24 firmware source/test files and19 HA source/test/fixture files were adopted
after exact preimage checks and backups. Receipts:
`C:/aeh-build/blue-flash-20261107/canonical115-firmware-adoption/report.json` and
`C:/aeh-build/blue-flash-20261107/ha129-canonical-adoption/report.json`.
Unrelated dirty work and unchanged CRLF files were preserved. Nothing was
committed or pushed. The next small display-copy improvements are prepared
offline for a subsequent useful feature batch, not a standalone cosmetic OTA.

## HA130 editor cache-version follow-up

The broader existing Action suite found that HA129's manifest version had
advanced while `PANEL_ASSET_VERSION` still said128. The tested JS itself was
correct, but the URL could retain a stale client cache. HA130 changes only
`panel.py` and `manifest.json`, both to130; the86-file package otherwise retains
exact HA129 bytes. The focused existing version-consistency test passes.

One HA restart was requested and completed. The initial observer failed on
`KeyError: panel_extra_profiles` during transient startup, so
`ha130-deployment-first/report.json` remains FAILED. A separate read-only check,
`ha130-reconciliation-first/report.json`, passed without another restart:
loaded version130, exact versioned module URL and served JavaScript hash,
native115/layout403 identity, provider, configuration and protected preimages.
Its SHA is `1f25b50278e917ccf29455319b3879e62ed7ae812ad13cd35104cccced097f0d`.
The two source files were then adopted with backups and exact preimage checks:
`ha130-canonical-adoption/report.json`, SHA
`d482e7f3b529d5cdfb83c60e66940d636b7eb9830b8c238db9d073da72b259c2`.
No new firmware was needed for this cache-version correction.
