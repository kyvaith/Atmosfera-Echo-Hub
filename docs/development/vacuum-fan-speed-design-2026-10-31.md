# Moc odkurzacza — HA65, odbiór ograniczony

Status: odebrany zakres MQTT/HA/native/visual/browser/cleanup i krótki pomiar.
Native45/HA65/173; 30 oryginałów,5exact commands,54sourceFPS/failed0.
Szczegóły: validation-2026-10-31.md; fizyczny robot pozostaje osobno.

Jawny v3 Choice/propertyfan_speed dotyczyvacuum. Wymaga rzeczywistego FAN_SPEED32,
zarejestrowanego vacuum.set_fan_speed i pełnego fan_speed_list1..8 różnych
drukowalnych nazw po najwyżej32bajty UTF-8. Bieżąca opcja pochodzi z fan_speed
w znanym staniecleaning/docked/idle/paused/returning/error. Brak, None, off-list,
unknown/outage nigdy nie stają się domyślną mocą ani trybem ręcznym.

HA cached attribute translations są etykietami. Brakujące znane nazwy mają
pakiet PL/EN, pozostałe zachowują dokładną nazwę. Kolizja etykiet wraca do
surowych nazw. Usługa zawsze dostaje dokładny rawfan_speed z katalogu, bez
zależności od tłumaczenia. Start/pauza/powrót do bazy są osobnymi operacjami;
wybór mocy nie wysyła ich jako dodatkowych poleceń.

Ten sam Choice owner/generation/authorization/single-service fence i app6
z ośmioma wierszami. Zmiana katalogu lub funkcji unieważnia sesję; A-B-A nie
przywraca starego kandydata. Brak nowego bufora, taska, timera, subskrypcji,
protokołu lub kodu native. To fragmentCTL014, nie mapy/pokoje/routines.

Wymagany odbiór: własna rzeczywista MQTT vacuum, broker-before-feedback bez
start/dock, różne aktywności, None/nieznany/off-list/literalnone, katalogi1/8/9,
reorder/empty/featureloss/outage/ABA/cancel/noop, PL/EN, edytor review/Undo,
oryginalne screenshoty, pomiar i dokładny cleanup. Fizyczny robot pozostaje
odrębny. MQTT wysyła surową nazwę na set_fan_speed_topic i czeka na stan.

Źródła: W2/installed-vacuum-source.json oraz installed-vacuum-constants-source.json
z Core2026.7.1. Corevacuum SHA3ef93e4f71dd1d538cf3a1c8c60591318f1c6408c1c50b93ed2fbefd3131c9f6;
MQTT SHA26f458353136e5cadd2d6807af5921954bc4999e3a5101a2203d0eece334b68a.
Dokumentacja: https://www.home-assistant.io/integrations/vacuum/.
