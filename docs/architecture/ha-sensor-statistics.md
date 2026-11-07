# Read-only hourly sensor statistics

Statistics1 extends the existing Info1 selection in App6. An explicit schema-v3
sensor/entity card action opens it:

```json
{"kind":"control","control":"panel","property":"statistics"}
```

The editor uses review → draft → Save. A saved Statistics action remains selected
when its source becomes unavailable, with one availability-aware explanation.
Switching back to Info is offered only when that source independently satisfies
the existing Info profile and server metadata checks. Existing Info cards do not
migrate automatically. The view covers the last 24 completed UTC hours, showing arithmetic
mean and minimum–maximum. Reopening starts a new read. This version has no period
selector, pagination, live history poller, service command or Recorder mutation.

## Home Assistant ownership and coherent reads

HA qualifies the actual loaded `SensorEntity`, its identity, measurement state
class, device class, unit and registry identity when present. YAML sensors without
a registry entry remain valid. Only Recorder-owned arithmetic statistics for the
selected entity qualify; sums, circular means and external statistic identifiers
do not. Current sensor availability is separate from historical data availability.

Recorder is optional (`after_dependencies`). A missing instance yields unsupported;
a configured instance that is not ready, has failed, or is stopping yields an
explicit unavailable result. The integration neither enables Recorder nor drains
its queue. It submits one scalar SELECT through the ready instance's executor,
using a fresh read-only session and the Core 2026.11 schema. A LEFT JOIN returns
metadata/storage unit and hourly rows together; the fixed UTC-window condition is
in the join, with SQL LIMIT 24 before materialization. A metadata-only row preserves
the distinction between no metadata and a qualified source with no data. This
bounds returned rows, not database I/O or execution time.

The worker receives captured immutable inputs, not live HA state. Unit conversion
uses the metadata returned with those rows; incompatible units are rejected.
Read authorization, loaded source, registry identity, state/device class, display
unit, HA zone and connection/selection identity are fenced across asynchronous
boundaries, including source/unit ABA. Permission loss or replaced selection
closes the view rather than publishing stale data.

HA129 normalizes existing string subclasses to built-in strings before storing
these semantic fields. Core `UnitOfTemperature` values are `StrEnum` instances;
HA128's exact-type unit check incorrectly excluded them. Conversion is limited to
values already satisfying `isinstance(value, str)`; it does not coerce numbers,
bytes or arbitrary objects into qualified units. Both state attributes and native
entity properties are normalized, preserving identity checks and cross-boundary
comparisons. The actual Core enum regression failed before this change and passes
after it. The live HA129 catalogue now includes the owned temperature sensor.

The existing bridge refresh path owns one executor-future admission slot. Closing,
unloading, cancelling a waiter or reaching the 10-second display deadline does not
cancel the original worker or free that slot early. Late results cannot reach a
new selection; late exceptions are retrieved. A second read while occupied gets
bounded `busy`, without a queue. Close retires cached data; lease renewal
reauthorizes without repeating the database read or moving the window.

## Negotiation and bounded wire

Separate response-only `entity_info_statistics_query` / `entity_info_statistics_bind`
APIs negotiate `entity_info_statistics_v1`, version1, after current-channel Info1.
The option defaults off and is independent of the eight existing Extra profiles.
Binding requires a quiescent owner and rechecks runtime/client/channel/epoch.
Handshake size is 512 bytes; snapshots keep the existing 2048-byte envelope.

Snapshots use Info caps `{"info_type":"statistics","statistics_version":1}`,
zero eligible actions, and the existing selection/generation/sequence rules.
States distinguish loading, ready, empty, unsupported and error. A 24-bit mask
distinguishes gaps from real zero values. The 288-character packed field holds
24 min/mean/max triples, quantized to 0..1000; native stores 72 uint16 coordinates,
not retained hex or JSON-number nodes. Flat data uses 500. Missing/incomplete rows
are gaps; invalid values or ordering are errors. Generation includes retained
unquantized data, so visually equal quantization cannot hide a semantic change.

The graph never reconstructs measurements from coordinates. HA supplies bounded
axis/unit/date labels with full local dates, UTC offsets and zone name. The window
always spans 24 UTC hours across DST. Unrepresentable labels yield an explicit
state instead of a misleading clipped unit/date.

## Native owner, memory and UI

The existing Info owner stores one Statistics variant and retains App6 navigation,
preview retirement and shared buffers. Actual P4 type compilation measured
Statistics 356 bytes, Snapshot 728, Message 960, Owner 1184 and Codec 5152; the existing
owner/message/codec sizes did not grow. The codec arena remains 5120 bytes and the
payload 2048 bytes. This is a static ABI result, not a runtime free-heap measurement.

P4/32-bit must accept the complete corpus within that budget. Desktop64 has larger
allocation metadata and safely rejects the maximum-storage stress case, leaving
output and selection unchanged and accepting a subsequent valid message. That is
bounded-rejection coverage, not full-corpus x64 support. Host32 with P4 allocation
alignment is explicitly a proxy, separate from actual target execution.

One plain, childless, nonclickable DRAW_MAIN surface adds a vector graph: at most
23 adjacent mean segments, 24 whiskers and singleton markers. There is no chart
dependency, bitmap, canvas, framebuffer, task or timer. Geometry derives from the
configured surface; existing KIND/TITLE/UPDATED/STATUS widgets remain. The product
adds nine localized keys and preserves 38 previous widgets. Full-width time rows
and a two-line zone label include actual line spacing. Empty/error states retire
the plot. Gallery, Player, Assistant, Camera and display ownership are unchanged.

## Validation and retained limits

Firmware115 and HA129 were adopted locally on 2026-11-07 after the complete
native build, linked verification, one OTA, actual HA deployment, CPU and
owned-demo temperature routes, original device screenshot review and browser
review/draft/Undo checks. See [the dated acceptance record](../development/statistics-2026-11-07.md)
for artifact hashes, measured memory, performance and exact evidence paths.

The same-firmware weather comparison explains the large apparent free-memory
difference from the older clear-night reference. It does not attribute every
allocation, prove absence of leaks, or qualify all weather variants. The
comparable batches retain the same Home median37.5 FPS and Settings54 FPS;
individual larger Home latency peaks on115 remain recorded. No physical60-FPS
or long-term stability claim follows from these measurements.

The first boot transmitted the complete digital startup sound and retained wake
readiness, but used known mixer/Sendspin resource recovery. Its strict-clean
classification remains false. Acoustic listening was not performed. Historical
failed boot, Agenda107 and desktop64 stress reports remain separate. The
maximum-storage desktop64 case is a deliberate bounded refusal; the unchanged
5120-byte codec arena is qualified for the actual32-bit target.

Statistics does not migrate existing Info cards. The temporary test launchers
were restored by revision-checked CAS; browser testing left no unsaved draft.
Larger periods, state-history timelines and other chart types remain future
work. Neither repository was committed or pushed.
