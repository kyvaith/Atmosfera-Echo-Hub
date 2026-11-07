# Camera launchers from Home

An explicit layout-v3 Camera action opens the existing Camera application
directly from a Home tile. It uses the existing temporary keyed preview and
its normal close gesture, timeout and source-selection restoration. There is
no intermediate device panel. The Camera renderer, network stream, JPEG/DSI
ownership, audio, player and voice applications are unchanged.

## Configuration and ownership

The saved card is an editable `entity` card targeting an existing `camera.*`
in this display's camera allow-list. Its closed action schema is
`{"kind":"camera_preview","duration_seconds":35}`, with an integer duration
from 15 to 90 seconds. URLs, service parameters and credentials are rejected.
Only the entity identifier and duration belong to the layout.

Adding a camera from the HA entity library creates a passive tile. The user
explicitly selects Camera preview, reviews the target and duration, then adds
the change to the draft. Normal Save commits the layout; Cancel and Undo keep
their established meanings. Import, validation and Save check the current
configuration-entry allow-list and the runtime entity's existence. The legacy
card mirror is passive. No migration changes existing tiles automatically.

The HA bridge owns the allow-list, current signed source catalog, authorization
and the launch request. Native Home already owns touch/release identity;
native CameraPreview continues to own App5 navigation and temporary source
selection. No frame buffer, task, widget or on-device cache is added.

## Admission and async boundaries

Schema support does not imply runtime readiness. The launcher requires both
contextual-press and press-enabled contracts, the exact response-only preview
API argument contract and a successful keyed source ACK from the current
runtime/client/connection epoch. Legacy non-keyed pushes never qualify.

The HA-only catalog proof retains existing source references and a generation.
Source refresh, source-state changes, reconfiguration, reconnect and unload
invalidate it. A stale completion cannot republish proof for a later epoch.
The tile is unavailable until the proof and a known available source agree.
No URL or credential is exported through editor/catalogue status.

The public contextual ingress carries slot, card identity and saved revision.
The typed manual route checks the current configuration entry as well as the
bridge cache, visibility, page visibility, source and catalog generation. It
checks display and camera permissions using the existing HA-context policy,
and repeats identity/runtime/catalog fences after each awaited authorization.

Only then does it generate one request ID and call the existing lower preview
helper. Its admitted source is already present, so this path cannot enter the
helper's asynchronous catalog-refresh branch before dispatch. One manual
request may be in flight. Busy and unconfirmed responses are never queued or
retried; manual launching never creates a ringing notification, provider
service call, tile event or automation event.

Four recent attempt identities prevent a repeated delivery with the same
HA Context from dispatching again. The existing contextual report has no
press-sequence field, so a later replay carrying a new Context is not claimed
to be deduplicated. The native preview's existing request-ID deduplication is
unchanged.

## Validation boundary

Focused host tests cover the actual registered contextual handler/schema,
closed layout schema, allow-list/editor projection, ordinary preview path,
permission denial, concurrent requests, repeated same-context delivery,
uncertain/busy replies, and source/layout/runtime changes at both authorization
boundaries. Editor tests exercise review, duration, Cancel, Undo and stale
capability/selection handling. Existing camera/bridge tests remain separate.

Hardware acceptance still needs a real configured camera: Home directly to
App5, a presented live frame, standard close and original source restoration,
screenshots, presentation FPS, memory and audio continuity. Host success does
not prove stream startup, physical display behavior or hardware performance.
