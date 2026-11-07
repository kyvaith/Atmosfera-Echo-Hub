# Light and Climate icon sources

These six monochrome SVG assets are Material Design Icons by Pictogrammers,
under Apache 2.0. The retained upstream notice is
[materialdesignicons-LICENSE.txt](../fonts/materialdesignicons-LICENSE.txt).

All sources are pinned to revision
`2424e748e0cc63ab7b9c095a099b9fe239b737c0`:

- `detail-lightbulb.svg`: [lightbulb-outline.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/lightbulb-outline.svg)
- `detail-thermometer.svg`: [thermometer.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/thermometer.svg)
- `detail-thermostat.svg`: [thermostat.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/thermostat.svg)
- `detail-preset.svg`: [tune.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/tune.svg)
- `detail-swing-vertical.svg`: [swap-vertical.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/swap-vertical.svg)
- `detail-swing-horizontal.svg`: [swap-horizontal.svg](https://github.com/Templarian/MaterialDesign/blob/2424e748e0cc63ab7b9c095a099b9fe239b737c0/svg/swap-horizontal.svg)

Product adaptation expands H/V segments to L, circular arcs to cubic curves
of at most 90 degrees per segment (including the thermometer's large bulb arc),
and implicit filled closure to Z. Non-rendering root IDs are removed. The
existing SVG widget applies the product accent at draw time.

Parameters also reuses the existing product `fan.svg` and `humidity.svg`.
There are no bitmap assets, continuously animated symbols or new icon workers.
