"""Exact bounded options for the opt-in choice controller; no I/O or services."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from homeassistant.components.fan import DATA_COMPONENT as FAN_COMPONENT

MAX_OPTIONS = 8
MAX_OPTION_BYTES = 32
MEDIA_REPEAT_MODES = ("off", "one", "all")
MEDIA_ACTIVE_STATES = frozenset(("on", "idle", "playing", "paused", "buffering"))
HVAC_MODES = frozenset(("off", "heat", "cool", "heat_cool", "auto", "dry", "fan_only"))
VACUUM_STATES = frozenset(("cleaning", "docked", "idle", "paused", "returning", "error"))


def choice_service(entity_id: str, property: str | None = None) -> tuple[str, str]:
    """Product adapter chooses the operation; clients never supply service names."""
    domain = entity_id.partition(".")[0]
    if property is not None:
        if domain == "media_player" and property == "repeat":
            return "repeat_set", "repeat"
        if domain == "media_player" and property == "sound_mode":
            return "select_sound_mode", "sound_mode"
        if domain == "media_player" and property == "source":
            return "select_source", "source"
        if domain == "remote" and property == "activity":
            return "turn_on", "activity"
        if domain == "vacuum" and property == "fan_speed":
            return "set_fan_speed", "fan_speed"
        if domain == "fan" and property == "percentage":
            return "set_percentage", "percentage"
        if domain == "light" and property == "effect":
            return "turn_on", "effect"
        if domain == "fan" and property == "direction":
            return "set_direction", "direction"
        if domain == "climate" and property == "hvac_mode":
            return "set_hvac_mode", "hvac_mode"
        if domain == "climate" and property == "preset_mode":
            return "set_preset_mode", "preset_mode"
        if domain == "climate" and property == "fan_mode":
            return "set_fan_mode", "fan_mode"
        if domain == "climate" and property == "swing_mode":
            return "set_swing_mode", "swing_mode"
        if domain == "climate" and property == "swing_horizontal_mode":
            return "set_swing_horizontal_mode", "swing_horizontal_mode"
        if domain == "humidifier" and property == "mode":
            return "set_mode", "mode"
        raise ChoiceDomainError("unsupported_property")
    if domain in {"select", "input_select"}:
        return "select_option", "option"
    if domain == "fan":
        return "set_preset_mode", "preset_mode"
    raise ChoiceDomainError("unsupported_entity")


def fan_speed_options(hass, entity_id: str, attributes: Any) -> tuple[str, ...]:
    """Read a loaded fan's real speed count and use Core's own uneven mapping."""
    if not isinstance(attributes, Mapping):
        raise ChoiceDomainError("fan_speed_attributes")
    features = attributes.get("supported_features")
    if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 1:
        raise ChoiceDomainError("fan_speed_unsupported")
    component = getattr(hass, "data", {}).get(FAN_COMPONENT)
    lookup = getattr(component, "get_entity", None)
    entity = lookup(entity_id) if callable(lookup) else None
    count = getattr(entity, "speed_count", None)
    step = attributes.get("percentage_step")
    if (getattr(entity, "entity_id", None) != entity_id or type(count) is not int or not 1 <= count < MAX_OPTIONS
            or type(step) not in (int, float) or step != 100 / count):
        raise ChoiceDomainError("fan_speed_count_unknown_or_mismatch")
    # Imported only for an admitted loaded fan, not for generic option metadata.
    from homeassistant.util.percentage import (
        percentage_to_ranged_value,
        ranged_value_to_percentage,
    )

    values = (0, *(ranged_value_to_percentage((1, count), index) for index in range(1, count + 1)))
    if (any(type(value) is not int or not 0 <= value <= 100 for value in values)
            or values[-1] != 100 or any(left >= right for left, right in zip(values, values[1:], strict=False))
            or any(math.ceil(percentage_to_ranged_value((1, count), value)) != index for index, value in enumerate(values))):
        raise ChoiceDomainError("fan_speed_mapping")
    return tuple(str(value) for value in values)


def choice_domain(entity_id: str, attributes: Any, property: str | None = None, *, hass=None) -> ChoiceDomain:
    """Use a fan's preset catalogue only when its actual capability allows it."""
    choice_service(entity_id, property)
    if property == "repeat":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**53 - 1 or not features & 262144:
            raise ChoiceDomainError("media_repeat_unsupported")
        return ChoiceDomain(MEDIA_REPEAT_MODES)
    if property == "source":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**53 - 1 or not features & 2048:
            raise ChoiceDomainError("media_source_unsupported")
        return ChoiceDomain.from_options(attributes.get("source_list"))
    if property == "sound_mode":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**53 - 1 or not features & 65536:
            raise ChoiceDomainError("media_sound_mode_unsupported")
        return ChoiceDomain.from_options(attributes.get("sound_mode_list"))
    if property == "activity":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**53 - 1 or not features & 4:
            raise ChoiceDomainError("remote_activity_unsupported")
        return ChoiceDomain.from_options(attributes.get("activity_list"))
    if property == "fan_speed":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 32:
            raise ChoiceDomainError("vacuum_fan_speed_unsupported")
        return ChoiceDomain.from_options(attributes.get("fan_speed_list"))
    if property == "percentage":
        return ChoiceDomain(fan_speed_options(hass, entity_id, attributes))
    if property == "effect":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 4:
            raise ChoiceDomainError("light_effect_unsupported")
        return ChoiceDomain.from_options(attributes.get("effect_list"))
    if property == "mode":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 1:
            raise ChoiceDomainError("humidifier_mode_unsupported")
        return ChoiceDomain.from_options(attributes.get("available_modes"))
    if property == "hvac_mode":
        options = attributes.get("hvac_modes") if isinstance(attributes, Mapping) else None
        if type(options) is not list or not 1 <= len(options) <= MAX_OPTIONS:
            raise ChoiceDomainError("hvac_modes_size")
        if any(not isinstance(value, str) or value not in HVAC_MODES or str(value) not in HVAC_MODES for value in options):
            raise ChoiceDomainError("hvac_mode_unknown")
        return ChoiceDomain.from_options([str(value) for value in options])
    if property == "fan_mode":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 8:
            raise ChoiceDomainError("fan_mode_unsupported")
        return ChoiceDomain.from_options(attributes.get("fan_modes"))
    if property == "swing_mode":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 32:
            raise ChoiceDomainError("swing_mode_unsupported")
        return ChoiceDomain.from_options(attributes.get("swing_modes"))
    if property == "swing_horizontal_mode":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 512:
            raise ChoiceDomainError("swing_horizontal_mode_unsupported")
        return ChoiceDomain.from_options(attributes.get("swing_horizontal_modes"))
    if property == "preset_mode":
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 16:
            raise ChoiceDomainError("preset_unsupported")
        return ChoiceDomain.from_options(attributes.get("preset_modes"))
    if entity_id.startswith("fan."):
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        features = attributes.get("supported_features")
        feature = 4 if property == "direction" else (1 | 8)
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & feature:
            raise ChoiceDomainError("preset_unsupported")
        if property == "direction":
            return ChoiceDomain(("forward", "reverse"))
        return ChoiceDomain.from_options(attributes.get("preset_modes"))
    return ChoiceDomain.from_ha(attributes)


def choice_state(entity_id: str, state: Any, attributes: Any, property: str | None = None) -> Any:
    """Fan power is not its selected preset; outages never expose a stale preset."""
    if entity_id.startswith("media_player.") and property == "repeat":
        value = attributes.get("repeat") if isinstance(state, str) and state in MEDIA_ACTIVE_STATES and isinstance(attributes, Mapping) else None
        return str(value) if isinstance(value, str) and value in MEDIA_REPEAT_MODES else None
    if entity_id.startswith("media_player.") and property == "source":
        return attributes.get("source") if isinstance(state, str) and state in MEDIA_ACTIVE_STATES and isinstance(attributes, Mapping) else None
    if entity_id.startswith("media_player.") and property == "sound_mode":
        return attributes.get("sound_mode") if isinstance(state, str) and state in MEDIA_ACTIVE_STATES and isinstance(attributes, Mapping) else None
    if entity_id.startswith("remote.") and property == "activity":
        return attributes.get("current_activity") if type(state) is str and state == "on" and isinstance(attributes, Mapping) else None
    if entity_id.startswith("vacuum.") and property == "fan_speed":
        return attributes.get("fan_speed") if isinstance(attributes, Mapping) and isinstance(state, str) and state in VACUUM_STATES else None
    if entity_id.startswith("fan.") and property == "percentage":
        value = attributes.get("percentage") if isinstance(attributes, Mapping) and isinstance(state, str) and state in {"on", "off"} else None
        return str(value) if type(value) is int and 0 <= value <= 100 else None
    if entity_id.startswith("light.") and property == "effect":
        return attributes.get("effect") if type(state) is str and state == "on" and isinstance(attributes, Mapping) else None
    if entity_id.startswith("humidifier.") and property == "mode":
        return attributes.get("mode") if type(state) is str and state in {"on", "off"} and isinstance(attributes, Mapping) else None
    if entity_id.startswith("climate.") and property == "hvac_mode":
        return state if type(state) is str and state in HVAC_MODES else None
    if entity_id.startswith("climate.") and property == "fan_mode":
        return attributes.get("fan_mode") if type(state) is str and state in HVAC_MODES and isinstance(attributes, Mapping) else None
    if entity_id.startswith("climate.") and property == "swing_mode":
        return attributes.get("swing_mode") if type(state) is str and state in HVAC_MODES and isinstance(attributes, Mapping) else None
    if entity_id.startswith("climate.") and property == "swing_horizontal_mode":
        return attributes.get("swing_horizontal_mode") if type(state) is str and state in HVAC_MODES and isinstance(attributes, Mapping) else None
    if entity_id.startswith("climate.") and property == "preset_mode":
        return attributes.get("preset_mode") if type(state) is str and state in HVAC_MODES and isinstance(attributes, Mapping) else None
    if entity_id.startswith("fan."):
        field = "direction" if property == "direction" else "preset_mode"
        return attributes.get(field) if isinstance(attributes, Mapping) and isinstance(state, str) and state in {"on", "off"} else None
    return state


def choice_is_empty(entity_id: str, state: Any, attributes: Any, property: str | None = None) -> bool:
    """Explicit known inactive presets differ from unavailable/missing values."""
    if property == "activity" and entity_id.startswith("remote."):
        return type(state) is str and state == "off"
    if property == "effect" and entity_id.startswith("light."):
        return (type(state) is str and state in {"on", "off"} and isinstance(attributes, Mapping)
                and "effect" in attributes and attributes["effect"] is None)
    if (property == "preset_mode" and entity_id.startswith("climate.") and type(state) is str and state in HVAC_MODES
            and isinstance(attributes, Mapping) and "preset_mode" in attributes):
        value = attributes["preset_mode"]
        return value is None or (type(value) is str and value == "none" and type(attributes.get("preset_modes")) is list and "none" not in attributes["preset_modes"])
    return (property is None and entity_id.startswith("fan.") and isinstance(state, str) and state in {"on", "off"}
            and isinstance(attributes, Mapping) and "preset_mode" in attributes
            and attributes["preset_mode"] is None)


def choice_labels(domain: ChoiceDomain, property: str | None, language: str) -> tuple[str, ...]:
    """Presentation only; canonical service values never come from translations."""
    if property == "fan_speed":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        names = {"quiet": ("Quiet", "Cicha"), "silent": ("Silent", "Cicha"), "normal": ("Normal", "Normalna"),
                 "standard": ("Standard", "Standardowa"), "turbo": ("Turbo", "Turbo"), "eco": ("Eco", "Eco"),
                 "max": ("Maximum", "Maksymalna"), "strong": ("Strong", "Silna"), "gentle": ("Gentle", "Delikatna"), "off": ("Off", "Wyłączona")}
        labels = tuple(names[value][int(polish)] if value in names else value for value in domain.options)
        return labels if len(set(labels)) == len(labels) else domain.options
    if property == "repeat":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        labels = {"off": ("Off", "Wyłączone"), "one": ("One track", "Jeden utwór"), "all": ("All tracks", "Cała kolejka")}
        return tuple(labels[value][int(polish)] for value in domain.options)
    if property == "percentage":
        return tuple(value + " %" for value in domain.options)
    if property == "mode":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        names = {"normal": ("Normal", "Normalny"), "eco": ("Eco", "Eco"), "away": ("Away", "Poza domem"),
                 "boost": ("Boost", "Przyspieszenie"), "comfort": ("Comfort", "Komfort"), "home": ("Home", "W domu"),
                 "sleep": ("Sleep", "Sen"), "auto": ("Automatic", "Automatyczny"), "baby": ("Baby", "Dla dziecka")}
        labels = tuple(names[value][int(polish)] if value in names else value for value in domain.options)
        return labels if len(set(labels)) == len(labels) else domain.options
    if property == "direction":
        return ("Do przodu", "Wstecz") if language.replace("_", "-").split("-")[0].lower() == "pl" else ("Forward", "Reverse")
    if property == "hvac_mode":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        labels = {"off": ("Off", "Wyłączone"), "heat": ("Heating", "Ogrzewanie"), "cool": ("Cooling", "Chłodzenie"),
                  "heat_cool": ("Heat/cool", "Grzanie/chłodzenie"), "auto": ("Automatic", "Automatyczny"),
                  "dry": ("Drying", "Osuszanie"), "fan_only": ("Fan only", "Wentylator")}
        return tuple(labels[value][int(polish)] for value in domain.options)
    if property == "fan_mode":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        names = {"auto": ("Automatic", "Automatyczny"), "low": ("Low", "Niski"), "medium": ("Medium", "Średni"),
                 "high": ("High", "Wysoki"), "on": ("On", "Włączony"), "off": ("Off", "Wyłączony"),
                 "top": ("Top", "Górny"), "middle": ("Middle", "Środkowy"), "focus": ("Focused", "Skupiony"), "diffuse": ("Diffuse", "Rozproszony")}
        labels = tuple(names[value][int(polish)] if value in names else value for value in domain.options)
        return labels if len(set(labels)) == len(labels) else domain.options
    if property == "swing_mode":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        names = {"off": ("Off", "Wyłączone"), "on": ("On", "Włączone"), "vertical": ("Vertical", "Pionowo"),
                 "horizontal": ("Horizontal", "Poziomo"), "both": ("Both axes", "Obie osie")}
        labels = tuple(names[value][int(polish)] if value in names else value for value in domain.options)
        return labels if len(set(labels)) == len(labels) else domain.options
    if property == "swing_horizontal_mode":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        names = {"off": ("Off", "Wyłączone"), "on": ("On", "Włączone")}
        labels = tuple(names[value][int(polish)] if value in names else value for value in domain.options)
        return labels if len(set(labels)) == len(labels) else domain.options
    if property == "preset_mode":
        polish = language.replace("_", "-").split("-")[0].lower() == "pl"
        names = {"none": ("No program", "Bez programu"), "eco": ("Eco", "Eco"), "away": ("Away", "Poza domem"),
                 "boost": ("Boost", "Przyspieszenie"), "comfort": ("Comfort", "Komfort"), "home": ("Home", "W domu"),
                 "sleep": ("Sleep", "Sen"), "activity": ("Activity", "Aktywność")}
        labels = tuple(names[value][int(polish)] if value in names else value for value in domain.options)
        return labels if len(set(labels)) == len(labels) else domain.options
    return domain.options


class ChoiceDomainError(ValueError):
    """Unsupported option domain or stale observation; never silently repair it."""


@dataclass(frozen=True, slots=True)
class ChoiceDomain:
    """Keep exact service values and ordering in one immutable bounded tuple."""

    options: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.options) is not tuple or not 1 <= len(self.options) <= MAX_OPTIONS:
            raise ChoiceDomainError("options_size")
        for value in self.options:
            if (
                type(value) is not str
                or not value
                or not value.isprintable()
                or value in {"unknown", "unavailable"}
            ):
                raise ChoiceDomainError("option_text")
            try:
                size = len(value.encode("utf-8"))
            except UnicodeError as error:
                raise ChoiceDomainError("option_text") from error
            if size > MAX_OPTION_BYTES:
                raise ChoiceDomainError("option_size")
        if len(set(self.options)) != len(self.options):
            raise ChoiceDomainError("duplicate_option")

    @classmethod
    def from_options(cls, options: Any) -> ChoiceDomain:
        """Wire and HA arrays must be actual lists, not arbitrary iterables."""
        if type(options) is not list or not 1 <= len(options) <= MAX_OPTIONS:
            raise ChoiceDomainError("options_type_or_size")
        return cls(tuple(options))

    @classmethod
    def from_ha(cls, attributes: Any) -> ChoiceDomain:
        if not isinstance(attributes, Mapping):
            raise ChoiceDomainError("attributes_type")
        return cls.from_options(attributes.get("options"))

    def observed_index(self, state: Any) -> int | None:
        if type(state) is not str or state in {"unknown", "unavailable"}:
            return None
        try:
            return self.options.index(state)
        except ValueError:
            return None

    def value_at(self, index: Any) -> str:
        if type(index) is not int or not 0 <= index < len(self.options):
            raise ChoiceDomainError("option_index")
        return self.options[index]

    def service_value(self, index: Any, *, current: ChoiceDomain) -> str:
        if type(current) is not ChoiceDomain or current != self:
            raise ChoiceDomainError("options_changed")
        return self.value_at(index)
