# Procent otwarcia rolety — HA66, odbiór ograniczony

Status: odebrany zakres native45/HA66/175: realMQTT/HA/native/visual/browser/
cleanup i krótki pomiar54sourceFPS/failed0; fizyczny silnik osobno.
Szczegóły: validation-2026-10-31.md. Fragment W05 (Number zW04),
AEH-CTL-005, precyzyjna korekta o jeden punkt procentowy na istniejącym Number.
Szeroki suwak i pochylenie lameli pozostają osobnymi funkcjami.

Jawny v3 Number/property `position` tylko dla cover, rzeczywiste SET_POSITION4
i zarejestrowane cover.set_cover_position. Domena Core 0..100, krok1; 0 zamknięte,
100 otwarte. Bieżąca wartość wyłącznie current_position w jednym ze stanów
open/closed/opening/closing. Nie wnioskujemy pozycji ze stanu open/closed ani
z current_tilt_position. None, bool, ułamek, poza zakresem i outage blokują
krok. A-B-A bieżącej pozycji unieważnia poprzedni zamiar przez istniejący licznik
generacji. Utrata funkcji lub usługi unieważnia sesję.

Ten sam Number owner i renderer app6. Każde dopuszczone +/- wysyła pojedynczy
całkowity position do cover.set_cover_position; brak dodatkowego open/close/stop
lub tilt. Potwierdzenie oznacza obserwację raportowanej pozycji, nie dowód,
że silnik fizycznie się zatrzymał. Zamykanie kontrolki nie jest poleceniem Stop.
Ekran Stop/Otwórz/Zamknij pozostaje osobną świadomie przypisaną akcją Cover.
Nie zmieniamy dotychczasowych tapów ani ustawień.

Brak nowego bufora, zadania, timera, subskrypcji, protokołu czy kodu native.
Dane i politykę posiada HA; Number posiada jedną aktywną sesję i licznik
generacji. Natywny renderer ponownie używa swojej istniejącej puli.

Odbiór: testy konfiguracji i właściciela, pełny Python/Node/static; własna MQTT
Cover z niezależnym position_topic i set_position_topic. Dokładne integer
commands przed feedback, endpoints, brak pozycji, ruch, ABA, outage, capability
loss/recovery, PL/EN i edytor review/Undo. Oryginalne screenshoty, performance,
exact inverse i cleanup; fizyczny silnik osobno. MQTT może zachować poprzednią
pozycję po błędnym payload — test odróżnia stan Core od oczekiwania testowego.

Zainstalowane Core2026.7.1: W2/installed-cover-position-source.json.
cover SHA c684500e447918caa4fb557010f13f0d5ae0cb1edec0309d03a5a8fdeb23bfbc;
MQTT SHA 6be0e7992e108f62df477a98b4fffffb9fb2040850ef4c35fd45ee587b9206a5.
[Dokumentacja Cover](https://www.home-assistant.io/integrations/cover/).
