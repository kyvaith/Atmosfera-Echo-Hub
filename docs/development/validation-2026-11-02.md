# Walidacja 2 listopada 2026

## Końcowy pakiet native49 / HA95

[Pełny odbiór i screenshoty](notifications-acceptance-2026-11-02.md): górne
powiadomienia/centrum, historia HA100/24h,8 wierszy, gesty, PL/EN/akcent i ikony
robota/kosiarki. 810Python(3skip),397Node,13 scenariuszy realnego LVGL; pełny build,
audyt533źródeł/207jednostek,11959 wspólnych zależności, OTA i realny ekran.
Końcowe hashe opcji/danych HA i układ298 bez zmian;41 plików zgodnych z wdrożeniem.
Powtarzalne zwalnianie8pasów:0raw/0bands. Zbiorczy receipt:
`C:/aeh-build/notification-center-20261102/native49-ha95-notification-acceptance.json`.
Porównywalny średni czas16,552→16,358ms, failed0/DSI0; koszt24KiB PSRAM/1KiB internal.
Zakresy i nieudane próby QA zapisane w odbiorze. Fizyczne audio/ruch/GT911 i
odłączenie zasilania nie są objęte tym nowym odbiorem. Bez stage/commit/push.

## Wcześniejsza korekta podglądu HA94


HA94 / native46 / układ298: korekta wyłącznie CSS podglądu Wi-Fi.
397 Node PASS, Python bez zmian zachowania (panel asset-version literal
sprawdzony przez AST), diff check PASS. Rzeczywista przeglądarka1270×714:
głośnik25,72px/Wi-Fi33,91px przed, oba25,72px i bez przesunięcia po zmianie.
Zrzut zapisany, brak Save i zmian szkicu/układu. 39canonical=frozen=installed,
pełne hashe opcji/danych i16kart/3kamery/revision298 bez zmian. Jedno wznowienie
Core, RUNNING i odwołany token. Native46: dokładnyELF i dwa oryginały800×800
przed/po; nie było zmiany firmware, nowego build/flash ani powtórnej pełnej
trasy wydajności. To nie nowy odbiór audio/fizycznego dotyku/panelFPS.

Receipt: C:/aeh-build/feature-continuation-20261102/ha94-preview-scoped-acceptance.json.
Odczyt Climate, usług histerezy i tabeli partycji był pasywny. Nie zmieniono
nastaw ogrzewania, partycji ani źródeł kamer. Raport i nowe priorytety w
status-2026-11-02.md oraz priorities-2026-11-02.md. Bez Git commit/stage/push.
