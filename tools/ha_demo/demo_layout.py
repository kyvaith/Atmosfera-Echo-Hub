"""Build importable demonstration layouts using only opted-in HA test devices."""

from copy import deepcopy

ORDER = [f"home-{index}" for index in range(1, 6)]


def control(kind, property_name=None):
    return {"kind": "control", "control": kind, **({"property": property_name} if property_name else {})}


def service(name, **data):
    return {"kind": "service", "service": name, "data": data}


def card(slot, entity, title, icon, action=None):
    return {
        "id": f"aeh-demo-{slot:02d}",
        "slot": slot,
        "type": "sensor" if action == {"kind": "none"} else "entity",
        "entity_id": entity,
        "title": title,
        "icon": icon,
        "palette": ("primary", "secondary", "tertiary", "primary_container")[slot % 4],
        "visible": True,
        "action": action or {"kind": "default"},
    }


def demo(domain, slug, title, icon, action=None):
    return (f"{domain}.atmosfera_demo_{slug}", title, icon, action)


INFO = {"kind": "none"}
TOOL_CARDS = {
    2: demo("binary_sensor", "contact", "Kontakt", "auto", INFO),
    3: demo("lock", "lock", "Zamek", "lock", service("lock.lock")),
    5: demo("cover", "garage", "Brama", "cover", control("cover")),
    6: demo("fan", "fan", "Nawiew", "fan", control("choice", "percentage")),
    8: demo("switch", "switch", "Przełącznik", "switch"),
    9: demo("fan", "fan", "Kierunek nawiewu", "fan", control("choice", "direction")),
    10: demo("lawn_mower", "mower", "Kosiarka", "mower", service("lawn_mower.start_mowing")),
    11: demo("alarm_control_panel", "alarm", "Stan alarmu", "alarm", INFO),
    12: demo("calendar", "agenda", "Agenda", "clock", INFO),
    13: demo("sensor", "sensor", "Pomiar", "sensor", INFO),
    14: demo("timer", "timer", "Minutnik", "clock", service("timer.start", duration=120)),
    15: demo("button", "notice", "Powiadomienie", "action"),
    16: demo("climate", "thermostat", "Termostat", "climate", control("number", "temperature")),
    17: demo("cover", "blind", "Roleta", "cover", control("number", "position")),
    18: demo("cover", "blind", "Lamele", "cover", control("number", "tilt_position")),
    19: demo("light", "effects", "Efekty", "light", control("choice", "effect")),
    20: demo("humidifier", "humidity", "Wilgotność", "sensor", control("number", "humidity")),
    21: demo("humidifier", "humidity_modes", "Nawilżacz", "sensor", control("choice", "mode")),
    22: demo("vacuum", "vacuum", "Odkurzacz", "vacuum", service("vacuum.start")),
    23: demo("vacuum", "vacuum", "Moc ssania", "vacuum", control("choice", "fan_speed")),
    24: demo("media_player", "music", "Play/Pauza", "action", service("media_player.media_play_pause")),
    25: demo("media_player", "tv", "Źródło TV", "action", control("choice", "source")),
    26: demo("remote", "remote", "Pilot", "action", control("choice", "activity")),
    27: demo("select", "options", "Opcje", "action", control("choice")),
    28: demo("light", "light", "Barwa lampy", "light", control("number", "color_temp_kelvin")),
    29: demo("fan", "fan", "Oscylacja", "fan", {"kind": "fan_oscillation"}),
    30: demo("button", "doorbell", "Dzwonek", "action"),
    31: demo("number", "number", "Nastawa", "sensor", control("number")),
}

EXTRA_CARDS = [
    demo("climate", "thermostat", "Tryb HVAC", "climate", control("choice", "hvac_mode")),
    demo("climate", "climate_presets", "Preset HVAC", "climate", control("choice", "preset_mode")),
    demo("climate", "thermostat", "Nawiew HVAC", "fan", control("choice", "fan_mode")),
    demo("climate", "thermostat", "Ruch góra/dół", "fan", control("choice", "swing_mode")),
    demo("climate", "thermostat", "Ruch na boki", "fan", control("choice", "swing_horizontal_mode")),
    demo("climate", "thermostat", "Wilgoć HVAC", "sensor", control("number", "humidity")),
    demo("fan", "fan", "Preset nawiewu", "fan", control("choice")),
    demo("humidifier", "humidity", "Zasilanie", "switch", service("humidifier.toggle")),
    demo("light", "light", "Jasność lampy", "light", control("light")),
    demo("lawn_mower", "mower", "Pauza koszenia", "mower", service("lawn_mower.pause")),
    demo("lawn_mower", "mower", "Baza kosiarki", "mower", service("lawn_mower.dock")),
    demo("vacuum", "vacuum", "Pauza robota", "vacuum", service("vacuum.pause")),
    demo("vacuum", "vacuum", "Stop robota", "vacuum", service("vacuum.stop")),
    demo("vacuum", "vacuum", "Baza robota", "vacuum", service("vacuum.return_to_base")),
    demo("vacuum", "vacuum", "Szukaj robota", "vacuum", service("vacuum.locate")),
    demo("vacuum", "vacuum", "Sprzątaj punkt", "vacuum", service("vacuum.clean_spot")),
    demo("remote", "remote", "Włącz pilot", "action", service("remote.turn_on")),
    demo("remote", "remote", "Wyłącz pilot", "action", service("remote.turn_off")),
    demo("media_player", "music", "Powtarzanie", "action", control("choice", "repeat")),
    demo("media_player", "music", "Tryb dźwięku", "action", control("choice", "sound_mode")),
    demo("media_player", "music", "Stop audio", "action", service("media_player.media_stop")),
    demo("media_player", "music", "Wycisz", "action", service("media_player.volume_mute", is_volume_muted=True)),
    demo("media_player", "music", "Losowo", "action", service("media_player.shuffle_set", shuffle=True)),
    demo("media_player", "music", "Głośniej", "action", service("media_player.volume_up")),
    demo("media_player", "music", "Ciszej", "action", service("media_player.volume_down")),
    demo("media_player", "music", "Głośność 35%", "action", service("media_player.volume_set", volume_level=0.35)),
    demo("timer", "timer", "Pauza timera", "clock", service("timer.pause")),
    demo("timer", "timer", "Anuluj timer", "clock", service("timer.cancel")),
]

INFO_CARDS = {
    2: ("sun.sun", "Słońce", "clock", INFO),
    3: demo("input_datetime", "data_i_czas", "Data i czas", "clock", INFO),
    5: demo("binary_sensor", "contact", "Kontakt", "auto", INFO),
    8: demo("automation", "automatyzacja", "Automatyzacja", "action", service("automation.trigger")),
    9: demo("scene", "scena", "Scena", "scene", service("scene.turn_on")),
    10: demo("script", "script", "Skrypt", "action", service("script.turn_on")),
    11: demo("input_text", "tekst", "Tekst", "action", INFO),
    12: demo("person", "osoba", "Obecność", "presence", INFO),
    13: demo("sensor", "sensor", "Pomiar", "sensor", INFO),
    14: demo("timer", "timer", "Minutnik", "clock", service("timer.start", duration=120)),
    15: demo("button", "button", "Przycisk", "action"),
    16: demo("vacuum", "vacuum", "Pokój", "vacuum", service("vacuum.clean_area", cleaning_area_id="atmosfera_demo")),
    17: demo("cover", "blind", "Stop rolety", "cover", service("cover.stop_cover")),
    18: demo("cover", "blind", "Stop lameli", "cover", service("cover.stop_cover_tilt")),
}


def build(current, states, *, extra=False, information=False):
    """Bind available test entities, retaining the two real user controls in the main layout."""
    result = {**current, "version": 3, "home_order": ORDER.copy()}
    result["cards"] = [deepcopy(item) for item in current["cards"] if item["slot"] in (0, 1)]
    if information:
        bindings = INFO_CARDS.items()
    elif extra:
        bindings = enumerate(EXTRA_CARDS, 2)
    else:
        result["cards"] += [
            deepcopy(item) for item in current["cards"]
            if item["slot"] in (4, 7) and item["visible"] and item["entity_id"] in states
            and states[item["entity_id"]] not in {"unavailable", "unknown"}
        ]
        bindings = TOOL_CARDS.items()
    for slot, definition in bindings:
        if definition[0] in states and states[definition[0]] != "unavailable":
            result["cards"].append(card(slot, *definition))
    return result
