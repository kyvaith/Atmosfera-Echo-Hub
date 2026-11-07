# Wydarzenie zgłaszane przez kalendarz HA — HA68, odbiór ograniczony

Status: odebrany zakres native45/HA68/193. Fragment CTL021/W18.
14oryginałów funkcjonalnych +24performance, realny browser, exact cleanup.
Dopasowane control/active/control/active:54sourceFPS/failed0. Szczegóły i
zachowane słabsze wyniki: validation-2026-10-31.md. Brak nowego flash.
To pasywny kafelek jednego wydarzenia CalendarEntity.event, nie agenda,
pełna lista ani rezerwacje. Wykorzystuje istniejące pole tekstowe i ikonę clock.

Źródłem jest znany stan on/off i publiczne message/all_day/start_time/end_time
z Core. HA już przelicza start/end na lokalną strefę i emituje kanoniczne
YYYY-MM-DD HH:mm:ss bez offsetu. Nie przeliczamy ich ponownie ani nie udajemy,
że z takich ściennych pól można odzyskać fold DST. Daty/godziny są sprawdzane
składniowo; nie porównujemy naiwnych godzin start/end przy jesiennym DST.
Wydarzenie całodniowe zachowuje datę i nie dostaje fikcyjnej godziny.
Znany off bez wszystkich pól wydarzenia oznacza Brak wydarzeń/No events;
częściowe/malformed/None i active on bez danych są nieznane. Nie pobieramy
description/location/URL do podpisu. Tytuł jest zwykłym ograniczonym tekstem,
markup i kontrolne znaki nie trafiają na ekran; całość do40 znaków z jawnym ...
przy skróceniu. Pełny rok zapobiega pomyleniu przyszłorocznego wydarzenia.
Normalizacja tytułu ma wejście do256 znaków. Katalog przekazuje oba podpisy
PL/EN oraz dokładne ograniczone pola obserwacji. Edytor pokazuje podpis tylko
przy zgodnej obserwacji; w przeciwnym razie Nieznany do istniejącego odświeżenia
metadanych co5s. Nie duplikuje parsera HTML ani obliczeń czasu w przeglądarce.

Tylko slot12: istniejący szeroki wiersz440px. Katalog/profile i edytor blokują
przeniesienie do mniejszej karty przed zapisem. Typ sensor, actionnone;
również raw/legacy service nie może zamienić go w akcję. Bez wpisywania lub
usuwania wydarzeń z urządzenia. Nie zmieniamy dotychczasowych kart użytkownika.

Właścicielem eventu i harmonogramu start/end jest Core CalendarEntity; HA
przekazuje zmianę przez istniejącą subskrypcję stanów i presentation. Bez nowego
timera, pollera, taska, bufora, protokołu ani natywnej alokacji. Nie dodajemy
relatywnego „Dziś/Jutro”, które wymagałoby osobnego zegara odświeżania.

Odbiór: host/JS/static, własny Local Calendar utworzony zwykłym config flow;
realne create_event/update/delete dotyczą wyłącznie własnej encji QA. Brak
eventu, timed/all-day, PL/EN, skrócenie/markup, aktualizacja poza stroną,
usunięcie źródła i dwa pasywne tapy; rzeczywisty edytor/Undo/placement,
oryginały urządzenia i performance. Exact inverse wyłącznie własnych pól slot12,
pozostałe15 kart (w tym6/7/15),3kamery/8preferencji bez zmiany. Usunięcie
własnego config entry przez Core usuwa jego własny plikICS; sprawdzić po cleanup.

Core2026.7.1: W2/installed-calendar-source.json. Calendar SHA
47175d88ca450b86ab0e8819ee5529dfdd0d5368bc85dccf2154d4d5ff118e04.
[Calendar](https://www.home-assistant.io/integrations/calendar/),
[Local Calendar](https://www.home-assistant.io/integrations/local_calendar/).

HA70 dodatkowy odbiór: rzeczywisty limit290px/Roboto16 (288px z marginesem)
oprócz40znaków;319 metryk z native45. Szerokie W255 kończą się widocznym...
13scenariuszy+Home ponownie na urządzeniu, realny browser, cleanup207; końcowy
odbiór Person/performance przy209. Szczegóły validation-2026-10-31.md.
