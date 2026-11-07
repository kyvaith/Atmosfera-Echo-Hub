# Native tile-event action panel

The optional `action_controller.tile_event` capability opens an owned Atmosfera
tile event in the existing App6 Action view. Home tiles remain launchers; opening
or closing this view does not send an event. The existing primary button sends
one Press command after an eligible pointer release. There is no automatic
migration of existing direct-action tiles.

The reusable option defaults to false and requires the Action controller to be
enabled. Atmosfera opts in through `tile_event_control_product_admitted`.
Negotiation keeps `action:2` and adds `tile_event:1`; the latter requires the full
Action2 mask (24), and its own bit is 256. Extra-profile masks are therefore
16-bit, while unrelated Detail masks remain 8-bit. An older implementation can
accept its known subset without enabling tile events. Without both capabilities,
the new Action subtype 5 is rejected by the parser, grant admission, and owner.

The existing Action envelope and command fields are unchanged. Tile events are
stateless, allow only Press, and use the existing generation, view-readiness,
lease, pending-command, and pointer fences. A missing last-used timestamp on the
first use is valid and does not imply an unavailable entity. A successful result
means `service_dispatched`, not confirmation that an automation or physical
device completed. `service_completed` and `state_matches` cannot complete this
command. The HA integration owns event target resolution, registry ownership,
dispatch authorization, and revocation; see `ha-tile-event-panels.md` in the HA
integration delivery.

The presenter reuses the existing Action root, four SVG icon objects, and three
buttons, choosing the existing action-button icon and primary Press control.
Product translation callbacks provide Event, Send event, and Event sent only
for this subtype, preserving all other Action labels. Polish and English labels
fit the existing generated Roboto glyph sets and geometry.

No task, polling loop, widget, raw framebuffer, or snapshot path is added. App6
retains its existing navigation and compressed-preview lifecycle. The widened
masks fit existing ESP32-P4 structure padding: the focused target probe retains
Snapshot 728 B, Message 960 B, owner 1136 B, and component 11584 B. The six extra
localized rows add flash data (including 72 B of Translation table entries), not
a new SRAM pointer array. These are source and target-layout observations, not
whole-firmware or hardware memory measurements.

Focused validation covers default-off compatibility, eight-profile negotiation,
actual HA wire fixtures, owner terminal-result rejection, source ABA and pointer
retirement, and public LVGL input using the unchanged Action geometry. Full
firmware build, deployment, event-count verification, screenshots, and measured
performance remain required before accepting the feature on the device.
