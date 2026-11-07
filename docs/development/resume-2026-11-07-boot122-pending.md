# Boot/audio repair checkpoint — 7 November 2026

Recorded at 21:15 Europe/Warsaw. This is a pending-work checkpoint, not acceptance of a new firmware. Recheck live identity before any device write.

## Confirmed result

Deployed candidate native120 passed one clean USB first boot and five controlled software restarts. Each of the five cycles transmitted the complete startup and confirmation audio, started wake-word detection, and produced an original Home screenshot. The user confirmed: “Tak, po wszystkich pięciu oba dźwięki były poprawne”. This physical confirmation applies only to native120.

- Device last verified: `192.168.88.82`, ESP32-P4 MAC `30:ed:a0:e2:0b:cd`, COM5 CH343 serial `5AB0165731`.
- Native120 ELF: `04f2cbe6a4be33f5660925b37d5703f50af993a83a55cd5e4c2fd2bbcace5226`.
- Artifact: `C:/aeh-build/native-context-v120/manifest.json`, SHA256 `5cc849d8718e4be5319916b39214f8994421069b340ace6034070e73db3cd87a`.
- Closed six-boot audit: `C:/aeh-build/boot-audio-20261107/audit/native120-six-boot-campaign-review.json`, SHA256 `33afe1cd0a03e1bc220f2f4e0d8eb1a056886930198208b2fede0f567aa0951d`.
- User listening record: `C:/aeh-build/boot-audio-20261107/native120-listening-user-confirmation.json`, SHA256 `f90921b5d48807b41e5ce09d1fa25f44fccd84f1555e09015c9f8aa8c24bf4be`.

The bounded native120 Home/Settings route recorded median Home compositor 38 FPS and Settings 55 FPS (reference117: 37.5 and 54). These are matched-route observations, not physical scanout FPS or proof of equal RAM usage. Its three original screenshots were reviewed. No DSI diagnostic event or hard fault appeared in those closed windows.

## Remaining image-memory problem

The subsequent Gallery test failed a contiguous JPEG allocation: 2,976,768 bytes needed versus a largest free block of 2,949,120 bytes. Player also failed a 1,280,000-byte pool allocation. Preserve `native120-artwork-v2/report.json` and its UART as FAILED. A separate continuation captured the existing Player placeholder and returned Home; it did not prove fresh image decoding.

Native121 moved the existing encoded-image inputs to their full initial capacities (262,144 and 786,432 bytes in PSRAM). This avoids two later relocations, but its effect on fragmentation is not established on hardware. Its first compile was stopped by an overly strict monitor classifying a CMake compiler probe as a parallel build. The corrected native121b compile was then deliberately stopped after source review found an independent deterministic bug; neither candidate121 attempt produced an accepted firmware or a device upload.

The deterministic bug: Settings releases its 3,657,600-byte loan, but the image component retains that reservation minimum. A later 3,145,728-byte Gallery reservation is allocated successfully and then rejected by the spare-buffer admission rule. A host test using ten actual component methods reproduces this even with an always-successful allocator. This is separate from native120's first allocation failure.

## Candidate122

Candidate122 retains the 118/120 boot-readiness and external-input placement changes plus 121's full initial encoded reservation. It adds only a reset of the released decode-pool reservation to minimum0/count1 before the existing cleanup. Active images, an in-progress decode, pinned retired generations and outstanding external loans retain their ownership. No new task or permanent image buffer is added. The failed119 scheduler experiment is excluded.

Four focused lifecycle cases passed with eleven allocations and eleven releases; the old121 implementation fails the smaller-reservation case. Full native compilation and all122 hardware verification remain pending. Actual P4 translation-unit compilation for the122 delta was not run because of disk pressure.

Reviewed isolated changes: `C:/aeh-build/boot-audio-20261107/audit/artwork122/manifest.json`, SHA256 `6853cc963f0c16884e173e8289a1b04d588bbb218ad98739c96425575adcf3f0`. Test report SHA256 `1f0fd3d4fad4403af2d53cdfab8df236199fa118a6641955dae48a68d13b89db`.

Source parent is frozen121 (`source-v121-build.json`, SHA256 `1e9bdb84cfcab4e51aa65a72717ba39eb958848d0ab65794a56547d521762d26`), but the live predecessor remains120. Do not confuse these identities. Do not run121 flash/adoption helpers.

## Resume steps

1. C: had about270 MB free. A request to free at least1 GB is pending. Preserve all original failed reports and the already verified120 artifact; do not repeat the earlier rejected archive relocation/removal.
2. Root and peer source reviews of the122 preparation and device adapters passed. Root ran the read-only preparation check: source/dependency/SDK/previous-failure guards passed; it stopped at disk allowance, 269,766,656 available versus 428,807,816 bytes required. No122 preparation, build or upload has run at this checkpoint. Planned source/artifact locations are `C:/aeh-build/native122-sources` and `C:/aeh-build/native-context-v122`.
3. Validate configuration, compile the full firmware serially, and verify generated/linked inputs and the retained artifact. The compiler-probe exception must be narrow; real Ninja builds use `-j1`, with both parallel-build environment limits set to1.
4. One root operator owns USB/network/upload. Perform one OTA from the rechecked120 identity, record strict first-boot audio/wake evidence, and reject resource retries or startup faults.
5. Run the matched Home/Settings route, then Gallery pool reservation plus fresh decode and increasing presented-frame count, then Player pool checks and original screenshots. On Gallery failure, preserve FAIL, close the owned Gallery once, return Home and diagnose before further restart cycles.
6. Only after that scenario passes, run five122 restart/audio cycles and obtain a new physical listening confirmation. The user's120 answer cannot qualify122.
7. Adopt only the final reviewed firmware delta into both canonical repositories, retaining unrelated dirty work. Update final architecture/validation/checkpoint documents. No commit or push is authorized; no shutdown is requested.

Canonical runtime source remains the117 checkpoint with HA131/layout410; boot candidates are isolated and have not been adopted. Existing feature state is documented in [resume-2026-11-07-actionparams117.md](resume-2026-11-07-actionparams117.md). No HA/provider/layout change or new feature work is part of this repair stage.

## Prepared122 tools

All paths below are relative to `C:/aeh-build/boot-audio-20261107/`. Device helpers have had source review only; run their prerequisite checks against the actual future122 build and reports before execution.

| File | SHA256 |
| --- | --- |
| `prepare122.py` | `24d7f8901a17ce4cbfc22334c66e0e49cf65b3415e141e60adbfd39fe5193d8d` |
| `delivery122.json` | `46d819be9510f4a5f199d9e7ec53734e6fa831e143b9fef8b7891822820fd43d` |
| `audit_native122_inputs.template.py` | `91e372938bc2100805655de89df20c4eb963bea00225aefe91a5209850f954a7` |
| `audit/strict122_observer.py` | `6946b9974d800968a2fccc7d1be6fe24df555551c79ceb4afda0fcd97d9f117b` |
| `panel_flash122.py` | `de757b313d5f1a42bb60021e93602e587382dc4ceeead99796878f60aacc30e4` |
| `restart122.py` | `8237936d118b2e2ffb3902f4f11e7a1f294bca7cbb1dfc3022df23990debd398` |
| `interaction122.py` | `3ec35d8011974ea4e7d158f4870fc22f413e172299a510557e96df4a67bb8da1` |
| `artwork122_device_route.py` | `c286887139cc4d9d14a06686c23dfdd9644c64d5e49203ed73defdbae3cce167` |

Use `C:/aeh-build/upstream-sync-20261022/.venv/Scripts/python.exe` with `-X utf8 -B`. Preparation requires the previous120 artifact SHA, delivery path/SHA and audit template path/SHA from this checkpoint. Its default is read-only; only after a successful current preflight add `--execute --compile`. The new receipt is `prepare122-receipt.json`. Run each restart separately, reviewing its closed report and original screenshot before the next cycle.

Final adoption still needs an updated helper composing118+120+121+122 over the exact canonical117 preimages (including two new lifecycle-test files). Do not use the old121 adoption helper. Final architecture documentation must reconcile obsolete claims of a permanently retained Gallery/Settings arena with the current per-session release contract; the122 change also ends its numeric reservation.
