# Read-only calendar agenda

Agenda1 extends the existing Info selection in App6. It is an explicit schema-v3
action on a visible calendar sensor/entity card:

```json
{"kind":"control","control":"panel","property":"agenda"}
```

The editor reviews the change and modifies only its draft. Existing passive
Calendar `info` cards remain unchanged until the user saves an explicit change.
No calendar service or write permission is involved; opening and paging require
fresh Read authorization for the same loaded CalendarEntity instance. YAML
calendars without entity-registry entries are valid. Registry identity changes
or replacement of the loaded source retire the selection.

## Negotiation and wire

Info1 and the existing generic channel remain prerequisites. Separate optional
response-only `entity_info_agenda_query` and `entity_info_agenda_bind` APIs use
`type: entity_info_agenda_v1`, `v: 1`, and `agenda_version: 1`. The bind captures
the current client/channel/connection epoch across both awaits. Absence, rejection
or reconnect leaves Agenda disabled; the eight Extra profiles are unchanged.

An Agenda snapshot uses `panel_type: info` and exact caps
`{"info_type":"agenda","agenda_version":1}`. Its state contains source/status,
request sequence, current index, count (0..16), `has_more`, one event, and an
explicit excerpt mask. It has no `updated_text` or clock-derived active flag.
Empty/loading/error/unknown states carry no old event text. Text byte limits are
summary96, start40, end40, zone48, location64 and description32. The existing
2048-byte payload limit and strict duplicate/unknown-field rejection remain.

Paging is a read-only `page` message carrying the existing selection identity,
`request_seq`, `target_index` and `expected_state_generation`. It never becomes a
COMMAND or HA service call. HA rechecks authorization, source identity, layout,
visibility and generation after awaits, then emits the matching STATE and
`page_result`. One pending request and one cached receipt bound duplicate work.
Native acceptance requires both the matching state and receipt; timeout does not
retry automatically. Same-generation unsolicited index changes are rejected.

## Ownership, dates and limits

On open, the window starts now and ends at local midnight seven calendar dates
later in HA's configured time zone. HA subscribes through Core's CalendarEntity
API. Core owns the fetch; the existing bridge state task coalesces callbacks.
Closing unsubscribes and releases the cache. A late Core fetch cannot modify a
closed or replaced selection. The existing renewal path also checks a ten-second
initial loading deadline; a later valid provider callback may recover from error.

The selection retains at most sixteen normalized events in chronological order.
It scans Core's list without copying or mutating that list and discards the old
cache before building its replacement. Core/provider expansion is not bounded by
this cache limit. The ESP retains only one event in its existing Info variant;
there is no new full-screen buffer or event array. The UI reuses Calendar widgets
and adds only two buttons and two labels. Page loading is static, not animated.

All-day dates preserve Core's exclusive end internally and display an inclusive
last day. Timed values retain the local UTC offset, including DST transitions.
Overlapping events and separate occurrences are preserved. Long text is plain,
UTF-8 bounded, marked as an excerpt, and never recorded in persistent calendar
logs. Source/status and the full semantics of retained events, including content
beyond displayed excerpts, drive generation changes and cancel held navigation.
Changing only the page index does not change the source generation.

## Demonstration and validation

The existing owned `calendar.atmosfera_demo_agenda` retains its non-registry
identity and `Calendar 1` name. Its provider supplies six read-only examples:
current, future, overlapping, all-day, multi-day and long Polish text. It adds no
unique ID, device registration, event-write service or automatic card migration.

Host tests cover actual report ingress, default-off negotiation, Read permission,
source/registry ABA, pagination deduplication, late callbacks, loading/error and
generation exhaustion, exclusive dates/DST, bounds and the existing passive Info
path. The actual HA/native codec corpus is kept under `tools/tests/fixtures/agenda`.
Compilation, installed Core/provider behavior, device screenshots and performance
remain separate hardware acceptance gates.
