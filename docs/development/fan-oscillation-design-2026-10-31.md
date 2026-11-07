# State-aware fan oscillation action

Accepted independent W06 slice, after manual-preset acceptance. Reuse an ordinary
Home tile and its existing captured card/revision, availability negotiation,
authorization and HA service dispatch. Do not add a native detail, task, timer,
subscription or image buffer.

Expose an explicit editor action, `fan_oscillation`, only for a fan card. Unlike
the existing fixed `fan.oscillate` service action, it resolves the opposite of
the current exact Boolean `oscillating` attribute at dispatch. Fan power is
independent: never call toggle/turn_on/turn_off as a side effect. Require a live
on/off state, OSCILLATE feature2, registered service and a present Boolean.
Missing, None, numeric, string, unknown, unavailable and capability loss must
disable the action instead of inventing false. The ordinary action revalidates
the current state at report arrival, as existing toggle actions do; it does
not promise a state value captured at touch-down or a command-result detail.

HA remains the semantic authority. The trusted profile advertises support;
browser import/draft/assignment validates the explicit action shape and entity
domain. Preview and device caption describe observed oscillation in PL/EN.
An enabled active-state palette represents oscillation, independently of power.
Existing explicit fixed-Boolean services and preset controls retain behavior.

Validate schema/dispatch/strict types, source disappearance, service and feature
loss, ordinary availability, preview/history and exact owned-layout cleanup.
Use a real MQTT fan with separate power and oscillation command topics. Observe
the actual oscillation broker payload before provider feedback; assert no power
command. Capture device originals for both observed states, outage and recovery,
plus browser configuration. Compare the normal Home/Settings route and released
buffers against the accepted native baseline. Physical fan movement is separate.

Primary contracts: [Fan entity](https://contributors.home-assistant.io/core/entities/fan/)
and [MQTT Fan](https://www.home-assistant.io/integrations/fan.mqtt/), checked
31 October 2026. Confirm the test fixture against the installed Core2026.7.1
implementation before using it; the current web documentation is newer.

HA46/native40 acceptance:549 Python tests (3 skipped),283 Node tests,34 installed
files matching the frozen source; two actual MQTT oscillation commands before
feedback and zero power commands. Held availability ABA, disabled outage,
capability loss/recovery, PL/EN, nine original captures and browser edit/Undo
passed. Exact cleanup129 restored16 cards/3 cameras/eight preferences. Normal
Home/Settings reported79frames/53 source FPS/avg16634us/failed0, with application,
scroll and close buffers released. Receipt `ha46-oscillation-scoped-acceptance.json`
in the 31 October evidence directory. Physical motor motion is a separate gate.
