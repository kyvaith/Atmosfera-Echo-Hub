"""One optional Core2026.11 schema read, bounded before materialization."""

from dataclasses import dataclass
import math

from .statistics_domain import StatisticsError, dataset_digest


@dataclass(frozen=True)
class Dataset:
    fields: dict
    digest: str


def ready_recorder(hass):
    # Optional dependency requirements are installed through after_dependencies.
    from homeassistant.helpers.recorder import DATA_INSTANCE, get_instance
    if DATA_INSTANCE not in hass.data:
        raise StatisticsError("recorder_missing")
    instance = get_instance(hass)
    ready = instance.async_db_ready
    if (not ready.done() or ready.cancelled() or ready.exception() is not None
            or ready.result() is not True or not instance.is_running):
        raise StatisticsError("recorder_unavailable")
    return instance


def statement(entity_id, start, end):
    from sqlalchemy import and_, select
    from homeassistant.components.recorder.db_schema import Statistics as S, StatisticsMeta as M
    return (select(M.id, M.source, M.mean_type, M.unit_of_measurement, M.unit_class,
                   S.start_ts, S.min, S.mean, S.max)
            .select_from(M).outerjoin(S, and_(S.metadata_id == M.id, S.start_ts >= start, S.start_ts < end))
            .where(M.statistic_id == entity_id).order_by(S.start_ts.asc()).limit(24))


def convert_for(metadata, unit):
    from homeassistant.components.recorder.statistics import _get_unit_converter_func
    from homeassistant.exceptions import HomeAssistantError
    storage_unit, unit_class = metadata[3:5]
    if storage_unit == unit:
        return lambda value: value
    try:
        converter = _get_unit_converter_func(unit_class, storage_unit, unit)
    except (HomeAssistantError, ValueError, TypeError, KeyError):
        raise StatisticsError("unit_incompatible") from None
    if converter is None:
        raise StatisticsError("unit_incompatible")
    return converter


def normalized(rows, end_hour, unit, converter_factory=None):
    if not rows:
        raise StatisticsError("no_metadata")
    if len(rows) > 24:
        raise StatisticsError("invalid_data")
    metadata = tuple(rows[0][:5])
    if metadata[1] != "recorder" or type(metadata[2]) is bool or metadata[2] != 1:
        raise StatisticsError("not_arithmetic")
    convert = (convert_for if converter_factory is None else converter_factory)(metadata, unit)
    points = [None] * 24
    seen = set()
    start = (end_hour - 24) * 3600
    for row in rows:
        if tuple(row[:5]) != metadata:
            raise StatisticsError("invalid_data")
        stamp, low, mean, high = row[5:]
        if stamp is None:
            if len(rows) != 1 or (low, mean, high) != (None, None, None):
                raise StatisticsError("invalid_data")
            continue  # The one metadata-only LEFT JOIN row.
        if (type(stamp) not in (int, float) or not math.isfinite(stamp)
                or stamp % 3600 != 0 or not start <= stamp < end_hour * 3600 or stamp in seen):
            raise StatisticsError("invalid_data")
        seen.add(stamp)
        if low is None or mean is None or high is None:
            continue
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in (low, mean, high)):
            raise StatisticsError("invalid_data")
        if not low <= mean <= high:
            raise StatisticsError("invalid_data")
        values = tuple(convert(value) for value in (low, mean, high))
        if any(type(value) not in (int, float) or not math.isfinite(value) for value in values) or not values[0] <= values[1] <= values[2]:
            raise StatisticsError("invalid_data")
        points[int((stamp - start) / 3600)] = values
    digest = dataset_digest(metadata, points)
    valid = [point for point in points if point is not None]
    if not valid:
        return Dataset({"status": "empty", "reason": "no_data"}, digest)
    lower = min(point[0] for point in valid)
    upper = max(point[2] for point in valid)
    axes = repr(float(lower)), repr(float(upper))
    if any(len(value) > 24 for value in axes):
        raise StatisticsError("label_unrepresentable")
    flat = lower == upper
    # Scaling before subtraction avoids overflow across -DBL_MAX..DBL_MAX.
    scale = max(abs(lower), abs(upper), 1.0)
    lo, hi = lower / scale, upper / scale
    def q(value):
        if flat:
            return 500
        return round(max(0.0, min(1.0, (value / scale - lo) / (hi - lo))) * 1000)
    words = [format(q(value), "04x") if point is not None else "0000"
             for point in points for value in (point if point is not None else (0, 0, 0))]
    return Dataset({"status": "ready", "reason": "none", "valid_mask": sum(1 << i for i, point in enumerate(points) if point is not None),
                    "packed_q": "".join(words), "flat": flat,
                    "axis_min_text": axes[0], "axis_max_text": axes[1]}, digest)


def read_dataset(instance, entity_id, end_hour, unit):
    from homeassistant.helpers.recorder import session_scope
    # No writes/ORM entities/metadata-manager cache; read_only alone is not a
    # security barrier. This fresh session owns precisely one scalar SELECT.
    with session_scope(session=instance.get_session(), read_only=True) as session:
        rows = session.execute(statement(entity_id, (end_hour - 24) * 3600, end_hour * 3600)).all()
        return normalized(rows, end_hour, unit)
