# Wear OS M3 LVGL Map

Source: `C:\Users\kyvai\Downloads\M3 Wear OS Apps Design Kit (Community).fig`

The local `.fig` was decoded as `fig-kiwi` and used as the design source for the LVGL UI. The kit uses a 192dp Wear OS canvas; this project renders at 800px, so the reference scale is `800 / 192 = 4.1667`.

## Tokens

Core WM3 tokens used in LVGL:

- Background: `0x000000`
- Surface: `0x303030`
- Surface bright: `0x474747`
- Tonal control surface: `0x332E3C`
- Selected tonal surface: `0x4D3D76`
- On surface: `0xF2F2F2`
- On surface variant: `0xC4C7C5`
- Outline variant: `0x5C5F5E`
- Primary: `0xD3E3FD`
- On primary: `0x001944`
- Primary container: `0x04409F`
- Secondary container/on: `0x004A77` / `0xC2E7FF`
- Tertiary container/on: `0x0F5223` / `0xC3EDCF`
- Error: `0xFD7267`

## Component Mapping

- `Icon-Button`: circular LVGL buttons, 52-60dp source size, used for player controls and close buttons.
- `Button`: pill action, 172x52dp source size, used as the basis for primary tile actions.
- `Button-Compact`: dense pill action, used as the basis for two-column home controls.
- `Toggle+Selection-Buttons`: settings states use selected tonal colors instead of custom green/purple labels.
- `Card`: tonal rounded cards use the kit radius of 26dp conceptually; in LVGL this is implemented as fully rounded grouped containers for the round viewport.
- `Slider`: 172x52dp tonal slider, mapped to the brightness card.
- `Page-Indicator`: replaced text counters with active/inactive dot indicators.
- `Media-Player`: player colors and controls now follow the WM3 dark token set.
- `Grouped containers`: home controls are intentionally arranged as uneven primary/secondary clusters instead of a uniform 2x3 grid.
- `Edge-hugging containers`: bottom clusters use wider rounded forms that visually embrace the circular viewport.

## Constraints

LVGL does not support every Figma component behavior directly, so the mapping prioritizes visible structure, colors, radii, typography, and interaction targets while preserving existing ESPHome IDs and scripts. Native Wear OS shape morphing and scroll-time corner animation remain outside ESPHome LVGL, but static containers should still follow the M3 Expressive visual language.
