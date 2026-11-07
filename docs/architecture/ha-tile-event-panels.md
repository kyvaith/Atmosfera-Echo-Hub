# Home Assistant tile-event panel

This additive feature reuses the existing Action view, ControlSession owner,
EventEntity and trusted callback. It creates no additional device application,
widget, framebuffer, poller or command queue. Implementation and host evidence
are separate from firmware compilation, installed HA, device and visual checks.

## Declaration and capability

An explicit layout v3 card has `type: action`, an empty `entity_id`, and
`action: {kind: control, control: panel, property: tile_event}`. An editor review
changes only the draft; ordinary Save is still required. Existing `kind: event`
cards retain their direct route. No layout or fixture migration runs at setup.

Both negotiated profiles `action:2` and `tile_event:1` are required. The offer
contains eight profiles and remains within the existing 512-byte handshake.
An older display can return the offered subset without tile_event. There is no
fallback transaction or implicit enablement from structural service ingress.

The existing `panel_type: action` envelope carries `action_type: tile_event`.
Its only operation is `press` (bit1), with stateless phase, null policy/current
fields and `run_blocked: none`. Capabilities permit a zero read-only mask; a
qualified registered panel advertises mask1. The initial EventEntity state may
have no timestamp: unknown history does not disable a known first press.
Protocol observations classified as unknown or unavailable remain ineligible. Firmware never supplies an
entity ID, event name, service, data dictionary or custom payload.

## Target, ownership and dispatch

The bridge registers a bounded `(entity_id, private token, callback)` per device
and stable card ID. Direct and panel declarations share registration identity;
moving or explicitly converting the card preserves its EventEntity. A fresh
registration creates a new token even if its public entity ID is unchanged.

The shared owner resolves a typed `ControlTarget` before authorization and
compares it after the await. The selection retains the original registration
reference in private capabilities. It is never deep-copied into a snapshot,
serialized, hashed into a wire fingerprint or accepted from a native message.
Binding, registry, visibility, revision, channel/runtime, principal and source
generation are rechecked by the existing session fence. EventEntity state is
included in the existing bounded card subscription; no second observer owner
is created. Registration changes synchronously retire the matching panel or
opening capture through the existing close task. The same registry listener used
by robot controls also observes event targets. Removal, recreation, renaming,
disabling or ownership changes retire an outstanding gesture even after an ABA
transition; presentation-only name/icon updates do not. No new poller is added.

The default dispatch hook still creates a typed HA service call. The event
adapter instead supplies a typed trusted callback to the same single service
task slot. On that scheduled turn the owner revalidates its capture, then the
bridge performs its final registry/layout/registration check and callback/fire
synchronously without an await gap. The original direct route uses that same
final fire routine after its unchanged authorization/runtime checks.

Open, close, preview and review emit no event. A valid release dispatches once;
duplicate command sequences reuse the terminal result. A callback must return
true before the public event is fired. The terminal status `service_dispatched`
means the event was sent, not that an automation or physical action completed.
Failure or an uncertain callback never triggers an automatic retry.

## Verification boundaries

Focused host tests exercise actual registered report-schema/router code, the
shared owner, bridge binding and EventEntity lifecycle with HA doubles. They
cover first use, exact duplicate payloads, unauthorized or disabled targets,
registration/source ABA, revision/slot/runtime changes, final scheduled-turn
validation, callback rejection/exception, late pending ACK after close, and
direct-route compatibility. Editor tests
cover explicit reversible conversion, capability loss during review, closed
schema, translation/escaping and no API or event calls before Save.

The generated wire corpus comes from this owner and codec. Native negotiation,
type discrimination and input semantics still require their own tests. Complete
build, measured static memory, first boot/UART/audio, temporary owned-card CAS,
one callback/public event on the device, original screenshots and one matched
Settings/memory batch remain deployment acceptance requirements.
