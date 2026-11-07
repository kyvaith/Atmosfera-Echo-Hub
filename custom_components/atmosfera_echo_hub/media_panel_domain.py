"""External-media model; no I/O or service calls.

This candidate does not change the dedicated local Player. Volume observation
is independent of the interface's explicit one-percent command grid.
"""

from dataclasses import dataclass
from decimal import Decimal, localcontext
import math

from .choice_domain import (
    ChoiceDomain, ChoiceDomainError, MEDIA_ACTIVE_STATES,
    choice_domain, choice_service, choice_state,
)

MEDIA_ACTION = {"kind": "control", "control": "panel", "property": "media"}
KNOWN_PHASES = MEDIA_ACTIVE_STATES | {"off", "standby"}
FACET_BITS = {"volume": 1, "source": 2, "sound_mode": 4, "repeat": 8}
# Match Core2026.7.1 and existing validated card adapters, including Core's
# relative-volume fallback for VOLUME_SET-only entities.
OP_FEATURES = {
    "play": (16384, "media_play"), "pause": (1, "media_pause"),
    "previous": (16, "media_previous_track"), "next": (32, "media_next_track"),
    "stop": (4096, "media_stop"), "turn_on": (128, "turn_on"),
    "turn_off": (256, "turn_off"), "volume": (4, "volume_set"),
    "volume_up": (4 | 1024, "volume_up"), "volume_down": (4 | 1024, "volume_down"),
    "mute": (8, "volume_mute"), "shuffle": (32768, "shuffle_set"),
}
OP_BITS = {name: 1 << index for index, name in enumerate(OP_FEATURES)}
RAW_VOLUME_BYTES = 24
PERCENT_BYTES = 26


class MediaPanelError(ValueError):
    """Reject a malformed or stale observation; never invent a control."""


def features(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 2**53 - 1 else 0


@dataclass(frozen=True)
class VolumeObservation:
    raw: str
    percent: str
    rail: int


def volume_observation(value):
    """Exact shortest source float representation and decimal percent, no rounding.

The rail is explicitly approximate display geometry in basis points. It is
never an authoritative current value or expected command index.
"""
    if type(value) not in (int, float) or not 0 <= value <= 1:
        return None
    if type(value) is float and not math.isfinite(value):
        return None
    raw = "0" if value == 0 else "1" if value == 1 else repr(value)
    with localcontext() as context:
        context.prec = 40
        number = (Decimal(raw) * 100).normalize()
        fixed = format(number, "f")
        percent = fixed if len(fixed) <= PERCENT_BYTES else format(number, "g").lower()
        rail = int((Decimal(raw) * 10000).to_integral_value())
    if len(raw) > RAW_VOLUME_BYTES or len(percent) > PERCENT_BYTES:
        raise MediaPanelError("unsupported_volume_representation")
    return VolumeObservation(raw, percent, rail)


def excerpt(value, byte_limit):
    """Descriptions may be labelled excerpts; measurements never use this path."""
    if value is None or value == "":
        return "empty", ""
    if type(value) is not str:
        return "invalid", ""
    # Normalize whitespace only. Invalid control/surrogate content is rejected,
    # not silently removed to create a different supposedly complete title.
    normalized = " ".join(value.split())
    if not normalized:
        return "empty", ""
    if not normalized.isprintable():
        return "invalid", ""
    try:
        encoded = normalized.encode("utf8")
    except UnicodeError:
        return "invalid", ""
    if len(encoded) <= byte_limit:
        return "value", normalized
    prefix = encoded[:byte_limit - len("…".encode())].decode("utf8", "ignore").rstrip()
    return "excerpt", prefix + "…"


@dataclass(frozen=True)
class MediaDomain:
    device_type: str
    operations: tuple
    choices: tuple
    reasons: tuple

    @classmethod
    def from_ha(cls, hass, state, language=None):
        from .cards import choice_control_labels

        if not state.entity_id.startswith("media_player."):
            raise MediaPanelError("unsupported_entity")
        caps = features(state.attributes.get("supported_features"))
        operations = tuple(op for op, (flag, service) in OP_FEATURES.items()
                           if caps & flag and hass.services.has_service("media_player", service))
        choices, reasons = [], []
        for facet in ("source", "sound_mode", "repeat"):
            service, _ = choice_service(state.entity_id, facet)
            if not hass.services.has_service("media_player", service):
                reasons.append((facet, "unsupported_service"))
                continue
            try:
                domain = choice_domain(state.entity_id, state.attributes, facet, hass=hass)
                labels = tuple(choice_control_labels(hass, state, domain, facet, language or hass.config.language))
                try:
                    ChoiceDomain(labels)
                except ChoiceDomainError:
                    labels = domain.options
                choices.append((facet, domain, labels))
            except ChoiceDomainError:
                reasons.append((facet, "unsupported_catalogue"))
        device_type = state.attributes.get("device_class")
        return cls(device_type if type(device_type) is str and device_type in {"speaker", "tv", "receiver"} else "generic",
                   operations, tuple(choices), tuple(reasons))

    def descriptor(self):
        return {"device_type": self.device_type, "operations": self.operation_mask, "facets": self.facets}

    @property
    def fingerprint(self):
        import hashlib
        import json
        value = [self.descriptor(), [(name, list(domain.options), list(labels)) for name, domain, labels in self.choices]]
        return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

    @property
    def facets(self):
        return (FACET_BITS["volume"] if "volume" in self.operations else 0) + sum(
            FACET_BITS[name] for name, _, _ in self.choices)

    @property
    def operation_mask(self):
        return sum(OP_BITS[name] for name in self.operations)

    def phase(self, state):
        return str(state.state) if isinstance(state.state, str) and state.state in KNOWN_PHASES else "unknown"

    def source(self, state):
        if state.state == "unavailable":
            return "unavailable"
        return "known" if self.phase(state) != "unknown" else "unknown"

    def volume(self, state):
        if self.phase(state) not in MEDIA_ACTIVE_STATES or not set(self.operations) & {"volume", "volume_up", "volume_down"}:
            return None
        return volume_observation(state.attributes.get("volume_level"))

    def boolean(self, state, operation):
        field = {"mute": "is_volume_muted", "shuffle": "shuffle"}[operation]
        value = state.attributes.get(field)
        return value if operation in self.operations and self.phase(state) in MEDIA_ACTIVE_STATES and type(value) is bool else None

    def choice(self, state, facet):
        for name, domain, _ in self.choices:
            if name == facet:
                return domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, facet))
        return None

    def command_state(self, state):
        volume = self.volume(state)
        return (self.source(state), self.phase(state), volume.raw if volume else None,
                self.boolean(state, "mute"), self.boolean(state, "shuffle"),
                tuple((name, self.choice(state, name)) for name, _, _ in self.choices))

    def allowed_facet(self, facet):
        return facet == "main" or facet in FACET_BITS and bool(self.facets & FACET_BITS[facet])

    def eligible(self, state, operation):
        if operation not in self.operations:
            return False
        phase = self.phase(state)
        if operation == "turn_on":
            return phase in {"off", "standby"}
        if operation == "turn_off":
            return phase in MEDIA_ACTIVE_STATES
        if operation == "play":
            return phase in {"on", "idle", "paused"}
        if operation == "pause":
            return phase in {"playing", "buffering"}
        if operation == "stop":
            return phase in {"playing", "paused", "buffering"}
        if operation in {"volume", "volume_up", "volume_down"}:
            value = self.volume(state)
            if value is None:
                return False
            return (operation != "volume_up" or value.raw != "1") and (operation != "volume_down" or value.raw != "0")
        if operation in {"mute", "shuffle"}:
            return self.boolean(state, operation) is not None
        return phase in MEDIA_ACTIVE_STATES

    def main(self, state):
        volume = self.volume(state)
        known = self.phase(state) in MEDIA_ACTIVE_STATES
        title_status, title = excerpt(state.attributes.get("media_title") if known else None, 128)
        artist_status, artist = excerpt(state.attributes.get("media_artist") if known else None, 96)
        return {"source": self.source(state), "phase": self.phase(state),
                "eligible": sum(OP_BITS[name] for name in self.operations if self.eligible(state, name)),
                "volume_raw": volume.raw if volume else None,
                "volume_percent": volume.percent if volume else "", "volume_rail": volume.rail if volume else None,
                "muted": self.boolean(state, "mute"), "shuffle": self.boolean(state, "shuffle"),
                "title_status": title_status, "media_title": title,
                "artist_status": artist_status, "media_artist": artist}

    def view(self, state, facet, sequence):
        if not self.allowed_facet(facet) or type(sequence) is not int or not 0 <= sequence <= 2**31 - 1:
            raise MediaPanelError("unsupported_view")
        if facet == "main":
            return {"facet": facet, "view_seq": sequence, **self.main(state)}
        if facet == "volume":
            observed = self.volume(state)
            return {"facet": facet, "view_seq": sequence, "source": self.source(state),
                    "editable": self.eligible(state, "volume"), "ui_step_percent": 1,
                    "observed_raw": observed.raw if observed else None,
                    "percent_text": observed.percent if observed else "", "rail": observed.rail if observed else None}
        _, domain, labels = next(item for item in self.choices if item[0] == facet)
        index = self.choice(state, facet)
        return {"facet": facet, "view_seq": sequence, "source": self.source(state),
                "options": list(labels), "index": index, "editable": index is not None}

    def service(self, hass, state, facet, operation, target=None):
        """Resolve an exact fixed intent after live validation, without dispatch."""
        from .cards import validate_live_action

        if not self.allowed_facet(facet):
            raise MediaPanelError("unsupported_view")
        if operation == "choice":
            if facet not in {name for name, _, _ in self.choices} or self.choice(state, facet) is None:
                raise MediaPanelError("unknown_current")
            _, domain, _ = next(item for item in self.choices if item[0] == facet)
            if type(target) is not int or target == self.choice(state, facet):
                raise MediaPanelError("invalid_target")
            service, field = choice_service(state.entity_id, facet)
            data = {field: domain.value_at(target)}
        else:
            if facet != ("volume" if operation == "volume" else "main") or not self.eligible(state, operation):
                raise MediaPanelError("ineligible")
            service = OP_FEATURES[operation][1]
            if operation == "volume":
                if type(target) is not int or not 0 <= target <= 100:
                    raise MediaPanelError("invalid_target")
                value = target / 100
                if volume_observation(value).raw == self.volume(state).raw:
                    raise MediaPanelError("unchanged_target")
                data = {"volume_level": value}
            elif operation in {"mute", "shuffle"}:
                if type(target) is not bool or target == self.boolean(state, operation):
                    raise MediaPanelError("invalid_target")
                data = {{"mute": "is_volume_muted", "shuffle": "shuffle"}[operation]: target}
            else:
                if target is not None:
                    raise MediaPanelError("unexpected_target")
                data = {}
        validate_live_action(hass, state, {"service": "media_player." + service, "data": data})
        return "media_player", service, data

    def matches(self, state, facet, operation, target=None):
        """Observed postcondition only; owner must require a fresh source event."""
        phase = self.phase(state)
        if operation in {"previous", "next", "volume_up", "volume_down"}:
            return False
        if operation == "play":
            return phase == "playing"
        if operation == "pause":
            return phase == "paused"
        if operation == "stop":
            return phase in {"off", "idle", "standby"}
        if operation == "turn_on":
            return phase in MEDIA_ACTIVE_STATES
        if operation == "turn_off":
            return phase in {"off", "standby"}
        if operation in {"mute", "shuffle"}:
            return type(target) is bool and self.boolean(state, operation) is target
        if operation == "volume":
            return type(target) is int and 0 <= target <= 100 and self.volume(state) == volume_observation(target / 100)
        if operation == "choice":
            return type(target) is int and self.choice(state, facet) == target
        return False


def media_metadata(hass, state, language=None):
    if not state.entity_id.startswith("media_player."):
        return {}
    domain = MediaDomain.from_ha(hass, state, language)
    return {"media_panel": {"version": 1, "caps": domain.descriptor(), "fingerprint": domain.fingerprint,
                            "state": domain.main(state), "unsupported_facets": dict(domain.reasons)}}
