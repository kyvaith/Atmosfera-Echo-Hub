# Date and time helper information

Implemented in HA42 and checked on native39, with live editor and physical
screenshots. This W10 slice follows the HA40 calendar sensor formatter. It adds
passive `input_datetime` information, not a date/time picker or service action.
HA owns values and capabilities. The public
[helper contract](https://www.home-assistant.io/integrations/input_datetime/)
distinguishes date-only, time-only and combined helpers; installed Core2026.7.1
source confirms strict boolean `has_date`/`has_time` metadata and local literal
state formats YYYY-MM-DD, HH:MM:SS and YYYY-MM-DD HH:MM:SS.

Reuse the HA40 calendar validator. Validate exact ASCII state and real date/time
bounds. PL date uses DD.MM.YYYY; EN keeps YYYY-MM-DD. Preserve all time fields,
including seconds. A combined local value stays local: do not interpret its
timestamp attribute or convert timezones. Missing/non-boolean capabilities,
both flags false, malformed values and outages remain explicit. Exact user
state labels retain priority. Numeric precision is not applicable.

Admit only editable information cards with action:none in the existing text
places 3/5/8/9/10/11/12. A combined value needs 19 characters. Hardware HA41
showed its first/last digits clipped in slot15's 136 px caption; even a wide
outer tile does not imply sufficient text width. The admitted Roboto16 captions
are at least 172 px wide. Publish an optional
trusted `datetime_text_slots` profile capability; old/absent capability fails
closed in the editor. Assignment, moving/swapping, clipboard, draft recovery,
import and save must use the same admission. Default to the existing clock icon.

HA normalization, catalogue and runtime resolver must reject executable
raw/legacy attempts too. Do not offer `input_datetime.set_datetime` as an action.
No native protocol, widget, font, task, timer, subscription or raw buffer changes.

Host gates: all three capability modes, strict booleans, time/date bounds,
shared PL/EN vectors, mappings/outages, unchanged sensor/timestamp behavior,
read-only model and resolver, text-place and editor transaction checks.
Device gate: one owned real HA helper changed through all three modes, real
source service updates, PL/EN, passive taps, offscreen updates, original images,
exact field inverse and deletion after unbinding. Preserve16cards/3cameras/8
preferences and 53–55-FPS Settings cadence. The user confirmed the desktop was
unlocked; all three modes now have actual editor observations and screenshots.
See [the acceptance record](validation-2026-10-31.md), including the preserved
failed/clipped attempt and its replacement campaign.
