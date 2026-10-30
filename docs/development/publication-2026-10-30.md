# Publication and feature-development resumption, 2026-10-30

The user requested publication of all current Atmosfera and companion ESPHome
changes, followed by resuming feature migration. Both repositories publish their
current `feature/ha-dashboard-2026-10-24` branch. Existing upstream ancestry is
preserved; neither push rewrites a branch or uses force.

Companion ESPHome checkpoint:
[`62745ae0c43a233760ddaf1fed60867736832547`](https://github.com/kyvaith/esphome/commit/62745ae0c43a233760ddaf1fed60867736832547).
The Atmosfera commit containing this record is the corresponding product
checkpoint. It includes the HA editor and adapters, product composition,
translations, research, implementation plan, tests and validation records.

## Validation before publication

- Product Python: 385 tests completed successfully, including three skips for
  optional host dependencies. Editor Node: 219 passed, no failures or skips.
- Companion: 205 focused tests and 508 subtests passed. Twelve optional tests
  were skipped because the public host LVGL/product-source environment was not
  configured. An outdated hand-written TileSurface codegen fixture was updated
  with the schema's existing `number_controls: false` default; runtime code did
  not change during publication.
- Python Ruff F/E9 and staged whitespace checks passed in both repositories.
- The publication inventory contains source, fixtures and documentation; no
  firmware binaries, private runtime captures, credentials or build caches are
  added. A bounded token/private-key scan found no matches.
- A failed test rerun exhausted C: compiler temporary space. Its failure log is
  retained. Compiler cache was preserved on D: and subsequent tests used D:
  temporary/output paths; the complete rerun passed.

The native31 [Home report](home-screen-fix-2026-10-30.md) records the separate
complete build, OTA and device/screenshot campaign. Current product firmware
configuration matches that frozen build after line-ending normalization;
later differences are HA integration/editor code, tests and documentation.
Publication does not make those later HA changes hardware-accepted. In
particular, HA20's passive Sun card still needs its device campaign and cleanup.
Earlier limits for physical touch, sustained audio and power-cut tests remain
as recorded; they are not converted into passes by this commit.

Detailed source inventory, checks and push logs remain outside Git under
`C:/aeh-build/publication-resume-20261030`. Previously preserved native30/native31
artifacts remain available for rollback.

## Resume point

Resume the pending HA20 Sun card campaign against fresh device identity and HA
state, then address the stale entity catalogue and continue the implementation
plan. Preserve the user's card positions and use only owned temporary test
entities. The native26-pinned historical operators must not be run unchanged
against native31. The user's earlier pause has ended explicitly; this is not
authorization to start publishing future feature changes automatically.
