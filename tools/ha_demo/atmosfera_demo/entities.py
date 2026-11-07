"""Select simulation-only entities from the locally installed HA Core demos."""

from importlib import import_module

from homeassistant.components.climate import ClimateEntityFeature

DEMO_PLATFORMS = {
    "alarm_control_panel": ((0, "alarm"),),
    "binary_sensor": ((0, "contact"),),
    "button": ((0, "button"),),
    "calendar": ((0, "agenda"),),
    "camera": ((0, "camera"),),
    "climate": ((1, "thermostat"), (2, "climate_presets")),
    "cover": ((2, "blind"), (3, "garage")),
    "fan": ((2, "fan"), (4, "fan_presets")),
    "humidifier": ((0, "humidity"), (2, "humidity_modes")),
    "light": ((0, "effects"), (1, "light")),
    "lock": ((0, "lock"),),
    "media_player": ((2, "music"), (4, "tv")),
    "number": ((0, "number"),),
    "select": ((0, "options"),),
    "sensor": ((0, "sensor"),),
    "switch": ((0, "switch"),),
    "vacuum": ((0, "vacuum"),),
}


def demo_platform(domain):
    async def setup(hass, entry, add):
        def select(entities, update_before_add=False):
            entities = list(entities)
            selected = []
            for index, slug in DEMO_PLATFORMS[domain]:
                entity = entities[index]
                entity.entity_id = f"{domain}.atmosfera_demo_{slug}"
                if slug == "thermostat":
                    entity._attr_supported_features &= ~ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
                    entity._attr_target_temperature_step = 0.5
                    entity._attr_max_humidity = 100
                    entity._target_humidity = 65
                elif slug == "climate_presets":
                    entity._attr_target_temperature_step = 0.5
                selected.append(entity)
            add(selected, update_before_add)

        await import_module(f"homeassistant.components.demo.{domain}").async_setup_entry(
            hass, entry, select
        )

    return setup
