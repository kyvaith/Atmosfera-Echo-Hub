# Porównanie projektów i zakres rozwoju Atmosfera — 2026-10-24

Analiza obejmuje jtenniswood/espcontrol, MaxGramser/homeassistant_espscreen (Tessera) i oficjalne ESP-Mosaico. Jej wynikiem jest [plan 108 rodzin funkcji ze stałymi ID](../development/feature-roadmap-2026-10-24.md). Rejestr rozróżnia obecną bazę, nowy kod i faktyczną akceptację urządzenia. Nie jest deklaracją, że funkcje wszystkich trzech produktów zostały zaimplementowane.

## Wnioski produktowe

Największa przenośna luka Atmosfery to konfiguracja: wizualny panel HA, biblioteka encji i ich możliwości, przeciąganie kart, własny model układu, backup, kontrola konfliktów i jasny wynik zastosowania. Druga luka to domenowe regulatory. Powiązanie climate z kartą i wyświetlenie temperatury nie daje panelu klimatu; ustawienie service nie daje dowolnego suwaka ani formularza parametrów. To cele AEH-CFG-001..010 i AEH-CTL-001..013.

Atmosfera ma już mocną bazę: snapshotową nawigację, kontrolę własności RGB888/DSI, sprzętowy JPEG, pełnoekranowe kamery HA/MJPEG, Player/Sendspin i grupowanie głośników, Immich, full-duplex voice/AEC, bounded powiadomienia, pogodę Lottie, en/pl, akcent i OTA. Rozwój edytora ma te mechanizmy wykorzystywać i rozszerzać.

ESPControl jest wzorcem kompletnego produktu panelowego. Tessera daje szeroki model HA i narzędzia konfiguracji, ale jej aktualny kod podlega AGPL, a sposób zarządzania stronami/buforami nie jest równoważny naszej architekturze. Mosaico wnosi inny rodzaj wartości: tworzenie i dystrybucję aplikacji, narzędzia obserwacji oraz agentowe rozszerzenia. Nie znaleziono tam potwierdzonego gotowego edytora dashboardu HA.

## Tożsamość źródeł i poziom dowodu

Opublikowany 2026-10-24 punkt odniesienia Atmosfery to produkt [65683789d83ceb4510b202ce98979043c8f5e2f6](https://github.com/kyvaith/Atmosfera-Echo-Hub/commit/65683789d83ceb4510b202ce98979043c8f5e2f6) i companion ESPHome [41e735733078651443b7c0bf56ede4c94f7f5d25](https://github.com/kyvaith/esphome/commit/41e735733078651443b7c0bf56ede4c94f7f5d25). Historia i zakres jego walidacji są w [validation.md](../development/validation.md). Nowe wdrożenia opisane w roadmapie wymagają własnego obrazu, testów i akceptacji; nie dziedziczą wyniku tego checkpointu.

Wstępne odczyty lokalne wykonano na 880c2379dc0718c86771e0ef10ad815b0174bf8e z późniejszymi walidowanymi zmianami, które następnie opublikowano powyżej. Status Baza w roadmapie jest historyczny; bieżąca realizacja nowych funkcji jest oddzielną kolumną.

| Źródło | Przypięta wersja / data | Co rzeczywiście zbadano |
| --- | --- | --- |
| ESPControl | 7c92df26cc8b95cd89780b366ae812bb8af169de, 2026-10-18 | Dokumentacja, kontrakty, aktywne źródła C++/TS i YAML; bez uruchomienia urządzenia lub test suite |
| Tessera main | 6a0df58f5d92d358cc1fef82436aba792a3475c0, 2026-10-23 | Katalog i renderery, add-on/editor/protokół, publiczne metadane wydania i zielonych checks; bez własnego build/device run |
| Tessera wydanie | screens-v0.4.90, 2026-10-23 | Add-on 0.4.90; wspólny firmware 0.57.0; 0.57.1 tylko wybranych Waveshare |
| Tessera wcześniejszy MIT | c0efdb62624c93238ca0e71a2e134b8649921ec4 | Tekst licencji i wybrane funkcje checkpointu 0.4.38; nie wszystkie późniejsze dodatki |
| Mosaico Claw | 2e1017e42d507cd9216d4da5b2c7d45cb2007971 | Źródła factory app/UI i gitlink esp-claw 62aaeed; bez własnego build/device run |
| Mosaico BSP | 7cbfb390638dcb93522fc3cde094b2d43cf907c2 | Płyta, drivers, moduły i przykłady |
| Mosaico Vibe | 1872fd88c01d7807556d01fd2a19864e40a307c9 | Workspace, symulator i CLI |
| Mosaico utils | be151ae047014e79a9c7ae0092dd203844499003 | ESP-Iris, host tools, maintenance firmware i granice licencji |
| Mosaico Matter | 260e636e8a26914082b0f59b6e2330eccd22c7ac | Osobne przykłady hub/bridge; nie domyślna integracja HA |
| ESP-GSP | 2d0e266f80569cee2b18d43ba3c73395f3b73cf0 | Publiczny pakiet, headers/adapters/examples, prebuilt archives i licencja |
| Mosaico oficjalne wydanie | Claw 0.6.0, build 2026-10-23 | Strona firmware i release notes; nie dowód reprodukcji z opublikowanego HEAD |

Odsyłacze do dokładnych źródeł są przy macierzach oraz w indeksie na końcu. Zmienne dane witryn opisują chwilę odczytu 2026-10-24.

Rozdzielamy pięć rodzajów dowodu:

- opis marketingowy — intencja i obietnica, nie wykonany scenariusz;
- dokumentacja — udokumentowany workflow i jego wymagania;
- kod/kontrakt — implementacja w określonej rewizji, czasem za feature flag;
- build/CI — konkretna konfiguracja się buduje lub checks przechodzą;
- sprzęt — dokładny obraz, zachowanie, pomiary i visual QA z ograniczeniami.

Nie uruchamiano obcych projektów, ich edytorów, firmware ani urządzeń. Zielone CI autora nie potwierdza płynności, poprawności DSI czy AEC na Atmosferze. Także liczba plików testowych nie jest liczbą wykonanych testów.

## Co istniało w opublikowanej bazie Atmosfery

Ta sekcja opisuje historyczny checkpoint `6568378`, także tam, gdzie mówi o
11 definicjach, stałym Webhooku lub brakującej lokalizacji JS. Nie opisuje
późniejszego kodu P0. Bieżąca implementacja i jej osobne dowody są w
[rejestrze walidacji](../development/ha-dashboard-2026-10-24.md).

| Obecna funkcja | Granica zakresu | ID chroniące przed błędnym oznaczeniem braku |
| --- | --- | --- |
| HA admin panel i sesja uwierzytelniona | Formularze entity/title/icon/palette/service/visible; nie pełny layout designer | CFG-001/002/009/020 |
| Native ESPHome API i projekcja stanu | Debounce, lock, deduplikacja/retry, changed-slot invalidation; brak applied revision ACK | CFG-010 |
| Kompozycja M3/Wear OS i akcent | Role palet i fixed object pool; nie dowód pełnej zgodności M3 Expressive | UI-001..003 |
| Firmware en-US/pl-PL i HA state translation | JS editor pozostaje do lokalizacji; brak edytora pakietów językowych | UI-004 |
| Camera HA/MJPEG i source picker | Odbieranie istniejących camera.*; nie fizyczna kamera/vision ani miniatury kart | MED-005/006, HW-005 |
| Player/Sendspin, artwork, kolejka | Dedykowana rozbudowana aplikacja; nie dowolna karta każdego media_player | MED-001/003 |
| Speaker grouping i volume | Discovery i kontrola członków już są | MED-002/004 |
| Immich/Gallery | Albumy, osoby/tagi, daty/orientacja, slideshow i lifecycle | MED-009/010 |
| Voice, post-AFE mic i AEC | Backend rozmowy i single physical duplex owner; nie lokalne Chat Coding | DEV-007..010 |
| Pogoda i 9 scen Lottie | Current conditions, jeden cykl i retained phase; brak forecast editor | MED-011/012 |
| Powiadomienia M3 | Kolejka czterech; brak obrazu/akcji/historii | MED-013..015 |
| Brightness/timeout/wake | Polityka aplikacji już jest; brak rozbudowanej obecności/nocy/saver sekwencji | SYS-001..006 |
| Managed HTTP OTA, stable/beta i dashboard import | Nie kompletny web installer/release/recovery UX | SYS-008..011 |
| Native komponenty, snapshots i testy sprzętu | Nowe strony/widgets wymagają jawnej rejestracji i osobnej walidacji | DEV-001/012/013 |

Wszystkie ID w tabelach mają prefiks AEH-. Dowody lokalnej bazy: [A-CARD] [A-PANEL] [A-EDITOR] [A-HA] [A-POOL] [A-CAMERA] [A-PLAYER] [A-GROUP] [A-GALLERY] [A-AUDIO] [A-SET] [A-OTA].

Istotne pułapki: aktywny entrypoint importuje tiles_m3.yaml. Starszy tiles.yaml z gotowym przykładem ustawienia climate na 22 stopnie nie dowodzi tej funkcji w obecnym interfejsie. Jedenaście definicji nie oznacza jedenastu widocznych kart: 0/1 Light i Climate są hidden compatibility objects. Przycisk More otwiera skompilowany ekran karuzeli, a Webhook uruchamia wskazany skrypt HA; nie są to uniwersalna podstrona ani edytor żądań HTTP. [A-HOME] [A-POOL]

## Macierz konfiguracji i platformy

| Obszar | ESPControl | Tessera | Mosaico | Luka/ID Atmosfery |
| --- | --- | --- | --- | --- |
| Konfiguracja WWW | Device-hosted panel, Layout/Screen/System | HA Ingress add-on i editor Vue/Vite/TS | Local IP/SoftAP console dla agenta/usług | Ulepszyć istniejący admin panel HA, CFG-020 |
| Biblioteka encji | Domeny, rodziny i normalizacja | Generated catalogue, capabilities/needs/actions | Brak potwierdzonego HA entity editor | CFG-002, DEV-002 |
| DnD/rozmiary | Move, dozwolone resize, copy/paste | Drag library→grid, multiwybór, resize i collision checks | Gesty drag w aplikacjach; brak dowodu designer HA | CFG-003/004/012/015 |
| Dokument stron | Podstrona/Back; bez zagnieżdżania | Stable page/tile IDs, Home/detail/pager/bar | Natywne aplikacje/launcher, inne pojęcie | CFG-001/014/016/017 |
| Historia edycji | Copy Code/Paste Code i przenoszenie | Undo/redo, drafts, cross-tab revisions | Iteracja kodu/skills; nie ten sam model dokumentu | CFG-006..008/011/012 |
| Zastosowanie | Durable store generation/checksum; oddzielny runtime | Negocjacja, revision/session/seq, begin/commit i ACK | Instalowanie aplikacji/pakietu w maintenance mode | CFG-005/010 |
| Backup/migracja | Własny backup, profile/migracja paneli | Wersjonowany dokument, atomic store, profile/keys osobno | DATA/skills/apps i maintenance; inny zakres | CFG-007/019 |
| Preview | Device geometry w przeglądarce | Prawdziwy LVGL/runtime w WASM, live HA state | GSP/game simulator i Iris screenshot/input | CFG-003/005, DEV-003/004 |
| Runtime controls | Rozbudowane rodziny kart i modale | Domenowe kontrolki i gating | Lua/LVGL lub compiled GSP programowanie aplikacji | CTL-001..031 |
| Aktualizacje i flota | Instalator, OTA/system controls | Add-on build queue, USB/OTA, profiles/remote server | Browser flash, native Ideas i .irisfw | SYS-009..011, DEV-011 |
| Rozszerzenia | Product schema/generatory, source-available | Plugin API 0.14, host code i manifests | Apps/skills/native firmware, agent tools | DEV-002/005..010 |
| Natywny voice assistant | Nie ustalono równoważności | Audio/AFE branch nie dowodzi kompletnego Assist | Agent voice z zewnętrznym ASR/model | Atmosfera ma własny bardziej konkretny kontrakt audio |
| Rendering | ESPHome/LVGL i własne komponenty | ESPHome/LVGL, retained pages/pictures | IDF+GSP, Lua/LVGL, osobny presenter | Zachować nasz P4/DSI i leases |

Źródła: [E-LAYOUT] [E-SUB] [E-STORE] [T-PAGES] [T-DELIVERY] [T-STORE] [T-WASM] [T-PLUGINS] [T-BUILD] [T-AUDIO] [M-GUIDE] [M-VIBE] [M-IRIS] [M-UI].

## Pełny zakres funkcjonalny rodzin kart

Macierz grupuje warianty, aby nie mylić liczby nazw z liczbą niezależnych funkcji. Pełny status i granice akceptacji każdej rodziny są w rejestrze roadmapy.

| Rodzina | Funkcje do porównania / brakujący zakres | Rejestr |
| --- | --- | --- |
| Podstawowe wykonanie | toggle, scene/script/button, input_button, automation run/enable | CTL-001/002/029 |
| Akcje konfigurowane | typowane parametry, osobna encja stanu, lokalny callback, trigger/zdarzenie, webhook przez HA | CFG-009, CTL-026/027/030/031 |
| Lights | power, brightness, Kelvin/RGB/effects, supported modes, stan aktywny | CTL-003/004 |
| Cover/garage/gate | open/close/stop, position/tilt, presets i stany ruchu | CTL-005/006 |
| Fan | power/speed/direction/oscillation/preset, ewentualna osobna lampa | CTL-007 |
| Climate | setpoint lub low/high, HVAC/fan/swing/preset, bounds/step | CTL-008 |
| Number i select | number/input_number stepper/slider; select/input_select options | CTL-009/010 |
| Timer | countdown, start/pause/resume/cancel i potwierdzenie | CTL-011 |
| Zamki i alarm | lock/unlock/open, confirm/lock_only, PIN/code i pending/unavailable; tryby alarmu/disarm | CTL-012/013 |
| Vacuum/mower | start/stop/pause/dock/spot/locate, pokoje/routines/mapy jeśli integracja udostępnia | CTL-014/015 |
| Humidifier | target/mode/toggle | CTL-016 |
| Sensory i obecność | jednostki/precyzja/czas/tekst, local sensor, door/window/presence state | CTL-017/020/026 |
| Dane historyczne | numeric graph/timeline, meter ring/tape/bars | CTL-018/019 |
| Zegar/słońce | date/time, 12/24h, strefy, digital/analog/dial/flip, warianty wygaszacza Digital/Glass/Classic/Bauhaus, sekundy/wygląd/przesuwanie pozycji; sunpath i status | UI-007, SYS-004, CTL-023 |
| Calendar | agenda/day/week/month, event detail/free-busy i booking przy wsparciu HA | CTL-021 |
| Person/map i energia | strefy/foto/pozycja, map provider, agregacje i flow | CTL-022/025 |
| Remotes | activity/power/keypad i katalog komend per integracja | CTL-024 |
| Media | dowolny player, transport/volume/seek/source/shuffle/repeat, library/favourites, speaker/group | MED-001..004 |
| Camera/image | miniatura i expanded, Fit/Fill, visibility/activity refresh, still/MJPEG, audio, doorbell policy | MED-005..008 |
| Galeria | Immich oraz opcjonalne HA media/Synology, memories, filtry, pary portretów | MED-009/010 |
| Pogoda | current, forecast, wiatr/deszcz, wiele dni, min/max i jednostki | MED-011/012 |
| Powiadomienia | kolejka, modal, timeout/tap, action buttons/picture/history | MED-013..015 |
| GIF/ambient/spectrum | bounded image formats/frames, muzyczna wizualizacja i kreatywne światy | MED-016/017 |
| Dane Wi-Fi | guest SSID, QR i ewentualny przełącznik; odseparowane sekrety | CTL-028 |
| Interfejs ekranu | własne strony/Back/header, screen lock, screensaver i remote navigation | CFG-014..018, SYS-004/006/012 |
| Wygląd i język | akcent/role, active/pressed/error, light/dark/solar, font/icon/radius, en/pl/editor locale | UI-001..007 |
| Polityka zasilania | brightness manual/schedule/solar, obecność, night off/dim/clock, tymczasowy wake | SYS-001..007 |

Rodziny i możliwości kart: [E-CARDS] [T-CAT]. Szczegóły specjalistyczne: [T-CALENDAR] [T-ENERGY] [T-MAP] [T-VACUUM] [E-CAMERA] [E-IMMICH] [T-SAVER]. Słowo domena w naszym SUPPORTED_DOMAINS oznacza obecnie tekst/wiązanie i prostą akcję; nie pełny regulator.

### ESPControl: zakres i ograniczenia

Kontrakt zawiera 44 wpisy runtime, w tym default, aliasy i ukryte warianty. Nie jest to 44 niezależne widoczne typy w menu. Pokrycie obejmuje switch/action, lights, fan, climate, cover/garage/gate, vacuum/mower, lock/alarm, date/time/world clock/timer, sensors/presence/door-window, images/weather, media, subpages oraz screen lock/screensaver/Wi-Fi sharing. Jest to szeroki wzorzec wymagań produktu. [E-CARDS]

Karty kamery ESPControl prezentują obrazy/snapshoty i GIF; dokumentacja nie obiecuje video streaming. Miniatury, pozostawianie starego kompletnego obrazu, widoczność, retry/backoff i generacje są wartościowymi pomysłami. Nie zastępują MJPEG Atmosfery. Osobny espcontrol-immich companion ma własny zakres/proweniencję; udokumentowane funkcje zdjęć nie są w całości kodem bazowego firmware. [E-CAMERA] [E-IMMICH]

Uśpienie/obecność/noc, pływający zegar/kamera/artwork saver, PIN, rotacja i display settings są osobnymi funkcjami, a nie wariantami zwykłego timeout. W roadmapie mają osobne ID. [E-SLEEP] [E-APPEAR] [E-SYSTEM]

### Tessera: zakres i ograniczenia

Katalog zawiera 31 plików typów: 30 domen HA i syntetyczne screen. Obejmuje alarm_control_panel, automation, binary_sensor, button, calendar, camera, climate, cover, fan, humidifier, image, input_boolean, input_button, input_number, input_select, light, lock, media_player, number, person, remote, scene, screen, script, select, sensor, sun, switch, timer, vacuum i weather. Katalog i renderery są lepszym źródłem bieżącego zakresu niż starsze przykłady README. [T-CAT]

boards.yaml ma 23 profile: 3 stable, 5 new i 15 experimental. Experimental jest definiowane jako built/rendered bez akceptacji sprzętowej, więc nie wolno pisać o 23 zwalidowanych płytach. Plugin API 0.14 nie ma jeszcze docelowej gwarancji zgodności 1.0. [T-BOARDS] [T-PLUGINS]

Protokół 2 rozdziela strukturę i wartości, negocjuje możliwości oraz wiąże packet z session/seq/revision. Chroni przed starym ACK i aktywuje kompletny transfer przez begin/commit. Nie oznacza dwóch pełnych modeli ani nieograniczonego rollback; po begin wymiana utrzymuje loading cover do commit. Atmosfera może wdrożyć mały revision/ACK bez kopiowania całego protokołu. [T-DELIVERY]

WASM kompiluje runtime/LVGL i używa rzeczywistych dekoderów, co daje mocniejsze preview niż niezależna makieta. Nadal nie symuluje DSI/PPA/cache/audio i timingów fizycznego P4. [T-WASM]

### Mosaico: odmienny produkt, realne źródła

ESP-Mosaico to ESP32-S31 320 MHz, 16 MB PSRAM, 16 MB NOR i 128 MB NAND, 480×480 QSPI AMOLED, mikrofon/głośnik ES8311, IMU/magnetometry, haptics, gauge, mała bateria i dwa module headers. Obecny oficjalny sklep opisuje kit jako preorder za USD 59 z orientacyjną wysyłką po 15 dniach. To stan oferty, nie dowód powszechnej dostępności od ręki. [M-BSP] [M-STORE]

System UI jest budowany z compiled GSP scenes i shared font catalogue. Lua apps używają też LVGL 9; publiczny stack nie jest po prostu tym samym ESPHome/LVGL co Atmosfera. Vibe Mode to oddzielne maintenance firmware, a nie App Store Lua wewnątrz Claw. [M-UI] [M-CLAW] [M-VIBE]

Udokumentowany workflow fabryczny obejmuje chat/voice, skills/Works, pamięć/scheduling, konfigurację model/ASR/network/Wi-Fi i sesje web/IM. Runtime agenta jest lokalny, ale LLM działa na skonfigurowanym serwerze. Dowolnego ASR nie można zastąpić samym nowym URL/key; potrzebna jest implementacja jego protokołu. [M-GUIDE] [M-FAQ]

App Store dodany w 0.5 obsługuje browse/install/uninstall, staging i weryfikację pobrań. Pierwszy zakres nie wspiera overwrite/in-place app update; built-in apps są chronione. Pakiety native .irisfw i sześciocyfrowy kod Ideas wymagają odpowiedniego Vibe Mode. Nie są tym samym co instalowanie Lua app. [M-APPSTORE] [M-VIBE]

Odczytano wszystkie 72 publiczne wpisy software i ich szczegóły: 69 z Iris URL, siedem oznaczonych official. Są aplikacje pogodowe/forecast, zegary/timery, stocks/news, aparaty/foto, gry, pets/companions, ambient/audio visualization i utilities. To nie 72 fabryczne aplikacje ani 72 moduły z jednolitą licencją. W tych rekordach nie znaleziono odwołań Home Assistant/homeassistant/MQTT/Matter. Nie wyklucza to integracji prywatnej lub przyszłej. [M-APPS]

Możliwość programowania custom widgets jest realna: GSP JSON/C API lub Lua/LVGL. Nie dowodzi jednak gotowego WYSIWYG designer HA, dowolnych kart HA czy zgodności protokołu MCP z konkretnym uwierzytelnieniem HA. Oficjalny HA MCP Server wymaga sprawdzenia transportu i OAuth. [M-GSP] [M-MCP] [HA-MCP]

Matter hub i bridge to osobne przykłady firmware. Hub commissionuje urządzenia własnego fabric; bridge wystawia lokalne akcesoria/GPIO. Przykład kamery bridge ma 320×240 H.264 przy 10 FPS, mock Opus silence i stały snapshot JPEG, bez recording; dokumentuje SmartThings live view. Nie jest dowodem importowania dowolnych encji/kamer HA do factory Claw. [M-MATTER] [M-MATTER-CAMERA]

Release 0.6.0 z 2026-10-23 opisuje nowsze gitlinki niż publiczny Claw HEAD zbadany w analizie; nie ustalono reprodukcji binary z tego HEAD. Nowe release notes usuwają update-check entry z Claw settings, choć starsze źródła/README je mają. Starsza strona mosaico.espressif.com nadal pokazuje 0.5.0. [M-FW] [M-CLAW]

## Przenośność i zależności

| Klasa | Co można sensownie przejąć jako wymaganie | Czego nie uznać za małą przenośną zmianę |
| --- | --- | --- |
| HA/browser | Editor, DnD, revision, backup, capabilities, typed actions | Serwer administracyjny na ESP32 albo cały uprzywilejowany add-on nie jest konieczny |
| Firmware UI | Bounded templates, rodziny kontrolek, event/state semantics | Obce źródła renderera i współdzielenia framebufferów nie dowodzą zgodności z naszym DSI |
| HA/host preprocessing | History, forecast, obrazy thumbnails, źródła galerii, optional model | Nie wykonywać ciężkich pobrań/agregacji w per-frame lambdzie |
| Usługi/integracje | HA camera/media/Immich, map provider, ASR/LLM, kalendarz booking | Wymagania konta/protokołu i dostępność regionu nie znikają po dodaniu ikony |
| Sprzęt | Profile możliwości i świadomie nowe moduły | BR/EDR, magnetometry, fizyczna kamera, bateria, haptics, Thread/RCP i GPIO relays wymagają faktycznej elektroniki |
| Developer tooling | Simulation, screen/input/log evidence i package identity | Host preview nie zastępuje sprzętowego FPS/DSI/audio i source-level reprodukcji |

Mosaico ma 480×480 = 230 400 pikseli; Atmosfera 800×800 = 640 000, czyli 2,78 razy więcej. Ilustracyjnie RGB565 480×480 to 460 800 B, a RGB888 800×800 to 1 920 000 B, 4,17 razy więcej. To rachunek geometrii/formatu, nie pomiar transferu lub FPS. Podobny procesor/driver nazewniczo nie daje porównywalnego obciążenia.

Nie przenosimy Tessera kept-pages/picture budget ani globalnych zmian burst PPA jako gotowego rozwiązania: mutex wokół refresh/copy nie zastępuje idle/scanned/queued/staged leases, VSYNC i wyrównania LVGL. Nie dodajemy raw obrazu na każdą stronę/aplikację. Pozostają trzy raw Home slots z JPEG backing, współdzielony app work, bounded Lottie/direct regions i jawne pause/drain/release. [A-NAV] [A-CAMERA] [T-MEM] [T-CAMERA]

## Licencje i granica adaptacji

| Źródło | Ustalenie | Granica dla tego projektu |
| --- | --- | --- |
| ESPControl | PolyForm Noncommercial 1.0.0, source-available | Analiza wymagań; nie kopiować C++/TS/JSON/generatorów/assetów do produktu/upstream bez odpowiednich osobnych praw |
| Tessera current main | AGPL-3.0-or-later i third-party NOTICE | Domyślnie niezależna implementacja; aktualny kod nie jest MIT |
| Tessera do 0.4.38 | MIT w dokładnym c0efdb...; current NOTICE zachowuje historię | Możliwa analiza konkretnego wcześniejszego pliku z provenance/notice; nie obejmuje wszystkich późniejszych dodatków |
| Mosaico Claw/BSP | Root Apache-2.0 | Zachować autorstwo/notice i osobne licencje zależności |
| Mosaico Vibe/Matter | Brak root LICENSE w captured trees | Publiczne repo nie daje samo pełnego grant; sprawdzać per-file/subtree |
| Mosaico utils | ESP-Iris Apache-2.0; Recovery/host tools mają jawnie brak repo-level grant | Nie przypisywać Apache-2.0 całemu monorepo |
| ESP-GSP | Espressif Modified MIT, ograniczone do Espressif products | Publiczny pakiet ma prebuilt archives; nie twierdzić pełnej dostępności źródeł runtime/compiler |
| Community apps/assets | Różne lub brak metadata license | Oddzielne pochodzenie aplikacji, fontów, zdjęć, dźwięków i firmware |

Dowody: [E-LICENSE] [T-LICENSE] [T-NOTICE] [T-MIT] [M-LICENSE] [M-GSP-LICENSE]. Zmiana licencji Tessera nastąpiła w [eb36f779ef03aa7f4b7c53bdb06687cecaed15a6](https://github.com/MaxGramser/homeassistant_espscreen/commit/eb36f779ef03aa7f4b7c53bdb06687cecaed15a6), 2026-10-01. Nie znaleziono tagu screens-v0.4.38; nie zastępować dokładnego SHA wymyślonym tagiem.

Publiczny ESP-GSP tree ma include/adapters/docs/examples i prebuilt/<target>/libesp-gsp.a, lecz nie src runtime ani compiler source. Kconfig domyślnie wybiera prebuilt consumer path. Marketingowe określenie otwartego stacku nie znosi tej granicy. [Pakiet GSP](https://github.com/espressif/esp-gsp/tree/2d0e266f80569cee2b18d43ba3c73395f3b73cf0), [Kconfig](https://github.com/espressif/esp-gsp/blob/2d0e266f80569cee2b18d43ba3c73395f3b73cf0/Kconfig).

W dokumentowanej adaptacji nie skopiowano kodu obcych produktów. Kontrakty Atmosfery i jej wdrożenia są projektowane niezależnie; analiza licencji wskazuje teksty i pochodzenie, nie zakłada dowolności przyszłego łączenia.

## Kierunek wzorniczy i kolejność wdrożeń

Celem nowych funkcji jest Material Design 3 Expressive rozwijające obecne M3/Wear OS, z tym samym akcentem, rolami, typografią, grupami kształtów i czytelnym feedback. To intencja, nie zakończona certyfikacja całego produktu. Źródłem geometrii/komponentów pozostaje [wearos-m3-map.md](../design/wearos-m3-map.md); [M3 Expressive][M3] jest kierunkiem projektu.

Pierwszy krok to wizualna obsługa znanych slotów i typed actions w HA, z profilem echo-hub-m3-v1. Roadmapa zawiera zatwierdzoną mapę 16 prekompilowanych slotów; slots 0/1 pozostają hidden, Home/Apps są read-only, edytowalne Security/Controls. Ten nowy zakres nie jest jeszcze walidowany przez bazowy checkpoint.

Dalej rzeczywiste regulatory light/climate/cover/fan/number/select/timer i czytelne lock/alarm flow; potem elastyczne bounded strony/podstrony i kolejne dane/widżety. Dowolne strony/resize wymagają kontraktu navigation, hit-test i memory admission, więc nie są obietnicą pierwszego DnD. Native controls, ustawione parametry tap action, zapis HA i applied ACK mają oddzielne ID/dowody.

Nowe komponenty zachowują wszystkie reguły [AGENTS.md](../../AGENTS.md), [extending-ui.md](../development/extending-ui.md) i [validation.md](../development/validation.md). Dokumentacja tej analizy nie jest zgodą na pomijanie compile/flash/hardware/visual gates.

## Indeks źródeł i materiałów audytu

Kod A-* oznacza opublikowaną bazę Atmosfera; E-* — ESPControl; T-* — Tessera; M-* — Mosaico/Espressif. Linki są przypięte do badanych rewizji tam, gdzie źródło na to pozwala. Dokument roadmapy używa tych samych kodów i pełnych definicji odsyłaczy.

Raporty robocze, kopie źródeł i publiczne metadata są poza Git w C:/aeh-build/feature-research-20261024: espcontrol-research.md, espscreen-research.md, mosaico-research.md i mosaico-source-manifest.json. Nie są wymagane do odczytania tej dokumentacji; kluczowe dowody prowadzą bezpośrednio do źródeł.

[A-CARD]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/custom_components/atmosfera_echo_hub/cards.py
[A-HA]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/custom_components/atmosfera_echo_hub/controller.py
[A-PANEL]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/custom_components/atmosfera_echo_hub/panel.py
[A-EDITOR]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/custom_components/atmosfera_echo_hub/www/tile-editor.js
[A-HOME]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/modules/lvgl/pages/tiles_m3.yaml
[A-POOL]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/modules/lvgl/material.yaml
[A-NAV]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/docs/architecture/navigation-snapshots.md
[A-CAMERA]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/docs/architecture/camera-streaming.md
[A-AUDIO]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/docs/architecture/audio-voice.md
[A-PLAYER]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/modules/player/runtime.yaml
[A-GROUP]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/modules/player/speaker_grouping.yaml
[A-GALLERY]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/modules/immich/runtime.yaml
[A-SET]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/modules/common/system_settings.yaml
[A-OTA]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/modules/common/managed_updates.yaml
[A-VALID]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/docs/development/validation.md
[A-DESIGN]: https://github.com/kyvaith/Atmosfera-Echo-Hub/blob/65683789d83ceb4510b202ce98979043c8f5e2f6/docs/design/wearos-m3-map.md
[E-CARDS]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/generated/cards/capabilities.md
[E-LAYOUT]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/features/setup.md
[E-SUB]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/features/subpages.md
[E-APPEAR]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/features/appearance.md
[E-SLEEP]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/settings/sleep.md
[E-SYSTEM]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/settings/system.md
[E-CAMERA]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/card-types/cameras.md
[E-IMMICH]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/docs/immich/index.md
[E-STORE]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/components/espcontrol/configuration_store.h
[E-LICENSE]: https://github.com/jtenniswood/espcontrol/blob/7c92df26cc8b95cd89780b366ae812bb8af169de/LICENSE
[T-CAT]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/CATALOGUE.md
[T-PAGES]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/PAGES.md
[T-DELIVERY]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/screen_manager/app/page_delivery.py
[T-STORE]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/screen_manager/app/layout_store.py
[T-PLUGINS]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/PLUGINS.md
[T-WASM]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/web/wasm/README.md
[T-CAMERA]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/CAMERA.md
[T-AUDIO]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/P4_AUDIO.md
[T-BUILD]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/BUILDS.md
[T-SAVER]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/SCREENSAVER.md
[T-CALENDAR]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/CALENDAR.md
[T-ENERGY]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/ENERGY.md
[T-MAP]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/MAP.md
[T-VACUUM]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/VACUUM.md
[T-MEM]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/docs/TILE_MEMORY.md
[T-BOARDS]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/boards.yaml
[T-LICENSE]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/LICENSE
[T-NOTICE]: https://github.com/MaxGramser/homeassistant_espscreen/blob/6a0df58f5d92d358cc1fef82436aba792a3475c0/NOTICE
[T-MIT]: https://github.com/MaxGramser/homeassistant_espscreen/blob/c0efdb62624c93238ca0e71a2e134b8649921ec4/LICENSE
[M-GUIDE]: https://mosaico.ai/en/guide
[M-FAQ]: https://mosaico.ai/en/faq
[M-FW]: https://mosaico.ai/en/firmware
[M-STORE]: https://store.mosaico.ai/products/esp-mosaico
[M-APPS]: https://mosaico.ai/en/software
[M-CLAW]: https://github.com/esp-mosaico/esp-mosaico-claw/blob/2e1017e42d507cd9216d4da5b2c7d45cb2007971/README.md
[M-UI]: https://github.com/esp-mosaico/esp-mosaico-claw/blob/2e1017e42d507cd9216d4da5b2c7d45cb2007971/components/mosaic_ui/README.md
[M-APPSTORE]: https://github.com/esp-mosaico/esp-mosaico-claw/blob/2e1017e42d507cd9216d4da5b2c7d45cb2007971/fatfs_image/system/apps/app_store/README.md
[M-BSP]: https://github.com/esp-mosaico/esp-mosaico-bsp/blob/7cbfb390638dcb93522fc3cde094b2d43cf907c2/README.md
[M-VIBE]: https://github.com/esp-mosaico/esp-mosaico-vibe/blob/1872fd88c01d7807556d01fd2a19864e40a307c9/README.md
[M-IRIS]: https://github.com/esp-mosaico/esp-mosaico-utils/blob/be151ae047014e79a9c7ae0092dd203844499003/ESP-Iris/components/esp_iris/README.md
[M-LICENSE]: https://github.com/esp-mosaico/esp-mosaico-utils/blob/be151ae047014e79a9c7ae0092dd203844499003/LICENSES.md
[M-GSP]: https://github.com/espressif/esp-gsp/blob/2d0e266f80569cee2b18d43ba3c73395f3b73cf0/README.md
[M-GSP-LICENSE]: https://github.com/espressif/esp-gsp/blob/2d0e266f80569cee2b18d43ba3c73395f3b73cf0/LICENSE
[M-MATTER]: https://github.com/esp-mosaico/esp-mosaico-matter/blob/260e636e8a26914082b0f59b6e2330eccd22c7ac/README.md
[M-MATTER-CAMERA]: https://github.com/esp-mosaico/esp-mosaico-matter/blob/260e636e8a26914082b0f59b6e2330eccd22c7ac/examples/matter_bridge/README.md
[M-MCP]: https://esp-claw.com/en/reference-cap/cap-mcp/
[HA-MCP]: https://www.home-assistant.io/integrations/mcp_server/
[M3]: https://m3.material.io/blog/building-with-m3-expressive
