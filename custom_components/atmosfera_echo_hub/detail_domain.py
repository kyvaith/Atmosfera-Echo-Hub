"""Bounded Light/Climate facets; pure metadata/observations, no service calls."""

from dataclasses import dataclass
import hashlib
import json
import math

from .choice_domain import ChoiceDomain, ChoiceDomainError, HVAC_MODES, choice_domain, choice_is_empty, choice_service, choice_state
from .number_domain import THERMOSTAT_ACTIVITIES, number_domain, number_service, number_state
from .numeric_domain import NumericDomainError
from .light_color_domain import ColorDomain, ColorDomainError
from .climate_range_domain import RangeDomain, RangeDomainError

LIGHT_ACTION = {"kind": "control", "control": "light", "detail": 1}
CLIMATE_ACTION = {"kind": "control", "control": "panel", "property": "climate"}
LIGHT_BITS = {"color_temp_kelvin": 1, "effect": 2, "color": 4}
CLIMATE_BITS = {"temperature": 1, "humidity": 2, "hvac_mode": 4, "preset_mode": 8,
                "fan_mode": 16, "swing_mode": 32, "swing_horizontal_mode": 64, "range": 128}
FACETS = {"light": ("main", *LIGHT_BITS), "climate": ("main", *tuple(CLIMATE_BITS)[1:])}
NUMBERS = {"temperature", "humidity", "color_temp_kelvin"}
REASONS = {"unsupported_metadata", "unsupported_service", "unsupported_catalogue"}


class DetailDomainError(ValueError):
    """Unsupported source metadata; never fabricate a capability."""


def measurement(value, minimum, maximum):
    if type(value) not in (int, float) or not math.isfinite(value) or not minimum <= value <= maximum:
        return ""
    return format(round(value, 6) or 0, ".6f").rstrip("0").rstrip(".")


def brightness(state, caps):
    if not caps["brightness"]:
        return None
    if state.state == "off":
        return 0
    raw = state.attributes.get("brightness")
    return (raw * 100 + 127) // 255 if type(raw) is int and 0 <= raw <= 255 else None


@dataclass(frozen=True)
class DetailDomain:
    family: str
    unit: str | None
    numbers: tuple
    choices: tuple
    light_caps: tuple = ()
    range_supported: bool = False
    reasons: tuple = ()
    display_limits: tuple = ("", "")
    color: ColorDomain | None = None
    range_domain: RangeDomain | None = None

    @classmethod
    def from_ha(cls, hass, state, language=None, *, color=False, range_enabled=False):
        # Local import keeps catalogue composition and pure models acyclic.
        from .cards import choice_control_labels
        from .light_control import light_capabilities

        family = state.entity_id.partition(".")[0]
        if family not in FACETS:
            raise DetailDomainError("unsupported")
        unit = getattr(getattr(hass.config, "units", None), "temperature_unit", None)
        unit = str(unit) if unit in {"°C", "°F"} else None
        numeric, choices, reasons = [], [], []
        bits = LIGHT_BITS if family == "light" else CLIMATE_BITS
        light_caps = tuple(sorted(light_capabilities(hass, state).items())) if family == "light" else ()
        for facet in bits:
            if facet in {"color", "range"}:
                continue
            try:
                if facet in NUMBERS:
                    service_domain, service, _ = number_service(state.entity_id, facet)
                    if not hass.services.has_service(service_domain, service):
                        reasons.append((facet, "unsupported_service"))
                        continue
                    numeric.append((facet, number_domain(hass, state, facet)))
                else:
                    service, _ = choice_service(state.entity_id, facet)
                    if not hass.services.has_service(family, service):
                        reasons.append((facet, "unsupported_service"))
                        continue
                    domain = choice_domain(state.entity_id, state.attributes, facet, hass=hass)
                    labels = tuple(choice_control_labels(hass, state, domain, facet, language or hass.config.language))
                    try:
                        ChoiceDomain(labels)
                    except ChoiceDomainError:
                        labels = domain.options
                    choices.append((facet, domain, labels))
            except NumericDomainError:
                reasons.append((facet, "unsupported_metadata"))
            except ChoiceDomainError:
                reasons.append((facet, "unsupported_catalogue"))
        features = state.attributes.get("supported_features")
        range_supported = family == "climate" and isinstance(features, int) and not isinstance(features, bool) and features >= 0 and bool(features & 2)
        minimum = measurement(state.attributes.get("min_temp"), -100, 300) if family == "climate" and unit else ""
        maximum = measurement(state.attributes.get("max_temp"), -100, 300) if family == "climate" and unit else ""
        if not minimum or not maximum or float(minimum) >= float(maximum):
            minimum = maximum = ""
        color_domain = None
        if family == "light" and color:
            try:
                color_domain = ColorDomain.from_ha(hass, state)
            except ColorDomainError:
                reasons.append(("color", "unsupported_metadata"))
        range_domain = None
        if family == "climate" and range_enabled:
            try:
                range_domain = RangeDomain.from_ha(hass, state)
            except RangeDomainError:
                reasons.append(("range", "unsupported_metadata"))
        return cls(family, unit if family == "climate" else None, tuple(numeric), tuple(choices), light_caps,
                   range_supported, tuple(reasons), (minimum, maximum), color_domain, range_domain)

    @property
    def mask(self):
        bits = LIGHT_BITS if self.family == "light" else CLIMATE_BITS
        return (sum(bits[name] for name in dict(self.numbers)) + sum(bits[name] for name, _, _ in self.choices)
                + (LIGHT_BITS["color"] if self.color is not None else 0)
                + (CLIMATE_BITS["range"] if self.range_domain is not None else 0))

    @property
    def fingerprint(self):
        value = {"family": self.family, "unit": self.unit, "range": self.range_supported,
                 "numbers": {name: domain.descriptor() for name, domain in self.numbers},
                 "choices": {name: [list(domain.options), list(labels)] for name, domain, labels in self.choices},
                 "light_caps": dict(self.light_caps), "reasons": dict(self.reasons), "display_limits": self.display_limits}
        if self.color is not None:
            value["color"] = {"modes": self.color.modes, "write_mode": self.color.write_mode}
        if self.range_domain is not None:
            value["range_domain"] = self.range_domain.domain.descriptor()
        return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

    def allowed_facet(self, facet):
        if facet == "main":
            return True
        return facet in FACETS[self.family] and bool(self.mask & (LIGHT_BITS if self.family == "light" else CLIMATE_BITS)[facet])

    def property(self, facet):
        return "temperature" if self.family == "climate" and facet == "main" else facet

    def known(self, state):
        return state.state in (HVAC_MODES if self.family == "climate" else {"on", "off"})

    def observed(self, state, facet):
        prop = self.property(facet)
        if prop in dict(self.numbers):
            domain = dict(self.numbers)[prop]
            index = domain.observed_index(number_state(state, prop)) if self.known(state) else None
            return index, index is not None
        for name, domain, _ in self.choices:
            if name == prop:
                index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, prop)) if self.known(state) else None
                known = self.known(state) and (index is not None or choice_is_empty(state.entity_id, state.state, state.attributes, prop))
                return index, bool(known)
        return None, False

    def command_state(self, state):
        numeric = tuple((name, *self.observed(state, "main" if name == "temperature" else name)) for name, _ in self.numbers)
        choices = tuple((name, *self.observed(state, name)) for name, _, _ in self.choices)
        extra = (brightness(state, dict(self.light_caps)), state.attributes.get("color_mode")) if self.family == "light" else ()
        if self.color is not None:
            extra += (self.color.observation(state),)
        if self.family == "climate":
            main = self.main(state)
            extra = (main["target"], main["low"], main["high"])
            if self.range_domain is not None:
                extra += (self.range_domain.observation(state),)
        return (state.state if self.known(state) else "unknown", numeric, choices, extra)

    def main(self, state):
        if self.family == "light":
            return {"on": state.state == "on", "brightness_pct": brightness(state, dict(self.light_caps)), "caps": dict(self.light_caps)}
        known = self.known(state)
        attrs = state.attributes
        text = lambda key: measurement(attrs.get(key), -100, 300) if known and self.unit else ""
        activity = attrs.get("hvac_action") if known else None
        if activity not in THERMOSTAT_ACTIVITIES:
            activity = "off" if state.state == "off" else "unknown"
        domain = dict(self.numbers).get("temperature")
        index, editable = self.observed(state, "main")
        minimum, maximum = self.display_limits
        return {"unit": self.unit, "mode": state.state if known else "unknown", "activity": activity,
                "target": text("temperature") if not self.range_supported else "", "current": text("current_temperature"),
                "low": text("target_temp_low") if self.range_supported else "", "high": text("target_temp_high") if self.range_supported else "",
                "min": minimum, "max": maximum, "domain": domain.descriptor() if domain else None,
                "index": index, "editable": editable}

    def view(self, state, facet, sequence):
        if not self.allowed_facet(facet):
            raise DetailDomainError("unsupported")
        value = {"facet": facet, "view_seq": sequence}
        if facet == "main":
            return value | (self.main(state) if self.family == "climate" else {})
        if facet == "color":
            return value
        if facet == "range":
            return value | self.range_domain.source(state)
        prop = self.property(facet)
        index, known = self.observed(state, facet)
        if prop in dict(self.numbers):
            domain = dict(self.numbers)[prop]
            return value | {"domain": domain.descriptor(), "index": index, "editable": known,
                            "value_text": str(domain.value_at(index)) if index is not None else "--",
                            "current_text": measurement(state.attributes.get("current_humidity"), 0, 100)
                            if prop == "humidity" and self.known(state) else ""}
        _, domain, labels = next(value for value in self.choices if value[0] == prop)
        return value | {"options": list(labels), "index": index, "choice_known": known, "editable": known}

    def metadata(self, state):
        return {"version": 1, "facets": self.mask, "fingerprint": self.fingerprint,
                "facet_reasons": dict(self.reasons), "state": self.main(state)}

    def service(self, state, facet, operation, target):
        if not self.allowed_facet(facet):
            raise DetailDomainError("unsupported")
        prop = self.property(facet)
        if operation == "facet_number" and prop in dict(self.numbers):
            numeric = dict(self.numbers)[prop]
            domain, name, field = number_service(state.entity_id, prop)
            return domain, name, {field: numeric.service_value(target, current=numeric)}
        if operation == "facet_choice":
            for name, domain, _ in self.choices:
                if name == prop:
                    service, field = choice_service(state.entity_id, prop)
                    return self.family, service, {field: domain.value_at(target)}
        raise DetailDomainError("unsupported")
