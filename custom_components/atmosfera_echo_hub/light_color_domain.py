"""Authoritative Light color metadata and absolute HS targets; no service calls."""

from dataclasses import dataclass
import math

MODES = frozenset(("rgb", "hs", "xy", "color_temp"))
REASONS = frozenset(("none", "off", "unsupported_mode", "invalid_color", "invalid_brightness", "source_unavailable"))
COLOR_BIT = 4


class ColorDomainError(ValueError):
    """Unknown/unsupported color must never become a fabricated target."""


def triple(value):
    return tuple(value) if (isinstance(value, (list, tuple)) and len(value) == 3
                           and all(type(x) is int and 0 <= x <= 255 for x in value)) else None


def coordinates(value, maxima):
    if (not isinstance(value, (list, tuple)) or len(value) != len(maxima)
            or any(type(x) not in (int, float) or not math.isfinite(x) or not 0 <= x <= maximum
                   for x, maximum in zip(value, maxima, strict=True))):
        return None
    return tuple(value)


def target(hue, saturation):
    if type(hue) is not int or not 0 <= hue <= 359999 or type(saturation) is not int or not 0 <= saturation <= 100000:
        raise ColorDomainError("target")
    return hue, saturation


@dataclass(frozen=True)
class ColorDomain:
    modes: tuple[str, ...]
    write_mode: str

    @classmethod
    def from_ha(cls, hass, state):
        modes = state.attributes.get("supported_color_modes")
        valid = MODES | {"rgbw", "rgbww", "white", "brightness", "onoff"}
        if (not isinstance(modes, (list, tuple, set, frozenset)) or not modes
                or any(not isinstance(x, str) or x not in valid for x in modes)
                or len(set(modes)) != len(modes) or {"rgbw", "rgbww", "onoff", "brightness"}.intersection(modes)
                or not hass.services.has_service("light", "turn_on")):
            raise ColorDomainError("unsupported")
        route = next((mode for mode in ("hs", "rgb", "xy") if mode in modes), None)
        if route is None:
            raise ColorDomainError("unsupported")
        return cls(tuple(sorted(str(mode) for mode in modes)), route)

    def source(self, state):
        attrs = state.attributes
        rgb, hs = triple(attrs.get("rgb_color")), coordinates(attrs.get("hs_color"), (360, 100))
        actual = attrs.get("color_mode")
        mode = str(actual) if isinstance(actual, str) and actual in MODES else ("unknown" if actual is None else "other")
        if state.state not in ("on", "off"):
            mode, reason = "unknown", "source_unavailable"
        elif state.state == "off":
            mode, reason = "unknown", "off"
        elif mode not in MODES:
            reason = "unsupported_mode"
        elif mode not in self.modes or rgb is None or hs is None:
            reason = "invalid_color"
        elif type(attrs.get("brightness")) is not int or not 1 <= attrs["brightness"] <= 255:
            reason = "invalid_brightness"
        else:
            reason = "none"
        known = reason in ("none", "invalid_brightness")
        return {"version": 1, "write_mode": self.write_mode, "source_mode": mode,
                "rgb": list(rgb) if known else None,
                "hue_milli": round(hs[0] * 1000) % 360000 if known else None,
                "saturation_milli": round(hs[1] * 1000) if known else None,
                "editable": reason == "none", "reason": reason}

    def observation(self, state):
        source = self.source(state)
        brightness = state.attributes.get("brightness")
        brightness = brightness if type(brightness) is int and 0 <= brightness <= 255 else None
        xy = coordinates(state.attributes.get("xy_color"), (1, 1))
        hs = coordinates(state.attributes.get("hs_color"), (360, 100))
        effect = state.attributes.get("effect")
        effect = effect if isinstance(effect, str) else None
        return (state.state, source["source_mode"], tuple(source["rgb"]) if source["rgb"] is not None else None,
                source["hue_milli"], source["saturation_milli"], hs, xy, brightness, effect, source["reason"])

    def projection(self, hue, saturation):
        hue, saturation = target(hue, saturation)
        # Core owns supported-space conversion. No replacement color engine here.
        from homeassistant.util import color as color_util

        hs = hue / 1000, saturation / 1000
        if self.write_mode == "xy":
            return tuple(color_util.color_xy_to_RGB(*color_util.color_hs_to_xy(*hs)))
        return tuple(color_util.color_hs_to_RGB(*hs))

    def service(self, state, hue, saturation):
        hue, saturation = target(hue, saturation)
        source = self.source(state)
        if not source["editable"]:
            raise ColorDomainError("unavailable")
        return {"hs_color": [hue / 1000, saturation / 1000], "brightness": state.attributes["brightness"]}

    def matches(self, state, hue, saturation, brightness):
        source = self.source(state)
        return (source["editable"] and source["source_mode"] == self.write_mode
                and state.attributes.get("brightness") == brightness
                and tuple(source["rgb"]) == self.projection(hue, saturation))

    def unchanged(self, state, hue, saturation):
        source = self.source(state)
        return (source["editable"] and source["source_mode"] != "color_temp"
                and ((hue, saturation) == (source["hue_milli"], source["saturation_milli"])
                     or tuple(source["rgb"]) == self.projection(hue, saturation)))
