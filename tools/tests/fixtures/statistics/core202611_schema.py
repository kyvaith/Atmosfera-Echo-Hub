"""Exact Core2026.11.0 recorder db_schema.py class excerpts for isolated SQL tests.
Source Apache-2.0: https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/recorder/db_schema.py
Full source SHA256 2ae9c803ec3fc575b04ee93997a30e746d33cbd5bf44e03d74e9d2c910cac668.
Only dependencies/types are supplied by the fixture loader; class bodies unchanged.
"""
from __future__ import annotations

class StatisticsBase:
    """Statistics base class."""

    id: Mapped[int] = mapped_column(ID_TYPE, Identity(), primary_key=True)
    created: Mapped[datetime | None] = mapped_column(UNUSED_LEGACY_DATETIME_COLUMN)
    created_ts: Mapped[float | None] = mapped_column(TIMESTAMP_TYPE, default=time.time)
    metadata_id: Mapped[int | None] = mapped_column(
        ID_TYPE,
        ForeignKey(f"{TABLE_STATISTICS_META}.id", ondelete="CASCADE"),
    )
    start: Mapped[datetime | None] = mapped_column(UNUSED_LEGACY_DATETIME_COLUMN)
    start_ts: Mapped[float | None] = mapped_column(TIMESTAMP_TYPE, index=True)
    mean: Mapped[float | None] = mapped_column(DOUBLE_TYPE)
    mean_weight: Mapped[float | None] = mapped_column(DOUBLE_TYPE)
    min: Mapped[float | None] = mapped_column(DOUBLE_TYPE)
    max: Mapped[float | None] = mapped_column(DOUBLE_TYPE)
    last_reset: Mapped[datetime | None] = mapped_column(UNUSED_LEGACY_DATETIME_COLUMN)
    last_reset_ts: Mapped[float | None] = mapped_column(TIMESTAMP_TYPE)
    state: Mapped[float | None] = mapped_column(DOUBLE_TYPE)
    sum: Mapped[float | None] = mapped_column(DOUBLE_TYPE)

    duration: timedelta

    @classmethod
    def from_stats(
        cls, metadata_id: int, stats: StatisticData, now_timestamp: float | None = None
    ) -> Self:
        """Create object from a statistics with datetime objects."""
        return cls(  # type: ignore[call-arg]
            metadata_id=metadata_id,
            created=None,
            created_ts=now_timestamp or time.time(),
            start=None,
            start_ts=stats["start"].timestamp(),
            mean=stats.get("mean"),
            mean_weight=stats.get("mean_weight"),
            min=stats.get("min"),
            max=stats.get("max"),
            last_reset=None,
            last_reset_ts=datetime_to_timestamp_or_none(stats.get("last_reset")),
            state=stats.get("state"),
            sum=stats.get("sum"),
        )

    @classmethod
    def from_stats_ts(
        cls,
        metadata_id: int,
        stats: StatisticDataTimestamp,
        now_timestamp: float | None = None,
    ) -> Self:
        """Create object from a statistics with timestamps."""
        return cls(  # type: ignore[call-arg]
            metadata_id=metadata_id,
            created=None,
            created_ts=now_timestamp or time.time(),
            start=None,
            start_ts=stats["start_ts"],
            mean=stats.get("mean"),
            mean_weight=stats.get("mean_weight"),
            min=stats.get("min"),
            max=stats.get("max"),
            last_reset=None,
            last_reset_ts=stats.get("last_reset_ts"),
            state=stats.get("state"),
            sum=stats.get("sum"),
        )

class Statistics(Base, StatisticsBase):
    """Long term statistics."""

    duration = timedelta(hours=1)

    __table_args__ = (
        # Used for fetching statistics for a certain entity at a specific time
        Index(
            "ix_statistics_statistic_id_start_ts",
            "metadata_id",
            "start_ts",
            unique=True,
        ),
        _DEFAULT_TABLE_ARGS,
    )
    __tablename__ = TABLE_STATISTICS

class _StatisticsMeta:
    """Statistics meta data."""

    __table_args__ = (_DEFAULT_TABLE_ARGS,)
    __tablename__ = TABLE_STATISTICS_META
    id: Mapped[int] = mapped_column(ID_TYPE, Identity(), primary_key=True)
    statistic_id: Mapped[str | None] = mapped_column(
        String(255), index=True, unique=True
    )
    source: Mapped[str | None] = mapped_column(String(32))
    unit_of_measurement: Mapped[str | None] = mapped_column(String(255))
    unit_class: Mapped[str | None] = mapped_column(String(255))
    has_mean: Mapped[bool | None] = mapped_column(Boolean)
    has_sum: Mapped[bool | None] = mapped_column(Boolean)
    name: Mapped[str | None] = mapped_column(String(255))
    mean_type: Mapped[StatisticMeanType] = mapped_column(
        SmallInteger, nullable=False, default=StatisticMeanType.NONE.value
    )  # See StatisticMeanType

    @staticmethod
    def from_meta(meta: StatisticMetaData) -> StatisticsMeta:
        """Create object from meta data."""
        return StatisticsMeta(**meta)

class StatisticsMeta(Base, _StatisticsMeta):
    """Statistics meta data."""
