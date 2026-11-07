# Pochylenie lameli — HA67, odbiór ograniczony

Status: odebrany zakres native45/HA67/177,24oryginały/6exactcommands/
53sourceFPS/failed0; fizyczny silnik osobno. Fragment W05/CTL005, Number zW04.
Szczegóły: validation-2026-10-31.md.
Jawny v3 Number/property `tilt_position` wymaga SET_TILT_POSITION128 i
cover.set_cover_tilt_position. Domena Core0..100 ze skokiem1; procent HA,
nie kąt w stopniach. Bieżąca wartość tylko current_tilt_position w znanym
stanie cover. Zwykłe current_position ani open/closed nie wyznaczają pochylenia.

Ten sam Number owner, renderer, generacja ABA i jedna usługa z integer
tilt_position. Zero dodatkowych open/close/stop ani podnoszenia rolety.
Zamykanie widoku nie zatrzymuje napędu. Potwierdzenie wartości w HA nie jest
obserwacją fizycznego silnika. Stop lameli pozostaje osobną akcją HA.
Core normalizuje zakres producenta tilt_min/max, również odwrócony.

Brak nowego native kodu, bufora, zadania, timera, subskrypcji i protokołu.
Polityka i dane należą do HA; renderer ponownie używa istniejącej puli.
Odbiór wymaga host/static i własnej rzeczywistej MQTT Cover: niezależne
current_position99 i tilt45, broker przed feedback, endpoints, brak/unknown,
ABA, outage, utrata funkcji, odwrócony zakres, PL/EN, browser review/Undo,
oryginalne screenshoty, pomiar, exact inverse i cleanup. Fizyczny silnik osobno.

Źródło Core2026.7.1: W2/installed-cover-tilt-source.json. Cover i MQTT mają te
same SHA co adapter pozycji; const SHA62850e0235e9a6bb0d78d4b96701c47a894672181318a2048a5fb46a2b52c40d.
[Dokumentacja Cover](https://www.home-assistant.io/integrations/cover/).
