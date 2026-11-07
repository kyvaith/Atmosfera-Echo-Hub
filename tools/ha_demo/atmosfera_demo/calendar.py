"""Simulation-only calendar platform."""

from datetime import timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util


class DemoAgenda(CalendarEntity):
    """Six read-only examples on the existing non-registry Calendar 1 identity."""

    _attr_name = "Calendar 1"

    def __init__(self):
        self.entity_id = "calendar.atmosfera_demo_agenda"
        now = dt_util.now().replace(microsecond=0)
        today = now.date()
        self._events = (
            CalendarEvent(start=now-timedelta(minutes=15), end=now+timedelta(minutes=45),
                          summary="Domowe spotkanie", location="Salon", description="Bieżące wydarzenie demonstracyjne."),
            CalendarEvent(start=now+timedelta(hours=2), end=now+timedelta(hours=3),
                          summary="Plan na jutro", location="Gabinet"),
            CalendarEvent(start=now+timedelta(hours=2, minutes=15), end=now+timedelta(hours=3, minutes=15),
                          summary="Nakładające się wydarzenie", description="Oba wydarzenia pozostają widoczne."),
            CalendarEvent(start=today+timedelta(days=1), end=today+timedelta(days=2),
                          summary="Dzień dla rodziny"),
            CalendarEvent(start=today+timedelta(days=2), end=today+timedelta(days=4),
                          summary="Dwudniowy wyjazd", location="Góry"),
            CalendarEvent(start=now+timedelta(days=4), end=now+timedelta(days=4, hours=1),
                          summary="Zażółć gęślą jaźń — spotkanie z długim polskim tytułem do sprawdzenia czytelnego skrótu",
                          description="Długi opis demonstracyjny. Szczegóły pozostają w Home Assistant, a ekran pokazuje jawny skrót."),
        )

    @property
    def event(self):
        now = dt_util.now()
        return min((event for event in self._events if event.end_datetime_local > now),
                   key=lambda event: event.start_datetime_local, default=None)

    async def async_get_events(self, hass, start_date, end_date):
        return sorted((event for event in self._events
                       if event.end_datetime_local > start_date and event.start_datetime_local < end_date),
                      key=lambda event: event.start_datetime_local)


async def async_setup_entry(hass, entry, async_add_entities):
    # Core's previous demo had no unique_id/device_info. Do not register a new
    # identity or attach unrelated devices while retaining its explicit entity_id.
    async_add_entities([DemoAgenda()])
