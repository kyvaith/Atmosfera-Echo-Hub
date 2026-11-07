# Timer, Remote and Power icon sources

These monochrome shapes are Material Design Icons by Pictogrammers, under
Apache 2.0. The upstream notice is retained in
[materialdesignicons-LICENSE.txt](../fonts/materialdesignicons-LICENSE.txt).

All five sources use revision `2424e748e0cc63ab7b9c095a099b9fe239b737c0`:

- `panel-timer.svg`: [timer-outline.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/timer-outline.svg)
- `panel-remote.svg`: [remote.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/remote.svg)
- `panel-power-switch.svg`: [light-switch.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/light-switch.svg)
- `panel-power-outlet.svg`: [power-socket-eu.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/power-socket-eu.svg)
- `panel-power-unknown.svg`: [power.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/power.svg)

Product adaptations replace H/V with explicit L commands, circular arcs with
cubic curves, and implicit filled-contour closure with Z. Non-rendering root
IDs are removed. The existing bounded native SVG widget supplies the tint.
There are no raster assets, continuous animation or new graphics workers.

Power class is selected only from Home Assistant's actual device class.
Missing or unrecognized classes use the neutral power symbol; entity names
and IDs do not determine an outlet or switch illustration.
