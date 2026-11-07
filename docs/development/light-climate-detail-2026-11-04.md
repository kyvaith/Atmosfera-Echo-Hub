# Light detail and Climate panel — HA111

This package extends the existing single App6 control session. Product SVG,
composition and600px thermostat geometry remain product/native responsibilities.
The HA backend owns live capability/catalogue discovery, permissions, exact
service mapping, source feedback and bounded read-only facet selection.

HA111 removes a redundant old kind allow-list from the registered report
service. The strict report decoder remains the direction gate and accepts
the negotiated `facet` report. Firmware-only message kinds remain rejected.
Tests exercise the actual registered schema and handler; codec-only coverage
had missed that the HA110 service rejected valid facet reports at ingress.

## Explicit actions and compatibility

Light detail saves `{"kind":"control","control":"light","detail":1}`;
Climate saves `{"kind":"control","control":"panel","property":"climate"}`.
They never replace legacy actions automatically. Kelvin/effect and thermostat
cards controlling different entities must not be collapsed during migration.
Existing RGB and range service actions remain separate; this package does not
provide a new RGB picker or editable target range.

Supplementary features use `entity_detail_features_v1`: detail_version and
independent light_detail_version/climate_panel_version0/1. Binding is to the
current channel, with no active/opening selection. The previous Panel-v1
query/bind and schema_panel_types remain exactly Timer/Remote/Power. New
schema_light_detail/schema_climate_panel flags describe the product schema;
actual admission requires live negotiated flags. Missing or malformed detail
APIs do not disable old controls.

The Light Home row carries control_kind light plus control_detail_version1.
Only the explicit native launcher sends detail_version1 on open/cancel_open.
HA checks it against the stored action; it is not part of tokenized selection
identity. A legacy peer cannot silently treat this card as brightness-only.
Unsupported detail launchers have disabled press. Climate admission is
independent of a currently editable target and may display an offline source
with real retained metadata.

## Facets and lifetime

Light facets: main, color_temp_kelvin, effect. Climate facets: main, humidity,
hvac_mode, preset_mode, fan_mode, swing_mode, swing_horizontal_mode. Main
Climate maps to its existing single-temperature numeric adapter.

One monotonic view_seq belongs to the current token. Initial grant is main0;
other facets require a positive requested sequence. A facet request contains
selection identity, view_seq and a closed facet name, with no target or service.
The sole authorization slot is reused. Fresh state follows successful
authorization, then a typed ready/rejected facet receipt. A receipt never
proves a device action. Pending service or authorization makes navigation busy;
no service is cancelled merely to open a subview. Old/colliding sequences,
another token, stale metadata and closed views cannot re-enter the owner.

Commands capture facet, view_seq, authoritative index and semantic generation.
`facet_number` resolves one exact NumericDomain index to an absolute service;
`facet_choice` resolves one index through the HA-owned ordered catalogue.
Power/brightness keep their existing service semantics in explicit Light main,
with additional generation/view fencing for this opt-in profile. One pending
command/service remains the maximum.

Metadata/catalogue/unit changes revoke the selection, including ABA. Target,
mode and knownness transitions advance semantic generation before event
coalescing. This includes displayed single-target and range low/high setpoints
when no editable NumericDomain exists. Current temperature/humidity and HVAC action are display-only
updates; their changes preserve an otherwise valid held target. Measurements
never substitute for targets. State feedback must match the captured target;
successful service completion alone does not become a physical confirmation.

## Bounded metadata and honest unknowns

Each entity's light_detail/climate_panel catalogue metadata contains version1,
facets bitmask,64-hex metadata fingerprint, facet_reasons and a main observation.
Reasons are unsupported_metadata, unsupported_service or unsupported_catalogue.
The fingerprint excludes routine observations and includes actual domains,
ordered canonical options, labels and units. Editor review does not expire on
ordinary telemetry changes.

Climate minimum/maximum temperatures are immutable provider metadata, included
in the fingerprint even for passive or range-only panels. They remain visible
when the source becomes unknown, if the source still advertises valid bounds.
Unknown source state clears current/target/low/high observations and disables
commands; it does not invent or discard still-valid configuration limits.

One native snapshot contains one active numeric/choice body, with at most8
unique32-byte UTF-8 labels. Canonical values stay in HA. Translation collisions
or oversized labels fall back to the complete canonical list; no truncation
or invented option0. A known empty effect/program is distinct from missing,
unknown or off-list source data. Unrenderable native labels disable that facet
with a visible reason; they cannot dispatch a hidden choice.

Kelvin uses actual min/max and Core's integer1K service granularity. Its target
is known only while on with color_mode=color_temp. Climate uses the existing
native/display temperature-unit check and exact provider step; off remains an
allowed single-target mode, as in legacy Number. Auto/heat_cool or range-only
metadata does not imply an editable single target. Actual low/high setpoints
are passive range observations, not hysteresis. Generic provider-independent
hysteresis remains unimplemented and requires a real separately authorized
provider mapping; no second entity is inferred into this session.

## Validation boundary

Focused host tests cover strict codecs, old/new negotiation fallback,
read-only opens/views, every service mapping, exact empty/unknown handling,
pending physical-service fences, view/metadata/source ABA, terminal ordering,
passive range/offline sources and bounded labels. Shared old-profile tests
must also pass. Native parser arena, setup stack, full build, firmware identity,
device gestures, original screenshots and performance remain separate evidence
owned by the complete candidate90 acceptance. Never service-test the real
boiler or unrelated lights as a convenience fixture.
