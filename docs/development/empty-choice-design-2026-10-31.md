# Selecting a fan preset from manual mode

The existing v1 choice contract deliberately equates availability with a known
index. HA43 therefore cannot select the first fan preset when `preset_mode` is
explicitly None. Keep that contract strict for old peers.

An optional typed `entity_choice_get_features` / `entity_choice_bind_features`
handshake advertises `entity_choice_features_v1`, version1. The echo must accept
the exact current generic channel before either peer admits known-empty choice.
Rebind/disconnect retires acceptance; stale echoes and attempts while a selection
or open authorization exists fail closed. The reusable choice selector option
`allow_empty_selection` defaults false. The product explicitly opts in.

After negotiation only, a choice grant/state may carry `available:true,index:null`.
Unavailable remains `available:false,index:null`. HA admits known-empty only for
an available fan with the PRESET_MODE capability, valid exact preset list, live
service and an explicitly present None preset attribute. Missing, malformed,
off-list, unknown and unavailable values do not become manual mode.

The native owner represents empty internally by MAX_OPTIONS, outside all valid
indices. No synthetic option is inserted. Initially no candidate is selected
and Apply is disabled; a real candidate tap enables it. The current caption says
there is no active option until HA confirms a preset. Commands use nullable
expected_index plus the existing semantic generation. Manual→preset→manual and
available→unavailable→available advance generation and cancel an old held Apply.
The existing exact-list, authorization, service fence and result policies remain.

Ownership: HA owns semantics and the real preset service. The one native choice
owner holds channel acceptance, current/candidate and pointer state. Its existing
eight widgets and app6 own presentation through unchanged navigation/buffers.
Two bounded flags and an unused index value replace no image storage. There is
no new task, timer, subscription or framebuffer. Codec extension flags are per
transaction and default false; routing accepts structure only, then the matched
owner revalidates negotiation before authorization. Existing Cover and legacy
Light handshakes retain their exact shapes.

Acceptance requires old/default rejection and negotiated round trips in Python
and actual C++, real LVGL no-candidate/Apply/ABA tests, schema defaults, complete
configuration/build, preserved firmware and one verified OTA. Then a real owned
MQTT fan must start with no active preset, choose locally without a command,
Apply once with expected_index:null, receive an actual broker command before
provider feedback, and confirm a real preset. Cover list/unavailable/ABA/rebind,
browser admission/preview, PL/EN originals, exact cleanup and matched performance.
Compile, flash, software feedback, screenshots and physical motor acceptance are
separate claims. Native40/HA45 passed these scoped gates, including the public
service-schema nullable decode fix, on 31 October. Final campaign10 restored
revision127 and all eight preferences; twelve device originals and the real
browser review/Undo were inspected. The normal Home/Settings route reported
54 source FPS,79 frames, failed0 and released application/scroll/close buffers.
See `manual40-ha45-scoped-acceptance.json` in the 31 October evidence directory.
