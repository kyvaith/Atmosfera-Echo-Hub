# Negotiated priority Cover Stop

Status: native37/HA39 installed after one OTA. Full ESP-IDF build and53 focused
native tests/685subtests pass; HA negotiation reports version1. Hardware input,
visual and performance acceptance is in progress. This contract implements the
pending-command requirement of W05 without changing `entity_control_v1` envelopes.

## Ownership and negotiation

Keep one existing HA selection, one ordinary service fence and one bounded
successor Stop. The existing ESPHome owner/component remains on its owner task;
the view uses app6 and its shared work buffer. No worker, framebuffer, independent
subscription, polling timer or arbitrary service/URL is introduced.

Priority behavior is opt-in and defaults disabled upstream. Two optional native
API actions advertise the feature and accept its version for the exact newly
bound channel. HA checks exact API argument/response contracts and current
runtime/connection generation before accepting the echo. The native owner clears
peer acceptance on rebind/disconnect. HA exposes Cover readiness only after the
version1 echo; Light/Number/Choice continue negotiating through unchanged v1.
Older HA never enables priority input; older firmware keeps those other controls.

## Ordered, bounded successor

- An admitted Stop may supersede only a current ordinary Cover Open or Close
  in the same selection, with the negotiated feature, live STOP capability,
  authenticated principal and a non-future expected state generation. Negotiated
  Stop is an absolute intent: position updates do not invalidate it. Open and
  Close retain exact state-generation matching.
- Cancel the old local authorization/observer before yielding. Every execution
  rechecks that its command record is still current immediately before creating
  the one HA service task. A cancellation-resistant old lookup cannot dispatch
  a movement after replacement.
- If the old service already started, keep its existing shielded fence and wait
  at most the configured service timeout (normally5seconds) for completion before
  dispatching Stop. Failure consumes no extra queue or retry; an uncompleted fence
  reports not confirmed and continues blocking later ordinary dispatch.
- Replace the old state observation immediately, without waiting its8second
  confirmation window. Ignore late old results by record and command sequence.
  A repeated identical Stop is a replay; another new Stop while it is pending
  is busy. There is never an unbounded list of successors.
- Revalidate permission, binding, domain and STOP capability after the wait.
  Stop intent may survive ordinary motion-state updates after admission; reset
  its confirmation generation immediately before its own dispatch so earlier
  stationary feedback cannot be reported as a new Stop confirmation.
- Unsent movement may be canceled with an already-stationary result and no
  service call. An already-started ambiguous movement requires an explicit Stop
  call after its fence completes. No close/navigation action sends Stop itself.

The native pending-operation field admits only the Stop button while a movement
command is pending, after peer acceptance. One pointer/generation is retained.
Metadata changes, unavailable state, loss of visibility or selection still
retire held input. A negotiated Stop contact survives ordinary position/state
updates; movement contacts retain exact semantic-epoch protection. Old results
cannot re-enable movement or change status.
The negotiated Stop deadline is bounded at28seconds; ordinary commands keep
their13second deadline. Lease/renewal and explicit no-retry semantics remain.

## Acceptance gates

Test no service started, authorization cancellation resistance, slow already
started service, observation wait, timeout, duplicate/new Stop, capability and
permission loss, rebind/reopen, close/disconnect and late results. Test native
press/release/held state changes and both optional-feature builds. Keep all
ordinary Light/Number/Choice regressions. Compile, preserve, flash once and
verify exact identity, real API negotiation, screenshots, warm memory, DSI and
normal Home/media performance. MQTT feedback proves the software route; a
designated physical Cover is required for any claim of actual motor stopping.
