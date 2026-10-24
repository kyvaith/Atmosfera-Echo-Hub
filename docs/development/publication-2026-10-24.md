# Validated checkpoint publication, 2026-10-24

The user explicitly requested publication of both repositories before the next
feature-development phase. Both use `productization/current-2026-09-27`.

The companion ESPHome revision is
[`41e735733078651443b7c0bf56ede4c94f7f5d25`](https://github.com/kyvaith/esphome/commit/41e735733078651443b7c0bf56ede4c94f7f5d25).
The Atmosfera commit containing this record identifies the matching product
checkpoint. No upstream history was replaced, and neither push uses force.

The [LVGL and memory recovery report](lvgl-memory-recovery-2026-10-22.md)
contains the exact firmware ELF/OTA hashes and bounded hardware results from
2026-10-22. Publication does not turn unavailable cold-power, real Sendspin
playback or provider/acoustic dialogue tests into passes.

Before publication, all 11,631 companion source entries and 213 frozen product
entries were compared with the validated source checkpoint. The differences
are line endings, later documentation and the build-only `diagnostic.yaml`
wrapper (not part of the normal product configuration). There are no substantive
runtime changes. One redundant EOF blank line was removed from a Sendspin host
test fixture to satisfy the staged whitespace check; all 36 focused Sendspin
tests passed afterward with both optimization branches executed.

Detailed comparison and publication evidence remain outside Git under
`C:/aeh-build/feature-research-20261024`. Firmware captures and private runtime
logs remain under the earlier validation evidence roots. They are not uploaded
as product assets.

Subsequent research and implementation belong to a new working phase. They
must retain explicit component ownership, bounded memory and actual-device
performance/screenshot validation before being described as verified.
