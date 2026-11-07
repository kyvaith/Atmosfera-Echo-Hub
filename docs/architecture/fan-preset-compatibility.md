# Fan presets and an explicit return to manual speed

HA122 aligns fan preset admission with Core2026.11.0: either `SET_SPEED`1 or
`PRESET_MODE`8 permits the preset service. The registered service and complete,
bounded, valid preset catalogue remain required. This applies to the combined
fan domain, legacy Choice domain, live service validation and editor Choice
availability. Direction still requires4; climate presets still require16.

Core's full demo fan uses mask55, has a preset catalogue and implements the
preset setter. Its preset-only peer uses56. The full fan is therefore a useful
compatibility case, not a reason to alter the provider's feature flags.
[Service registration](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/fan/services.py#L78-L84),
[attribute export and validation](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/fan/entity.py#L105-L125),
[demo providers](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/demo/fan.py#L51-L88).

An active preset may legitimately report `percentage: null`. The known source
is then the exact current preset, rather than an invented percentage. In the
combined fan panel an absolute speed may be selected when all of these hold:

- The entity reports an available `on` or `off` state.
- A valid discrete speed catalogue and the speed service exist.
- The percentage is known, or a known current preset names an exact member of
  the valid preset catalogue.
- The requested absolute index belongs to the current speed catalogue.

An explicitly empty/manual preset with an unknown percentage does not qualify.
Neither do missing, malformed or off-list presets, unavailable power, an absent
speed service or a preset-only fan. Existing known-percentage behavior stays
unchanged, including a reported percentage outside the service lattice.

The device's existing speed buttons show explicit percentages and send an
absolute catalogue index on release. Native100 must apply the same narrow
source rule before enabling that input; HA122 alone cannot enable a button
blocked by older firmware. No relative adjustment, automatic initial speed,
power toggle or guessed current percentage is introduced. The demo preset
setter clears percentage; its percentage setter clears preset. Both transitions
must be confirmed by actual subsequent state, not merely a service return.
[Core demo setter semantics](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/demo/fan.py#L223-L245).

The existing single entity-control selection owns identity, lease, generation,
authorization, deduplication and the service fence. A capability change retires
the selection; a source ABA invalidates a captured command. Preset metadata
remains bounded to eight distinct names of at most32 UTF-8 bytes. This change
adds no wire fields, background task, subscription, timer, frame buffer or
display ownership path. Product composition and the saved layout are unchanged.

The isolated host tests cover both feature masks, live service checks, exact
names, invalid catalogues, manual→preset→manual provider feedback, no-feedback
results, permission denial, source ABA, preset-only and unknown-source cases.
Editor tests retain explicit review, Undo and Save boundaries and make no
provider call. These tests are not firmware or physical-device acceptance.

Keep both existing fan launchers until native100/HA122 hardware acceptance
proves the complete manual→preset→manual path and preserves the preset-only
case. Replacing the preset-only launcher's slot with Text is a later, separately
reviewed layout CAS; it does not delete the mock entity. Text99a/HA121 acceptance must finish first; its guarded final layout
restoration belongs to that acceptance. This candidate preserves the Text121
service ingress fix and adds no layout mutation.
