# Fan preset selection

W06 extends the accepted generic choice view to fan presets. HA owns the exact
`preset_modes`, `preset_mode`, PRESET_MODE feature and `fan.set_preset_mode`
service. Power (`on`/`off`) is independent of the selected preset; no inferred
toggle is added. The existing default fan action remains unchanged.
The [public fan contract](https://contributors.home-assistant.io/core/entities/fan/)
distinguishes presets from manual speed and allows no active preset.

Reuse the one app6, choice token, semantic generation, authorization, single
service fence and bounded eight native option widgets. No new firmware field,
task, subscription, timer or full-screen buffer. The complete exact list remains
1..8 distinct printable values, each at most32 UTF-8 bytes. Unsupported or
oversized lists are rejected whole. Both HA and editor revalidate capabilities,
registered service, current preset, list and selection before Apply. A state/list
ABA or capability loss cannot revive a held selection.

The original adapter admits an existing known preset on an available fan.
Native40/HA45 also accepts an explicitly present `None` as known manual mode
through the negotiated [empty-choice contract](empty-choice-design-2026-10-31.md).
Missing or malformed attributes remain unknown. There is no synthetic option0:
the first real candidate must be selected before Apply becomes available.
Speed/oscillation/direction remain separate W06 slices.

Validation uses an owned real
[MQTT fan](https://www.home-assistant.io/integrations/fan.mqtt/), without a motor.
The operator subscribes to its unique preset command topic. Only after observing
the actual broker payload does the test provider publish matching preset state.
Service acceptance, MQTT command, matching HA state and native result stay
separate evidence. Local candidate/cancel/no-op must emit zero extra commands.
Also check list/capability changes, unavailable, editor review/Undo, screenshots,
normal Home/Settings FPS, heap/buffer release and exact cleanup. No household
fan commands are part of this campaign. All changes remain local/uncommitted.
