# Wznowienie funkcji — 30 października 2026

## Publikacja przed wznowieniem

Użytkownik zlecił publikację, a następnie wznowienie funkcji. Oba commity
potwierdzono przez odczyt zdalnych gałęzi `feature/ha-dashboard-2026-10-24`:
Atmosfera `5de0e0789ab8b9cc76adc2de5195e622370e51d9`, ESPHome
`62745ae0c43a233760ddaf1fed60867736832547`. Oba katalogi były czyste w chwili
odbioru publikacji. Dowód: `publication-receipt.json` pod
`C:\aeh-build\publication-resume-20261030`. Późniejsze prace nie są automatycznie
commitowane ani wypychane.

## HA20: pasywna karta najbliższego wschodu/zachodu — odbiór ograniczony PASS

Świeży odczyt HA Core 2026.7.1 potwierdził integrację 0.4.0.dev20, 25/25 zgodnych
plików po normalizacji końców linii, 16 kart, 3 kamery i rewizję 16. Żadne źródła
HA ani konfiguracja kamer nie były zmieniane. Zachowany native31 wgrano ponownie
przez OTA, jedna próba zakończona 15:10:17 UTC. Pełny ELF:
`f78afc026eb0da1d2d536560871bbf2c521134cc0858b462888eb939f5f1bd59`.
Nie budowano innego firmware: funkcja używa istniejącej projekcji tekstu z HA.

Kampania `sun-device-v3` używała jednej własnej, wcześniej nieistniejącej encji
`sun.atmosfera_qa_sun_20261030`. Zwykły walidowany zapis CAS zmienił tylko pięć
pól karty `info-20261024-15` na slocie 15. Nie zmieniano prawdziwego `sun.sun`,
strefy HA, zegarów, preferencji urządzenia ani stanu domowych urządzeń.

Pięć poprawnych podpisów potwierdzono w eksporcie natywnego modelu i na
oryginalnych obrazach 800×800 z urządzenia:

| Dane własnej encji | Podpis na urządzeniu |
|---|---|
| unknown | Nieznany |
| bliższy zachód, oba znaczniki ze strefą i przyszłe | Zach. 30.10 18:12 |
| bliższy wschód, po lokalnej północy | Wsch. 31.10 00:12 |
| jeden znacznik bez strefy | Nieznany |
| unavailable | Niedostępny |

Sprawdzono regularny tekst w obsługiwanym miejscu; nie dopuszczano tych długich
podpisów do dużych liczbowych slotów 13/14. Wycinki kontrolne i pełne oryginały
są obok raportu. Odbiór nie obejmuje wykresu Sunpath, elevation, automatycznego
motywu ani zmiany strefy HA; angielskie napisy i DST pozostają sprawdzone hostowo.

Przywrócenie przeszło: wszystkie 16 definicji kart są dokładnie takie jak przed
testem, łącznie z pozycjami użytkownika i rzeczywistym
`sensor.indoor_temperature`. Rewizja naturalnie wzrosła 16→17→18; nie cofano
licznika. Źródłowy model urządzenia potwierdził przywróconą kartę „W domu”,
a encję QA usunięto dopiero po odpięciu z HA i firmware. Token sesji odwołano,
osiem preferencji zachowano. Końcowy Home1 ma komplet kontrolek w oryginalnych
pikselach. Brak awarii API, restartów i DSI underrun w scenariuszu.

PSRAM przed/po: 4893/4893 KiB; snapshot 6549 KiB, w tym trzy surowe sloty
5625 KiB i JPEG 924 KiB w obu odczytach. raw/app_work/scroll/close = 0.
Internal 34→33 KiB. Późniejszy pomiar Ustawień: 79 klatek, 54 FPS,
średnio 15895 µs, max 23211 µs, 0 nieudanych; poprzedni native31 miał
54 FPS / 16430 µs i 54 FPS / 16090 µs.
Nie wykazano pogorszenia przewijania ani nowego dużego bufora. Nie testowano
ciągłego audio ani fizycznego dotyku GT911; wejście używało listenera LVGL.

Dwie wcześniejsze próby zakończyły się **przed utworzeniem encji i zapisem**:
v1 miała błędną nazwę pola eksportu w helperze; v2 wymagała gotowości snapshotu
po skrócie diagnostycznym, który pomija callback normalnego settle. V3 dochodzi
do Home4 trzema pełnymi gestami. Nie zmieniono firmware, żeby dostosować go do
testu. Nie uznawać samych pending masek off-window za błędu ani fizycznego ACK.

Dowody poza Git: `sun-device-v3/report.json`, `original-layout.json`,
`bound-layout.json`, `restored-layout.json`, `device.log`, obrazy oraz
`sun-post-benchmark/report.json`. Pięć testów czystego planu potwierdza ochronę
tożsamości i zachowanie niezależnych edycji użytkownika podczas przywracania.

## HA21: aktualne stany i możliwości w bibliotece encji — PASS w badanym zakresie

Przyczyną rozbieżności był stan zachowany w wyniku poprzedniego zapytania
katalogu. Podgląd korzystał z bieżącego `hass.states`, lecz biblioteka wyświetlała
`entity.state`. HA21 aktualizuje tekst i klasę dostępności istniejących etykiet
z danych frontendu, bez wymiany wierszy i utraty fokusu, szkicu czy historii.
Porównanie referencji stanów obejmuje także zmiany samych atrybutów.
Metadane możliwości nadal pochodzą z serwera. Odświeżają się przy istniejącym
odczycie statusu co pięć sekund, tylko po zmianie używanej encji. Zapytania są
łączone, opóźnione odpowiedzi poprzedniego urządzenia odrzucane, a odświeżenie
odkładane podczas przeciągania, zapisu, potwierdzania lub fokusu na liście.
Nie dodano timera, subskrypcji ani odpytywania firmware.

Walidacja lokalna: **227 testów Node PASS** (219 wcześniejszych i osiem nowych),
**385 testów Python OK, trzy pominięte**. Dwa nowe testy etykiet uruchomione
przeciw staremu źródłu celowo nie przeszły, potwierdzając wykrywanie regresji.
Ruff i kontrola białych znaków przeszły. Logi: `catalogue-node-focus-final.log`,
`catalogue-node-old-negative.log`, `ha21-python-tests.log`.

Wdrożono `0.4.0.dev21`. Odczyt przez SSH potwierdził **25/25 zgodnych plików**,
niezmienione skróty danych i opcji wpisu, rewizję 18, 16 kart i trzy kamery.
Końcowy JS SHA-256:
`2c1d7051c5cdff5932b4aa44d38edf87c76f0e7a261d7575ff700c9cf93273c2`.
Odpowiedź API potwierdziła panel, dostępne urządzenie i przyjętą rewizję 18.

Instalacja wymagała **dwóch restartów HA**. Początkowo własną kopię HA20
pozostawiono jako ukryty katalog obok integracji. Loader HA odczytał jej manifest,
powstał konflikt domeny i panel był chwilowo niedostępny. Po weryfikacji wszystkich
skrótów przeniesiono kopię poza katalog komponentów do
`/usr/share/hassio/homeassistant/.atmosfera-development-backups/ha20-c78b0ed1591343cd82a4a8ec5a1a4f3d`.
Drugi restart przywrócił panel i API; nie utracono konfiguracji.
**Kopie wdrożeniowe muszą znajdować się poza `/config/custom_components`, także
gdy ich nazwa zaczyna się od kropki.** Pierwotny nieudany start zachowano w
`ha21-startup-diagnostics.json`, odzyskanie w `ha21-backup-recovery.json`.

Test w rzeczywistej przeglądarce używał wyłącznie własnej, nieprzypiętej encji
`light.atmosfera_qa_catalog_20261030`: unknown → on → unavailable → usunięta.
Stary panel pozostał na unknown po zmianie na on; nowy pokazał on, następnie
unavailable i styl niedostępności. Po usunięciu encji lista sama wróciła do
zera wyników. Wyszukiwanie i fokus zostały zachowane, Zapisz pozostało wyłączone.
Nie wywołano usług ani zapisów układu. Właściciela i brak odwołań sprawdzono
przed usunięciem; odpowiedź 404 potwierdziła brak encji. Na koniec wyczyszczono
filtr. Obrazy: `catalogue-browser-before.jpg`, `catalogue-browser-after.jpg`,
`catalogue-browser-unavailable.jpg`; odczyt końcowy: `catalogue-browser-cleanup.json`.

## Kontrola urządzenia po HA21

Firmware pozostał native31; nie kompilowano nowego obrazu dla zmian wyłącznie HA.
Ponowny pomiar Ustawień: **81 klatek, 55 FPS, średnio 16110 µs, max 23892 µs,
zero nieudanych**. Osiem preferencji pozostało zgodnych. Galeria prezentowała
95 klatek przy 39,2 FPS. Pierwszy skrypt multimediów zatrzymał się na braku
oczekiwanej linii diagnostycznej aplikacji kamery; nie odebrał linii ze złym
stanem. Zachowano ten niezaliczony przebieg, zamiast uznać go za PASS.

Osobny test potwierdził stan otwartej kamery, `has_frame=YES`, wzrost licznika
**prezentacji o 78 klatek**, 12,3–13,3 FPS i dwa oryginalne obrazy strumienia.
Po normalnym zamknięciu bufor kamery miał 0 KiB, raw/app_work/scroll/close = 0,
a Home1 był kompletny. Nie wykryto restartu ani błędu DSI w tym przebiegu.
Oryginalne piksele Home po pomiarze i kamerze przeszły kontrolę pogody,
mikrofonu, wskaźników i statusu. Obrazy kamery obejrzano osobno. Stan rozgrzanych
JPEG aplikacji po multimediach nie jest porównywalny z zimnym pomiarem Sun;
nie wyciągać z niego wniosku o całkowitym zużyciu pamięci ani długim lifetime.

Dowody: `ha21-device-benchmark/report.json`, `ha21-device-media/report.json`
(niezaliczony obserwator), `ha21-camera-confirm/report.json`,
`ha21-device-home-final.json` oraz oryginalne obrazy pod wspólnym katalogiem
`C:\aeh-build\publication-resume-20261030`. Nie testowano fizycznego dotyku,
ciągłego audio, prawdziwej lampy ani wielogodzinnej stabilności.

## HA22: konfigurowalny czas timera i podpis anulowania — odbiór ograniczony PASS

Katalog `timer.start` otrzymał opcjonalne `duration`: 1–86400 pełnych sekund.
Obie warstwy walidacji odrzucają zakres, ułamki, boolean, tekst, NaN i nadmiarowe
pola. Formularz PL/EN podaje jednostkę i wyjaśnia znaczenie pustego pola.
Pusty parametr nadal jest pomijany; domyślne Start/Pauza/Wznów nie zmieniają
semantyki. Kafelek jawnego presetu pokazuje np. „Uruchom 1:30”, a jawnego
`timer.cancel` — „Anuluj”. To nazwa akcji, nie potwierdzenie jej wykonania.
Nie dodano cyklicznego odświeżania, natywnego timera, pola wire ani bufora.

Końcowe testy: **393 Python OK, trzy pominięte; 229 Node PASS**. Nowe osiem
testów Python i dwa Node obejmują granice, brak parametru przy resume, publikację
metadanych bez mutacji, PL/EN, brak usługi/dostępności, odrzucenie starej rewizji
i jedno wywołanie z kontekstem. Ruff i kontrola białych znaków przeszły.
Logi: `ha22-python-final.log`, `ha22-node-tests.log`.

HA22 zainstalowano jednym kolejnym restartem. Kopię HA21 od początku umieszczono
poza loaderem komponentów, poprzez wymianę katalogów. Pakiet oraz odczyt SSH
potwierdziły 25/25 plików. Konfiguracja wpisu, kart i trzech kamer nie zmieniła
się podczas wdrożenia. Ścieżka rollbacku i skróty są w `ha22-deployment.json`.

Kampania `timer-preset-v1` stworzyła przez publiczne API HA jeden własny pomocnik
z unikalnym ID i domyślnym czasem 12 godzin. Na tej samej chronionej karcie 15
przetestowała trzy natywne dotknięcia, przez pełny listener LVGL:

1. Preset: dokładnie jeden `timer.start(duration=90)`, rzeczywiste active,
   duration=0:01:30 i odpowiednia przyszła chwila zakończenia.
2. Po pauzie wykonanej wyłącznie na własnym timerze przez operator QA:
   `timer.start` bez duration, rzeczywiste active i zachowane remaining=0:01:28.
3. Anulowanie: dokładnie jeden `timer.cancel`, rzeczywiste idle, brak deadline
   i remaining, powrót skonfigurowanego duration=12:00:00.

Obserwator HA zachował dokładną sekwencję usług start(90), pause, start(), cancel
oraz zdarzenia stanów. Oryginalne obrazy obejmują gotowy preset, aktywny timer,
wznowienie, „Anuluj”, idle i przywróconą kartę. Wycinki presetu i anulowania
obejrzano. Nie wywołano usług domowych urządzeń. Przywrócono wszystkie 16
definicji kart, zachowano osiem preferencji, a własny pomocnik usunięto po
świeżym odpięciu z HA i firmware. Rewizje: 18→19→20→21→22. Nie cofano licznika.
Końcowy Home1 ma komplet kontrolek w oryginalnych pikselach; faults jest puste.

Osobny odbiór formularza użył własnej, nieprzypiętej encji runtime
`timer.atmosfera_qa_editor_20261030`. Wyłącznie w szkicu przeglądarki wybrano
`timer.start`, pokazano pole „Czas (sekundy)”, min/max/step i tekst pomocy.
90 było poprawne, 1.5 otrzymało błąd, a puste pole wróciło do poprawnego stanu.
Wszystkie edycje cofnięto bez zapisu, przywrócono „W domu”, usunięto encję,
odświeżono edytor: pusty filtr, Zapisz wyłączone, brak szkicu QA.
Obraz pola z otoczeniem: `timer-preset-browser-field.jpg`.

### Wydajność: znaczenie normalnej drogi wejścia

Pierwszy pomiar po kampanii: 69 klatek, **46 FPS**, średnio 19633 µs,
max 28564 µs, zero failed, **14 segmentów**. Zachowano go w
`ha22-device-benchmark`. Log ma `trim=NO`, trzy raw sloty Home, odmowę pożyczki
ciągłego bufora i snapshot Ustawień 3571 KiB podzielony na części.
Operator kończył kampanię przez `debug_navigation_home`, który pomija normalny
callback przygotowania Home. Kolejność logów i kontrakt komponentu wskazują,
że aktualne okno zostało przygotowane dopiero po próbie trim; nie traktować
samego odczytu `home_page=1` jako dowodu gotowości jego cache.

Bez flashu, resetu, zmiany preferencji ani kodu wykonano następnie
**Home1→Home2→Ustawienia→Home2→Home1** zwykłymi gestami listenera LVGL.
`trim=YES`, pożyczka 3657600 bajtów przeszła, snapshot miał jeden segment:
**79 klatek, 54 FPS, średnio 16670 µs, max 23491 µs, failed=0**.
Przy powrocie ograniczony reclaim sześciu nieużywanych preview odzyskał
1391607 bajtów i udany retry odbudował trzy raw sloty. Końcowo raw/app_work/
scroll/close=0, camera=0 KiB; PSRAM 4585 KiB, największy blok 3200 KiB.
To rozgrzany stan po multimediach, nie porównanie zimnej pamięci z Sun.

Raport `ha22-real-home` potwierdza pełny ELF, oba rzeczywiste przejścia,
zachowanie preferencji, brak awarii i kompletny oryginalny Home. Ten scenariusz
potwierdza utrzymanie przewijania po HA22; wynik 46 FPS nadal dokumentuje koszt
fragmentarycznego fallbacku. Nie dowodzi to braku regresji audio, fizycznego
GT911 ani wielogodzinnego lifetime. Nowe funkcje pozostają lokalne po wcześniej
opublikowanym checkpointcie obu repozytoriów.

Zbiorczy odbiór ograniczonego zakresu:
`C:\aeh-build\publication-resume-20261030\resumption-acceptance.json`.
Weryfikuje skróty oryginalnych obrazów i źródeł HA22, dokładne przywrócenie kart,
zgodne konteksty usług i stanów timera, końcowe preferencje oraz normalną drogę
do Ustawień. Nie zastępuje brakujących poziomów odbioru wymienionych powyżej.
