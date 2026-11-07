# External-media panel — native93 / HA113

This profile controls one explicit Home Assistant media_player entity. It does
not alter the dedicated local Player, audio transport, Sendspin, Voice, Camera,
Gallery or notifications. No artwork or bitmap is introduced. Native device
identity uses SVG/material icons and the existing M3 controls.

The saved v3 action is explicit:

```json
{"kind":"control","control":"panel","property":"media"}
```

Existing service, default and Choice launchers retain their intent. The editor
offers a staged draft conversion only after optional Extra `media:1` negotiation
and live capability checks. Saving remains the existing revision compare-and-swap.
Unknown sources may open a passive view; they cannot issue commands. This profile
requires the existing control permission. It is not a read-only Info shortcut.

## One selected owner

`MediaPanelPolicy` extends the existing entity-control owner and service fence.
It creates no second session, subscription, service queue or renewal timer. One
selection retains one domain and one active view: Main, Volume, Source, Sound
mode or Repeat. Native receives only the active catalogue, at most eight complete
labels of32UTF-8bytes. Capability/catalogue changes retire the selection.

Main exposes explicit Play/Pause, Previous/Next, Stop, power, relative volume,
Mute and Shuffle only when actual feature flags and registered services permit
them. Attribute presence never grants a control. The historical demo TV notably
publishes volume and mute attributes without advertising those capabilities.
Native controls use SVG identity and one shared panel owner, not another player.

The owner increments semantic generation for phase, raw volume, mute, shuffle
and current catalogue selection changes, including ABA. Track title, artist and
position telemetry remain display observations, so they do not invalidate a held
volume gesture. The existing layout/card/channel/token/principal/epoch checks
apply at admission and again after authorization immediately before dispatch.

## Honest volume and confirmation

Raw observed volume is finite0..1, serialized as the exact canonical shortest
source float string up to24ASCIIbytes. Percent text is its exact decimal product
by100, up to26ASCIIbytes, with scientific notation for very small numbers. The
rail is approximate geometry0..10000. It is never an authoritative index. Missing
or invalid volume is null, never a fabricated zero.

The explicit UI target grid is integer percent0..100 with step1. This does not
claim source/device precision. Preview sends no service. Release sends one
absolute target/100, guarded by exact expected raw observation, semantic
generation, facet and view sequence. Authoritative changes cancel a held edit.
Mute/Shuffle similarly use explicit boolean targets, never toggles. Play and
Pause remain distinct operations. Choice applies one exact canonical value.

Absolute-target operations require a new semantic generation and matching HA
observation after dispatch. Stop accepts actual Off/Idle/Standby. Previous/Next
and relative volume cannot prove an exact target; successful callbacks report
only `service_completed`, not physical track or volume confirmation. No source
state is optimistically changed. A pending service blocks facet navigation.

## Closed optional wire

Extra handshake extends its sorted profile subset with `{name:media,version:1}`;
Info/Lock and old Panel/Detail handshakes remain unchanged. OPEN still has kind
Panel and the complete selection identity. STATE uses panel_type media, bounded
operation/facet masks, and exactly one active view. Media commands and facet
messages carry integer `media_version:1`, parsed before Light/Climate Detail.
This prevents an identical facet name from being interpreted as another family.

Limits are unchanged:2048 wire bytes,5120 DOM bytes, one owner and active family.
The frozen host wire corpus lives in the isolated work directory `wire-v1`.
Native93 keeps the existing728-byte snapshot and960-byte message. The complete
component is10752B,400B more than92c; the complete firmware static RAM grows952B.
These are separate, overlapping accounting levels and must not be added together.
No worker or full-screen buffer is added. Final linked call-path review is scoped
to the inspected paths, not a universal stack bound. Device heap and performance
remain separate measurements.

Media owns the foreground of its buttons and their content. An SVG widget can
carry its own theme text color, so changing only its parent does not guarantee
contrast. Native93a corrects the neutral-icon issue locally in the Media renderer;
the generic SVG theme remains unchanged. Actual device screenshots confirm the
neutral and selected control contrast.

## Evidence and remaining integration

The isolated HA host tests cover actual music/TV capabilities, fractional and
subnormal volume, strict codecs, known/unknown availability, explicit intent,
metadata-vs-command generation, ABA, duplicate commands, service fences and
canonical choice. Editor tests cover optional negotiation, live features and
service loss, draft-only conversion, review invalidation, offline retained
intent and PL/EN copy. These are host tests with fake services, not proof of
physical playback. Native93 has passed the full build and qualified first-boot
audio/wake checks. HA113 is installed; layout357 changes only the actions of
slots24/25 to this panel. A separate read-only check confirmed persisted layout
after the initial migration postcheck failed; the original failure is retained.

The first device batch passed both players' Play/Pause and a42% volume command,
then stopped on a gesture that emitted no command. The updated harnessv5 samples
each press and requires actual drag/render progression. On native93a it confirmed
the61% preview and the42→100 command, but subsequent readiness failed because
completion base161 no longer matched current base162. Native93b normalizes the
Volume Back button's invisible recolor across enabled/disabled states. The
actual default-theme clock test reproduces9 delayed flushes in each direction
before the fix and0 after it. Scalar's stale-base rejection remains unchanged.

Native93b passes all four Media hardware groups, including repeated volume
commands, exact42.5% observation, separate61% preview, semantic ABA cancellation,
source/sound/repeat choices and unavailable/recovery. All21 original screenshots
passed review. Both owned mocks were restored exactly, with no layout change.
Light/Climate open-close checks and five further screenshots passed. The initial
shared-view smoke failure came from incomplete diagnostic assembly, not a stuck
renderer; its original report and corrected-test evidence are retained.

Three Settings routes measured55FPS and no failed compositor presentations,
versus54FPS previously. Snapshot segmentation differed; this is not a controlled
speedup attribution or a sustained60FPS claim. DSI underrun warnings remain:
3 baseline IRQ events versus4 in the candidate's short route batch. Static
screenshots do not prove absence of transient physical scan-out artifacts.
The local Player and audio transport are unchanged. See the
[current checkpoint](../development/resume-2026-11-04-panels.md).

Primary contracts: Home Assistant Core2026.7.1
[media features](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/media_player/const.py),
[media service implementation](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/media_player/__init__.py),
[demo entities](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/demo/media_player.py),
and the [HA frontend media view](https://github.com/home-assistant/frontend/blob/dev/src/dialogs/more-info/controls/more-info-media_player.ts).
