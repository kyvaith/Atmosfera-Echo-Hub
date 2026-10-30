# TouchDeck: płynność LVGL i kandydaci do Atmosfery

Data:30 października2026. Analiza źródeł `Keralots/TouchDeck`, main,
commit [`ae1011234b3a3b948397349bd1a9f1a3444a842a`](https://github.com/Keralots/TouchDeck/tree/ae1011234b3a3b948397349bd1a9f1a3444a842a)
z29 października. Kod TouchDeck oglądano, nie uruchamiano. Pierwsza analiza
nie obejmowała buildów ani zmian runtime Atmosfery. Późniejsze, osobno zlecone
optymalizacje są wdrożone i opisane w
[raporcie pomiarów](../development/touchdeck-performance-2026-10-30.md). Migracja funkcji
pozostaje wstrzymana; [punkt wznowienia](../development/resume-2026-10-30.md).

## Najważniejszy wynik

**Obecny TouchDeck używa snapshotów i własnego kompozytora.** To ten sam rodzaj
optymalizacji co w Atmosferze, mimo że wizualnie animacja wygląda jak przesuwanie
żywych widgetów LVGL. Nie ma podstaw, aby na podstawie tego projektu zastępować
naszą nawigację pełnym przerysowaniem drzewa LVGL w każdej klatce.

Dowody w kodzie:

- [`deck_panel.h:1–11`](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_panel.h#L1-L11)
  opisuje składanie przejść z zapisanych obrazów stron bez renderowania LVGL.
- [`deck_ui.cpp:536–558`](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui.cpp#L536-L558)
  rzeczywiście wywołuje `lv_snapshot_take_to_draw_buf` w RGB565.
- [`deck_ui.cpp:936–971`](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui.cpp#L936-L971)
  zatrzymuje obsługę LVGL, gdy przeciąganie lub przejście posiada ekran.
  Po zakończeniu wraca normalne aktualizowanie widgetów.
- Snapshoty są także używane dla szczegółów kart, panelu szybkich ustawień
  i ramki zdjęć, a nie tylko do jednego efektu przejścia.

Nie ustalono, który commit firmware pokazuje film YouTube. Wnioski dotyczą
przypiętej wersji źródeł. README rozróżnia film urządzenia i podglądy animacji;
te ostatnie opisuje jako zapisane klatka po klatce. Podgląd nie dostarcza czasu
potrzebnego do uzyskania każdej klatki. Film YouTube nie był niezależnie mierzony
(odczyt internetowy został ograniczony przez serwis).
[Źródło prezentacji](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/README.md).

## Inny koszt jednej klatki

| Cecha | TouchDeck | Atmosfera — zwalidowana ścieżka produktu |
| --- | --- | --- |
| Układ | ESP32-S3 | ESP32-P4 + radio ESP32-C6 |
| Ekran |320×480, także obrót480×320 |800×800 |
| Docelowy obraz |RGB565,2 bajty/piksel |RGB888,3 bajty/piksel |
| Jeden surowy pełny obraz |307200 bajtów |1920000 bajtów |
| Transport |AXS15231B, QSPI40MHz |MIPI DSI, pula buforów należąca do wyświetlacza |
| Przejścia |Snapshoty + kompozytor |Snapshoty + kompozytor/PPA i kontrola własności |

Atmosfera ma4,17 raza więcej pikseli i **6,25 raza więcej bajtów na surową klatkę**.
To rachunek wielkości danych, nie twierdzenie, że jest6,25 raza wolniejsza.
Układy, transport, akceleratory i równoległe obciążenie audio/kamerą są inne.
Przy hipotetycznym60Hz sam strumień pełnych obrazów to18,432MB/s i115,2MB/s;
nie obejmuje odczytów kompozytora, kopii ani narzutu protokołu.

TouchDeck ma dwa pełne bufory LVGL w PSRAM, RGB565 DIRECT, LVGL9.5.0 i jeden
software draw unit. Nie jest to wynik włączenia wielowątkowego renderowania
LVGL lub tajemniczego GPU. Używa własnego sterownika; Arduino_GFX dostarcza
przede wszystkim tablicę inicjalizacji panelu.
[Konfiguracja](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/platformio.ini),
[LVGL DIRECT](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui.cpp#L793-L800),
[konfiguracja LVGL](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/include/lv_conf.h).
Nasza granica porównania: [pamięć](../architecture/runtime-memory.md)
i [nawigacja](../architecture/navigation-snapshots.md), nie sama nazwa opcji YAML.

## Co konkretnie robią dla wydajności

| Mechanizm | Co wynika z kodu | Znaczenie dla Atmosfery |
| --- | --- | --- |
| Nakładanie renderowania i wysyłania |Flush zgłasza gotową klatkę; oczekiwanie dotyczy starszego nadal zajętego bufora. LVGL może przygotowywać następną podczas transmisji poprzedniej. Komentarz autora wskazuje, że zbyt wczesne oczekiwanie zmniejszało animacje do30FPS. |Warto audytować nakładanie pracy w obecnej ścieżce DSI; nie stwierdzono, że mamy właśnie ten błąd. Nie zmieniać momentu zwolnienia bufora bez dowodu własności. |
| Asynchroniczne DMA w pasach |Dwa wewnętrzne bufory po48 wierszy; procesor przygotowuje następny pas, podczas gdy QSPI wysyła poprzedni. DMA czyta te bufory, a nie bezpośrednio PSRAM LVGL. |Zasada nakładania etapów jest cenna. Sterownik SPI i dodatkowe kopie CPU nie są zamiennikiem naszego DSI/PPA. |
| Synchronizacja TE |Transmisja zaczyna się blisko świeżego sygnału synchronizacji panelu; spóźniona krawędź jest pomijana. Osobne zadanie flush ma priorytet20 na rdzeniu1, poza głównym obciążeniem Wi-Fi. |Porównywać present/VSYNC i odstępy klatek. Nie kopiować numeru rdzenia, priorytetu ani progów czasowych. |
| Planowanie snapshotów |Najpierw brakujące obrazy i strony o jeden gest od aktualnej. Bez odświeżania podczas dotyku/przejścia; najwyżej jeden snapshot na przebieg. |Inspiracja do audytu istniejącego harmonogramu, z limitami wieku i bez głodzenia stron. |
| Wcześniejsze składanie Glass |Tapeta, rozmyte fragmenty, tint i obrysy powstają raz jako tło RGB565. Normalne renderowanie kopiuje wynik zamiast mieszać każdą szklaną kartę. |Dla przyszłych kosztownych teł M3: cache zależny od motywu/geometrii, w obecnej puli i z jawnym zwolnieniem. |
| Małe cache wykresów |Osobny bufor A8 dla wykresu, ponownie używany; brak przerysowania poniżej ćwierć piksela przesunięcia i bez istotnej zmiany osi. |Przydatne dla przyszłych wykresów; odświeżać ograniczony obszar i tylko gdy obraz rzeczywiście się zmienił. |
| Budżety animacji i pracy ukrytej |Wykresy tylko na widocznej niezasłoniętej stronie, kadencja33ms. Efekty drukarki celowo około5–15FPS, rozłożone kolejno między kafelkami. Wartości/napisy mają bramki wersji i równości. |Nie każdy efekt musi być60FPS. Osobny budżet i zatrzymanie niewidocznej pracy są ważniejsze niż mnożenie animacji. |

Źródła: [flush-wait](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui.cpp#L94-L122),
[DMA i zwolnienie klatki](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_panel.cpp#L1350-L1396),
[TE](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_panel.cpp#L1315-L1336),
[zadania](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_panel.cpp#L1547-L1550),
[snapshoty](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui.cpp#L484-L558),
[Glass](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui_glass.cpp#L163-L243),
[wykres](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui_metric.cpp#L124-L180),
[budżet efektów drukarki](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui_prnfx.cpp#L770-L795).

Istotny kompromis: sam snapshot całej strony według komentarzy kosztuje około
40–45ms. Gdy wykresy płynnie przesuwają się, odświeżanie istniejących snapshotów
jest ograniczane nawet do jednego na5s. Ich płynność także wymaga zarządzania
przerwami i świeżością danych. U nas zmiana akcentu, kontekstu akcji lub ważnego
stanu bezpieczeństwa nie może bezwarunkowo czekać5s według skopiowanej reguły.

## Jak mocne są dowody szybkości

W sterowniku są liczniki wysłanych klatek i klatek kompozytora, średnie/maksymalne
czasy budowania i transmisji, spóźnione TE, dropy, maksymalny odstęp pomiędzy
klatkami oraz maksymalny koszt snapshotu. To wartościowe narzędzia porównawcze.
[Logowanie](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui.cpp#L764-L779).

Podawane15,4ms transmisji i16,39ms okresu TE są **pomiarami deklarowanymi przez
autora w komentarzu**, nie naszym benchmarkiem. Timer16ms nie dowodzi60FPS,
33ms wykresów oznacza około30 aktualizacji/s, a klatki renderowane i pokazane
to różne liczniki. Nie wykonano testu identycznego workloadu na obu urządzeniach.

Najrozsądniejszy przyszły audyt u nas: oddzielić czas renderowania, przygotowania
snapshotu i faktycznej prezentacji; mierzyć rozkład odstępów/p95, spóźnione VSYNC,
pamięć po lifecycle oraz audio. Zerować okno pomiaru na początku kontrolowanego
scenariusza. Nie wyciągać wniosków z jednego mieszanego okna CPU.

## Funkcje do listy

Poniższe TD są identyfikatorami kandydatur badawczych. Nie zmieniają108 bazowych
rodzin, nie oznaczają wdrożenia ani zgody na rozpoczęcie migracji.

| Kandydat | Rzeczywista funkcja TouchDeck | Rozsądna granica u nas |
| --- | --- | --- |
|TD-01 — warunkowe strony/kafelki |Widoczność według encji/online PC, współdzielenie miejsca przez warianty, bezpieczny reflow po geście; auto-przejście po pojawieniu się strony i powrót. |Po bounded templates; HA ustala warunki, stabilne IDs i jawne zasady unknown/stale. Nie przerywać gestu, asystenta ani kamery. Rozszerza CFG-014/018 o brakującą politykę. |
|TD-02 — companion PC |CPU/GPU/RAM/sieć, media, głośność, skróty; parowane komendy z podpisem i jednorazowym nonce; transport LAN lub USB serial. |Opcjonalny host, najpierw tylko odczyt. Potem dozwolone komendy i potwierdzenia dla wyłączenia/restartu. To nie USB HID ani nasz Sendspin. |
|TD-03 — źródła HTTP JSON |Wspólny polling odpowiedzi URL+headers, wybór wielu ścieżek JSON i kontrola świeżości;32KiB body,48 punktów historii. |Preferować istniejące REST sensors HA, a brakujący adapter ulokować w HA. Tokeny, sieć i agregacja poza firmware. CTL-027 dotyczy akcji HTTP, nie całego tego mechanizmu odczytu. |
|TD-04 — drukarka Bambu/AMS |Postęp/temperatury, szpule i sloty AMS, osobne widoki; źródło bezpośrednie albo integracja HA, mapowanie przez registry IDs. |Opcjonalny pion funkcjonalny, gdy istnieje drukarka do testów. Preferować HA zamiast dodatkowego klienta TLS/MQTT i danych logowania w urządzeniu. |
|TD-05 — grupy stron w dwóch osiach |Poziomo między kolumnami, pionowo wewnątrz grupy. |Po prostych stronach runtime. Wymaga projektu nawigacji/gestów, zachowania puli snapshotów i testów wszystkich granic. |

Źródła funkcji: [warunki](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/GUIDE.md#conditional-tiles),
[bezpieczna zmiana strony](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui.cpp#L691-L754),
[companion](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/TouchDeck-CompanionApp/README.md),
[weryfikacja komend PC](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/TouchDeck-CompanionApp/companion-common/pc_control.py#L74-L153),
[HTTP](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_http.cpp#L197-L240),
[mapowanie Bambu przez HA](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_bambu_ha.cpp#L199-L258),
[model stron](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_config.h#L226-L232).

### Rozszerzenia już istniejących pozycji

- **CTL-017 / UI-003:** warn/crit, kierunek „za wysoko/za nisko” i histereza
  zapobiegająca miganiu koloru. TouchDeck stosuje margines max(0,01;1% progu).
  [Implementacja](https://github.com/Keralots/TouchDeck/blob/ae1011234b3a3b948397349bd1a9f1a3444a842a/src/deck_ui_bind.cpp#L24-L39).
- **CTL-017/018/019:** do czterech opisanych odczytów/pasków na kafelku i mała,
  ograniczona historia. Kompozycja wierszy jest w JSON; nie ma jeszcze pełnego
  edytora tych wierszy w portalu TouchDeck. Nie mylić historii od uruchomienia
  z historią HA Recorder.
- **CFG-004/015:** lokalny edytor Done/Cancel jako drugi klient tej samej
  konfiguracji HA, bez niezależnego zapisywania innej prawdy w urządzeniu.
- **UI-002:** ograniczone presety animacji i wariant spokojny/reduced motion;
  nie kopiować nowego silnika ani buforów. Ich zestawy to Classic/Calm/Water/
  Glass/Heavy/Custom; nie wszystkie efekty mają tę samą kadencję.
- **SYS-002/003:** obecność, harmonogramy i priorytety wake/sleep; **CFG-017 /
  SYS-001:** szybki panel jasności/łączności. To rozwinięcie już zaplanowanych
  polityk, nie nowe transporty.
- **DEV-004:** uporządkowane screenshoty, input replay i pomiary present, na bazie
  istniejących diagnostyk Atmosfery. Sam endpoint snapshotu nie jest nowością.

Widoki Proxmox/pfSense na screenshotach nie dowodzą dedykowanych integracji;
potwierdzony mechanizm to ogólne dane HTTP/JSON. USB serial companion zajmuje
port COM i nie jest USB HID. Przegląd podpisywania komend nie jest audytem
bezpieczeństwa ani dowodem szyfrowania całego transportu.

## Kolejność po ewentualnym wznowieniu

Najpierw wrócić do istniejącego punktu Sun/HA20 i zamknąć jego zaległy odbiór,
bez mieszania nowych zmian. Następnie rozważyć progi/histerezę oraz świeżość
danych, ograniczone wykresy i źródła HA. Warunkowe strony dopiero po stabilnych
szablonach; PC companion i Bambu jako osobne opcjonalne zakresy.

Nie przenosić dosłownie: surowego obrazu dla każdej strony, pełnego tła Glass
dla każdego nowego widoku, sterownika QSPI, progów900us/8ms ani polityki
przenoszenia wszystkich alokacji do PSRAM. Atmosfera ma trzy raw sloty Home,
JPEG poza oknem, wspólny obszar roboczy aplikacji i ciągły scanout DSI.
To kontrakty do zachowania, nie ograniczenia do obejścia.

Materiały robocze są w `C:\aeh-build\research-touchdeck-20261030`:
`rendering-findings.md`, `motion-findings.md`, `features-findings.md` i przypięta
kopia źródeł `TouchDeck`. Pierwsze zadanie badawcze ograniczało się do dokumentacji
i autoryzowanej notatki pamięci; w jego ramach nie wykonano testów sprzętowych
ani wdrożenia. Późniejsze, jawnie zlecone prace nad wydajnością mają osobny
[raport wdrożenia i pomiarów](../development/touchdeck-performance-2026-10-30.md).
