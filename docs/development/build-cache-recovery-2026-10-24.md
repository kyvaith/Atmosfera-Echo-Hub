# Local build-cache recovery — 2026-10-24

Only old generated/downloaded build caches were pruned or archived. Neither Git
checkout, its unpushed changes, frozen product/fork source tree, current v9/v10 inputs,
nor preserved native checkpoint was removed. This is local evidence maintenance,
not a repository publication.

## Compiled caches

The root verified resolved absolute paths, absence of reparse points and current
SDK activity before operating on these exact old build trees:

- `D:\aeh-build\feature-research-20261024\firmware\build` (v7).
- `D:\aeh-build\feature-research-20261024\firmware-v8\build`.
- `D:\aeh-build\lvgl-ram-regression-20261022\firmware\build`.
- `D:\aeh-build\upstream-sync-20261022\firmware-idf556\build`.

The recorded plan admitted only `.o`, `.obj`, `.a` and `.d` compiled files inside
those build roots. 10,130 files / 3,113,231,990 logical bytes were removed.
Every build ELF matched its independent preserved checkpoint before pruning;
noncompiled outputs were checked afterwards. No source in the active host-test
toolchain or current proposals was pruned.

The initial v7/v8 preflight stopped before deletion because the inventory omitted
one generated dummy object in each tree. Those unlisted objects were retained.
The completed deletion's post-check then stopped because a loose `sdkconfig`
filename match had incorrectly also classified one planned `.obj` as retained.
Independent reconciliation verified every planned deletion and all retained
outputs. Original audit and failure evidence remain; these are not hidden
retries or lost ELF artifacts.

## Recoverable v8 SDK and build cache

After object pruning, the old v8 `build` directory and all its
`managed_components` children except `bblanchon__arduinojson` were archived.
The active native host harnesses still use that exact ArduinoJson path; it and
the v8 `src` and project files remain expanded. Current v9 cache remains intact.

Recovery files are private local artifacts beneath
`C:\aeh-build\feature-wave2-20261024\cache-inventory-v10`:

- `old-v8-sdk-build-recovery.zip`: 393,499,662 bytes; SHA256
  `a03f2cf0d2128b976774024e76968210221ed98309960852048fa680955067fe`.
- `old-v8-sdk-build-recovery.json`: exact original paths, archive members, sizes
  and per-file SHA256; manifest SHA256
  `c3dfcfa7b79ee9611a5415a43888c7a407053302e968642158ee78be5f65fe89`.
- `old-v8-sdk-build-recovery-complete.json`: final completion and retained-source
  verification, including the original partial-removal qualification.

All 12,100 ZIP members were decompressed and hash-compared to their sources
before removal. The original recursive PowerShell removal stopped on an empty
exFAT directory. Completion checked every remaining file against the same
immutable manifest, then removed exact files and empty directories bottom-up.
All 176 retained active-library/checkpoint file hashes were unchanged.

To deliberately rerun a historical v8 build-path audit, first verify the ZIP and
manifest hashes above, then restore its named `build/` and `managed_components/`
members beneath `D:\aeh-build\feature-research-20261024\firmware-v8`. Inspect
existing targets before restoration. Historical reports still describe their
original paths and do not imply those cache directories remain expanded.

## V10 host ENOSPC and explicit retry

The first v10 compile ran from 16:26:19 to 16:30:58 UTC and exited with code 1.
`v10-compile.log` records assembler failures writing LVGL/ThorVG object files:
`No space left on device`, followed by Ninja stopping. This was a host storage
failure. The failed attempt and its process record remain unchanged; it was not
relabelled as a successful build.

Root then relocated only the old generated download cache at
`D:\aeh-build\feature-research-20261024\product-v8\.esphome\.espressif` to
`C:\Users\kyvai\Archive\atmosfera-build-cache-20261024\product-v8-espressif`.
This recoverable move retained all 11,932 files / 541,301,940 logical bytes. Before
each file move, its SHA256 was read at the source; the destination hash had to
match and the original file had to be absent before the journal recorded that
move. Empty source directories remain. Neither current v9/v10 source or SDK
inputs nor preserved native artifacts were moved. Plain SDK `.git` pointer files
were retained as ordinary bytes; no Git directory or pointer was followed.

The private evidence directory remains
`C:\aeh-build\feature-wave2-20261024\cache-inventory-v10`:

- `v8-download-cache-archive-plan.json`: exact source/destination and original
  file lengths; SHA256
  `e92e30b53481443251527781359f7fabdb6af78e6a4d2ccc847da69b044bf978`.
- `v8-download-cache-archive-moves.jsonl`: 11,932 unique original/destination
  records with per-file bytes and verified SHA256; journal SHA256
  `51e20b9c1284bad07f3168300bdfeae41220a64df5b9363d38161d9ebe8a489c`.
- `v8-download-cache-archive-complete.json`: original completion at 16:32:19 UTC;
  SHA256 `2ba6e019a7f5e60c56fc878b2c02dc2c788b1c4aabf9b7b50377028ba85fc798`.
- `v8-download-cache-archive-independent-verification.json`: all moved file
  hashes independently verified at 16:37:55 UTC, with the correct byte total;
  SHA256 `9fbde04c058507fd07dc2958e3c73b0bee13c687576a9ec8f4db11d1d5aba9f3`.

The original completion incorrectly reports `logical_bytes:11932.0`: PowerShell
read the `FileInfo` array's `.Length`, rather than summing individual file
lengths. Its per-file journal lengths/hashes are correct. The separate
independent record supplies 541,301,940 bytes without overwriting that completion.
Reconciliation of the plan and journal also gives 11,932 records and the same
541,301,940-byte sum. The completion's free-space readings were D: 3,497,263,104
bytes and C: 2,703,544,320 bytes; these are historical readings at completion,
not current capacity guarantees.

Retry1 was explicit, with a new `v10-compile-retry1.log` and process record. It ran
from 16:33:14 to 16:38:30 UTC and exited with code 0. Both process records name the
same immutable source-manifest SHA256
`833d5ec45e7775d08ff6794f260fa0a179f1ece57075a7f3b965a955c97df016`.
No source change or new source version was used to solve the host failure.
The two retained log hashes distinguish the attempts:

- first failed log: `9f027f6d6801899c16a21c7ac0e4433b9cab837aa1c5c3ce99361f07290d8835`;
- successful retry1 log: `334d9e55653be02ea358adeb394031f33eec8413292ddbbad5c990c4ea0dcbbd`.

Both records retain TLS verification and process-only CA-bundle scope, with
ccache disabled. The separate retry1 preservation helper admits the retry log's
exact path/hash; it does not overwrite the first log or relax source/artifact
guards. Compilation success is separate from later flash, runtime and visual
acceptance, recorded in the relevant validation documents.

## Storage layout

At this checkpoint D: is exFAT with 262,144-byte allocation units; C: is NTFS with
4096-byte units. The v10 frozen sources contain only about 50 MiB of logical data,
but thousands of small files consume several GiB on D:. For the moved download
cache, summing `ceil(file_length/262144)*262144` from the journal gives
3,487,563,776 estimated allocated bytes for 541,301,940 logical bytes. This excludes
directory allocation. The separate expanded `managed_components` SDK copy adds
another large small-file tree; capacity planning must include both download cache
and managed inputs as well as objects, outputs and temporary build files.

Future freezes should place source snapshots on suitably provisioned C:/NTFS and configure a separate
explicit D: native build root, with allocation-aware capacity admission first.
That is a future layout policy, not permission to rewrite historical frozen
paths or manifests. Source location, download cache and compiler output are
distinct owners; do not assume moving YAML alone relocates the SDK cache or
native build. After the earlier completed recovery archive, D: had 9,375,842,304
bytes available before the v10 native compilation. This is a timed observation,
not a permanent free-space guarantee.

## Historical v8 source archive before the next build

At 17:38 UTC, the obsolete `D:/aeh-build/feature-research-20261024/fork-v8`
snapshot was moved to
`C:/Users/kyvai/Archive/atmosfera-source-checkpoints-20261024/fork-v8`.
All 11,638 files matched the original source manifest before the move and were
verified again at the destination: 46,377,528 logical bytes. The original
manifest remains unchanged, SHA256
`7950ce8df65ca52a2a21a0be4338b130037e62fc0b68e323cf07ed70c87d34b1`.
The per-file recovery journal is
`C:/aeh-build/feature-wave2-20261024/fork-v8-archive-moves.jsonl`, SHA256
`e23ca5e60f1c99bcd5054f86e8fc369e5987ce5b3abb033cc8b0604d5947394f`.

The reference audit found historical v8/v9 freeze/admission dependencies. Restore
the archived tree to its original path before rerunning those helpers, or use
an explicitly reviewed relocation resolver. Current v10 verification does not
recursively load that v8 tree. The separate, active ArduinoJson headers under
`firmware-v8/managed_components/bblanchon__arduinojson/src` were untouched.
Only empty source directories were removed after file moves; no recursive
deletion was used. Completion recorded D: 11,014,504,448 bytes and C: 516,161,536
bytes free. These are timed readings, not a future build capacity guarantee.

Before reusing v10's ESPHome data root for the next isolated candidate, root
archived all 11,970 cache/metadata files, 544,071,427 logical bytes, into
`D:/aeh-build/feature-research-20261024/v10-data-before-v11-reuse.zip`.
All members were decompressed and compared by SHA256 with unchanged originals.
The ZIP is 307,911,927 bytes, SHA256
`53564883839766efca8664bb45811c96f3f0758d4bfa2627041bc1c7d07fa21c`.
Private metadata contents/per-file hashes are excluded from the public report.
The existing `product-v10/.esphome` is now explicitly a mutable shared data root
selected by process-only `ESPHOME_DATA_DIR`; recover it from that archive if
needed. This does not change the immutable v10 source files, artifact set or
source/artifact manifests. New sources reside in the isolated C:/NTFS candidate,
with a fresh explicit `firmware-v11` build on D: and unchanged global SDK prefix.
