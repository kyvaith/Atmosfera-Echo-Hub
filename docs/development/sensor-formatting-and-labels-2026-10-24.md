# Formatowanie sensorów i pasy etykiet — 2026-10-24

Lokalny przyrost implementacji CTL-017/020 i prezentacji istniejących kart,
po [pierwszych trzech przyrostach edytora](editor-three-features-2026-10-24.md).
Nie zamyka całych rodzin funkcji z [planu wykonania](implementation-plan-2026-10-24.md).
Kod HA i źródła natywne mają osobne granice odbioru. Późniejsze rzeczywiste
wdrożenie HA, screenshoty v9 i ograniczenia nieudanych prób cleanup opisuje
[aktualny zapis odbioru](live-ha-deployment-2026-10-24.md). Poniższa tabela
zachowuje stan checkpointu sprzed tych kolejnych prób.

<!-- BEGIN SENSOR_FORMATTING_STATUS -->
## Status po flashowaniu v9, podczas odbioru sprzętowego

| Warstwa | Ostatni potwierdzony status | Znaczenie |
| --- | --- | --- |
| Python/host | **PASS: 167/167, wynik root** | 112 dotychczasowych backendu + 28 formatowania + 15 stateless + 7 geometrii + 5 katalogu ikon; historyczne 147 opisano niżej; bez rzeczywistego HA i renderowania LVGL |
| Node/edytor | **Wcześniejsze 61/61 PASS** | Osobny wcześniejszy wynik, nie jest częścią liczby 167 |
| Konfiguracja i pełny build v8 | **PASS** | Zachowane artefakty i uruchomiona tożsamość v8; sam build nie potwierdza jakości ekranu |
| Flash i identyfikacja v8 | **PASS** | Pełny running ELF `ffb2ad7f…749139f`, marker `2026-10-24 16:40:25 +0200` |
| Pasy/formatowanie na v8 | **Cztery próby machine PASS; wykryty błąd glifów** | Pełny readback i normalized-native dedup potwierdzone; wizualnego odbioru ikon nie można uznać za PASS |
| Konfiguracja/build i zachowanie v9 | **PASS** | Nowy build z jedyną deltą native w fontach; manifest artefaktów z `15:19:05 UTC` |
| Flash i running identity v9 | **PASS, potwierdzone przez root** | OTA exit 0 i odczyt pełnego running ELF zgodnego z zachowanym v9 |
| Urządzenie/screenshoty/wydajność v9 | **ONGOING** | Wygenerowane glify nie zastępują bieżącego odbioru ekranu i osobnego pomiaru |
| Porównanie wydajności/pamięci | **Ograniczone obserwacje v8; brak globalnego PASS** | Większe wall counters i różnice stanu pamięci zachowano; v9 wymaga osobnego pomiaru |
| Pakiet HA v4 | **Lokalny, 0.4.0.dev2; NIEZAINSTALOWANY** | 18 plików, zweryfikowane CRC i deterministyczny rebuild; pakowanie nie dowodzi wdrożenia |
| Instalacja i odbiór rzeczywistego HA | **PENDING** | Dostęp został przekazany; instalacja, restart, logi i rzeczywiste usługi/stany pozostają do sprawdzenia |

Root potwierdził OTA i running identity v9; kolejne próby sprzętowe i pogodowe
trwają. Nie przypisano im jeszcze wyniku. Root uzupełnia kolejne warstwy dopiero
po otrzymaniu odpowiadających im dowodów. Pola `flashed:false` w
niezmiennych manifestach zachowania artefaktów opisują chwilę ich utworzenia;
nie zastępują późniejszego, osobnego raportu uruchomionej wersji.
<!-- END SENSOR_FORMATTING_STATUS -->

## Własność danych i aktualizacji

| Właściciel | Odpowiedzialność |
| --- | --- |
| `custom_components/atmosfera_echo_hub/formatting.py` | Czyste formatowanie tekstu z przekazanej wartości, jednostki, klasy, języka i opcji; bez dostępu do urządzenia, zapisów opcji i wywołań usług |
| `custom_components/atmosfera_echo_hub/cards.py` | Odczyt bieżących `hass.states`, opcji publicznego rejestru i tłumaczeń; złożenie ograniczonej projekcji 16 slotów |
| Istniejący `controller.py` | Dotychczasowe subskrypcje stanów kart, debounce, blokada wysyłki, deduplikacja payloadu oraz obsługa układu, języka i połączenia |
| `modules/lvgl/pages/tiles_m3.yaml` | Stała geometria pasów tekstu istniejących etykiet; pełny tekst pozostaje w ich pamięci |
| `lvgl_material.MaterialTileSurface` w forku ESPHome | Istniejąca aktualizacja tekstu/kolorów na zadaniu LVGL, oznaczenie zmienionych slotów i dotychczasowy cykl snapshotów |

Nie dodano nowego zadania, workera, timera, surowego bufora obrazu, per-kartowego
snapshotu ani dynamicznego drzewa LVGL. Home nadal używa trzech surowych slotów;
nie zmieniono własności buforów DSI, rejestracji stron ani reguł przekazywania
ekranu. Zmiana tekstu korzysta z dotychczasowej ścieżki odświeżania snapshotu,
opisanej w [architekturze dashboardu](../architecture/home-assistant-dashboard.md).

Precyzja jest czytana przy każdej istniejącej projekcji prezentacji. Nie dodano
subskrypcji zmian samego rejestru encji: edycja wyłącznie opcji precyzji zostanie
uwzględniona przy następnym istniejącym wyzwoleniu push, np. zmianie stanu,
układu, języka lub odtworzeniu połączenia. Nie ma obietnicy natychmiastowej
reakcji na sam zapis metadanych rejestru.

Formatowanie nie zmienia encji, zapisanych tytułów, ikon wybranych przez
użytkownika, palet, stabilnych ID, akcji ani semantyki kopiowania. Nie dodaje
natywnego regulatora. Dotychczasowe specjalne opisy klimatu, wentylatora i mediów
pozostają odrębnymi ścieżkami. Duży zegar i pogoda Home są bez zmian.

## Liczby i stany wyjątkowe

Ścieżka liczbowa obejmuje `sensor`, `number` i `input_number`. Korzysta z wartości
i jednostki bieżącego stanu HA; nie wykonuje ogólnych przeliczeń jednostek.
Dla `sensor` odczytuje `RegistryEntry.options['sensor']` bez modyfikowania tego
mapowania. Najpierw używa poprawnego całkowitego `display_precision`, potem
`suggested_display_precision`; w przeciwnym razie wyprowadza precyzję z zapisu
dziesiętnego stanu. Tę kolejność potwierdza
[kod sensora HA 2026.7.1](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/sensor/__init__.py#L735-L744),
a publiczny, chroniony przed zapisem charakter opcji —
[definicja rejestru encji](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/helpers/entity_registry.py#L149-L209).

Poniższe limity są polityką Atmosfery, a nie deklaracją limitów HA:

| Właściwość | Zachowanie |
| --- | --- |
| Wejście liczbowe | Zapis ASCII ze znakiem, kropką i opcjonalnym wykładnikiem; usuwa otaczające białe znaki; budżet parsowania 128 znaków |
| Zakres wartości | Wartość bezwzględna do `1e15`, włącznie |
| Precyzja | 0..6 miejsc; wartości całkowite spoza przedziału są ograniczane, `bool`/`float`/tekst nie są precyzją |
| Zaokrąglanie | `Decimal`, half-even, własny kontekst o precyzji 32; brak zależności od globalnego trybu zaokrąglania, flag, pułapek i granic wykładnika wywołującego |
| Znak i separator | Zwykły minus ASCII, usunięcie ujemnego zera; przecinek dla PL, kropka dla EN; brak separatora tysięcy |
| Jednostka | Bieżąca jednostka HA, zachowana wielkość liter; normalizacja do czystego tekstu i limit 20 znaków |
| Wynik | Czysty tekst do 40 znaków; limit może skrócić bardzo długą jednostkę |

Zastosowanie kolejności precyzji HA nie oznacza identycznego wyniku każdej
reprezentacji frontendowej: publiczne
[`async_rounded_state` HA](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/sensor/__init__.py#L969-L990)
korzysta z `float`, a tutaj świadomie zachowano dziesiętną wartość przez
`Decimal`. Integracja nie wywołuje prywatnego helpera HA.

| Dane | EN | PL |
| --- | --- | --- |
| `21.345 °C`, precyzja 1 | `21.3 °C` | `21,3 °C` |
| `2.675 V`, precyzja 2 | `2.68 V` | `2,68 V` |
| `-0.0001 V`, precyzja 2 | `0.00 V` | `0,00 V` |
| Stan `unknown` lub błędne/nieskończone dane liczbowe | `Unknown` | `Nieznany` |
| Stan `unavailable` lub brak encji | `Unavailable` | `Niedostępny` |
| Skończony zapis liczbowy poza budżetem wartości/reprezentacji | `Out of range` | `Poza zakresem` |

Brak danych i przekroczenie zakresu nie są tym samym stanem. Żaden z nich nie
staje się zerem ani bezpiecznym stanem binarnym. Klasy tekstowe `enum`, `date`,
`timestamp`, `uptime` oraz rozpoznane własne stany tekstowe bez jednostki mogą
przejść do istniejącej ścieżki tłumaczeń. Nie obiecuje to interpretacji dowolnego
niepoprawnego tekstu jako prawidłowego pomiaru.

## Czas trwania

Konwersja wymaga jawnego `device_class: duration` i jednej z jednostek
`μs`, `ms`, `s`, `min`, `h`, `d`, `w`. Ich zapis odpowiada
[jednostkom czasu HA 2026.7.1](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/const.py#L552-L564).
Najpierw respektowana jest precyzja w jednostce HA, potem następuje rozkład.
Miesiące `m`, lata `y` i nierozpoznane jednostki pozostają na zwykłej ścieżce
liczbowej; nie zakłada się ich stałej długości. Zwykły sensor z jednostką `s`
bez klasy duration nie jest automatycznie przeliczany.

Wynik pokazuje maksymalnie dwie niezerowe części spośród dni, godzin, minut
i sekund; niższa reszta może zostać pominięta. Ułamkowe sekundy mają maksymalnie
sześć miejsc. Zachowane są znak, znormalizowane zero i lokalny separator.
Limit bezwzględny to 316 224 000 s, czyli 3660 dni; przekroczenie daje
`Out of range` / `Poza zakresem`. Wynik nadal ma najwyżej 40 znaków.

| Wejście duration | Przykładowy wynik EN |
| --- | --- |
| `90 s` | `1 min 30 s` |
| `3661 s` | `1 h 1 min` |
| `61.25 s` | `1 min 1.25 s` |
| `1.5 h` | `1 h 30 min` |
| `1500 ms` | `1.500 s` |
| `250 μs` | `250 us` |

Dla niezerowego wyniku poniżej sekundy pozostaje jednostka wejściowa,
z jednym jawnym aliasem prezentacji: greckie `μs` jest pokazywane jako ASCII
`us`, aby pasowało do istniejącego zestawu glifów. Stan i jednostka w HA nie są
zmieniane. Nie jest to ogólna transliteracja jednostek użytkownika.

## Semantyka stanów binarnych i język

Fallback dotyczy wyłącznie rzeczywistych wartości `on`/`off` encji
`binary_sensor` o rozpoznanej klasie. Znaczenia klas mają oparcie w
[zasobach binary_sensor HA 2026.7.1](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/components/binary_sensor/strings.json).

| Klasa | EN: on / off | PL: on / off |
| --- | --- | --- |
| door, window, opening, garage_door | Open / Closed | Otwarte / Zamknięte |
| motion, occupancy | Detected / Clear | Wykryto / Nie wykryto |
| presence | Present / Away | Obecność / Brak obecności |

To własne etykiety fallback produktu, nie cytat polskiego pakietu tłumaczeń HA.
Specyficzne tłumaczenie platformy/encji, a następnie klasy urządzenia wygrywa
z fallbackiem. Dopiero ogólne tłumaczenie on/off nie zastępuje rozpoznanej
semantyki kontaktu lub obecności. Kolejność wyszukiwania zasobów sprawdzono w
[`async_translate_state` HA](https://github.com/home-assistant/core/blob/2026.7.1/homeassistant/helpers/translation.py#L420-L451).
Gdy język urządzenia różni się od języka serwera, używane są istniejące
buforowane zasoby danego języka. Obsługiwane przez produkt warianty to PL/EN;
formatowanie nie przestawia globalnego locale procesu.

`unknown`, `unavailable`, brak encji i własne stany tekstowe nie są mapowane
na Closed/Clear. Klasy spoza powyższej tabeli zachowują dotychczasową ścieżkę
tłumaczeń. Wybrana przez użytkownika ikona nie jest automatycznie zastępowana.

## Pasy natywne: CLIP i pełny odczyt tekstu

Wszystkie 32 etykiety tytułu/podtytułu w 16 zarejestrowanych bindingach mają
stałą wysokość jednego wiersza i `long_mode: CLIP`. Widoczne są nadal tylko
sloty 2..15; sloty 0/1 pozostają ukryte. Prostokąty przycisków, fonty i palety
nie zmieniły się. Długie 40-znakowe tytuły oraz surowe timestampy akcji są
przycinane wizualnie, bez wielokropka; pełny tekst pozostaje zapisany w HA
i w natywnej etykiecie.

To świadomy wybór względem DOT: lokalny `lv_label.c` w gałęzi DOT nadpisuje
tekst etykiety kropkami/NUL, a `lv_label_get_text()` zwraca ten zmieniony bufor.
`material_tile_surface.cpp` używa tego gettera zarówno do porównywania nowych
wartości, jak i do `serialize_presentation`. Efektywny DOT mógłby skrócić
odczyt modelu i powtarzać aktualizację identycznego pełnego tekstu. CLIP nie
nadpisuje tekstu i nie wymaga nowego stanu C++ przechowującego jego kopię.

Metryki pochodzą z istniejących współdzielonych TTF, FreeType i wygenerowanych
konstruktorów `font::Font` v7; test sprawdza ich zgodność z konfiguracją fontów:

| Font | Wysokość wiersza |
| --- | --- |
| Roboto 16 / 18 / 20 / 24 / 30 / 34 | 19 / 21 / 23 / 28 / 35 / 40 px |
| Material Symbols 36 / 44 / 68 | 43 / 53 / 82 px |

Górne karty Controls mają ikonę w y=30..112, tytuł w y=116..144 i podtytuł
w y=151..170. Karty kompaktowe mają odpowiednio y=12..55, y=59..82 i y=85..104.
Są to współrzędne lokalne, z końcem wyłącznym; odstęp ikony od tytułu wynosi
4 px. Dolne szerokości w ośmiu kartach zwężono do wnętrza zaokrągleń.
Sensor zachowuje dużą wartość nad małym tytułem, a time/alarm odwrotną kolejność.
Zegar i pogoda pierwszej strony Home pozostają nietknięte.

`GF_Latin_Core` obejmuje sprawdzone polskie etykiety, lecz nie jest katalogiem
wszystkich symboli jednostek. Wygenerowane Roboto 16/18/34 mają po 319 glifów;
nie ma w nich `μ` U+03BC ani `µ` U+00B5. Własne etykiety PL/EN i nowy alias
duration zostały sprawdzone, ale dowolne jednostki i tłumaczenia użytkownika
mogą nadal wykraczać poza subset. Sam formatter nie pobiera fontów. Opisana
poniżej poprawka v9 uzupełnia pięć wpisów istniejących podzbiorów Material Symbols;
nie dodaje nowego bufora RAW ani zadania.

## Wyniki v8 i poprawka brakujących ikon v9

V8 zostało zbudowane, wgrane i odczytane jako pełny ELF
`ffb2ad7fc7080c23f10fd5189f643664150fd06f51b8ee4aa3e8aee58749139f`,
marker `2026-10-24 16:40:25 +0200`. Cztery raporty pod
`C:/aeh-build/feature-wave2-20261024/v8-label-{long-pl,long-en,sensors-pl,sensors-en}/report.json`
mają status `machine_checks_pass_visual_review_pending`. Obejmują długie teksty
PL/EN oraz rzeczywistą projekcję syntetycznych stanów przez formatter HA,
wstrzykniętą następnie diagnostycznym API do urządzenia. Nie była to instalacja
backendu w rzeczywistym HA.

W każdej próbie potwierdzono pełny odczyt 16 slotów, zachowanie tytułu/podtytułu,
identyczny odczyt po ponownym zastosowaniu **znormalizowanego modelu natywnego**
i zerowe maski pending przed/po tej operacji. Nie wymagano bajtowej równości
kolorów podglądu HA z paletą wyprowadzoną na urządzeniu. Próby trwały
14,61–15,64 s w budżecie 25 s, zapisały łącznie osiem oryginalnych JPEG,
miały zero tile taps/native reports, `presentation_restored:true`,
`cleanup_errors:[]` oraz `first_sticky_fault:null`. Nawigacja używała
diagnostycznego listenera; nie dowodzi fizycznego palca/GT911. Przywrócenie
modelu przez CAS nie dowodzi oczyszczenia wszystkich off-window JPEG.

Podczas oględzin root wykrył rzeczywiste prostokąty `.notdef` przy ikonach
Door/Window w kartach 68 px, m.in. w `v8-label-sensors-en/sensors-en-page4.jpg`.
To usterka katalogu glifów, odrębna od poprawności tekstowych pasów CLIP i
formatowania stanów. `ICONS` ma 15 kluczy/14 unikalnych punktów Unicode, a 16
bindingów używa wyłącznie Material Symbols 36/44/68. Każda dopuszczona ikona
może zostać przeniesiona do innego fizycznego slotu, więc katalog musi działać
w każdym z tych trzech fontów. `ignore_missing_glyphs:true` tego nie wymusza.

| Font | Uzupełnienie v9 |
| --- | --- |
| Material Symbols 36 | E8B5 (`clock`) |
| Material Symbols 44 | E8B5 (`clock`) |
| Material Symbols 68 | F1B4 (`door`), F0D3 (`presence`), E8B5 (`clock`) |

Dodano tylko te pięć wpisów, zachowując poprzednie glify i parametry fontów,
semantykę `ICONS`, hit geometry, 32 pasy CLIP, fork oraz własność pamięci/zadań.
Pięć testów katalogu sprawdza 45 par klucz/font na rzeczywistych bindings,
również ukrytych. Oryginalny subset odtwarzał dokładnie pięć braków; cached TTF
zawiera rzeczywiste glify. Wygenerowane v9 tablice mają odpowiednio 28/32/24
glify i obejmują wszystkie 15 kluczy katalogu. To dowód źródeł/codegenu,
**jeszcze nie odbiór tych ikon na urządzeniu**.

V9 jest zbudowane i zachowane w
`D:/aeh-build/feature-research-20261024/native-context-v9`. Root następnie
potwierdził OTA exit 0 i odczyt zgodnego pełnego running ELF. Zachowany i
potwierdzony na urządzeniu pełny ELF to
`57d7b3d8fc2a716e1e951d7823eb30c3a3c60790cf7a91546d552d0f2a8325bb`,
OTA `e5636a519189fc6c85bf5cd7c330ffa05c2e40ce9faa9be5722e3e8ed5a39c2a`,
marker `2026-10-24 17:10:05 +0200`. Manifest źródeł
`source-manifest-v9.json` ma SHA256
`8d0de854e1891b3e732a57439913ae321a8bb3c1b7e57568c098ff86dbe6df6f`,
a manifest artefaktów SHA256
`d7ab9f1ef97e9b9033d567978dbcc71e28e6ed83775221a2e243284d611037f3`.
Jedyna delta native względem zachowanego v8 to `modules/lvgl/fonts.yaml`;
produkt zachowuje 139 ścieżek runtime, fork 5409. Odbiór compiler inputs
potwierdza niezmieniony sdkconfig, znormalizowane zależności i brak aktywnych
starych ścieżek builda. Odbiór compiler inputs i późniejsze potwierdzenie
running identity są oddzielne; bieżąca ocena wizualna i pomiary v9 nadal trwają.

## Ograniczony wynik pomiarów v8

Raporty `v8-weather-memory-review-post-clean-weather.md/.json` pod katalogiem
wave2 odnoszą się do osobnego przebiegu `v8-weather-post-clean-boot`.
Największy wolny blok PSRAM wynosił w trzech fazach 4032 KiB, jak w bazie v7.
Po sunny różnica wolnej PSRAM/internal wynosiła 0/0 KiB, po cloudy −3/+1 KiB.
Stan początkowy pozostaje nieporównywalny: wolna PSRAM była niższa o 720 KiB,
mimo tego samego największego bloku. Nie uzasadnia to globalnego braku regresji RAM.

Rendered-animation counters dały sunny 49,7468→50,1650 FPS i cloudy
26,2692→26,2224 FPS względem v7; to suma klatek/suma czasu urządzenia,
nie fizyczne FPS panelu ani dowód istotnego przyspieszenia. Mediana sunny
handler-wall na sekundę obserwowaną przez host wzrosła około 9%
(12679,7→13818,5 µs/s), a większe wartości odstające pozostają w danych.
Root odnotował nakładanie zbierania kandydata z kompilacją v9 na hoście;
to potencjalne zakłócenie, nie wykazana przyczyna różnic. Raport nie nadaje
globalnego PASS wydajności/pamięci. W tym osobnym przebiegu listy strict/raw
faults były puste.

Wcześniejsze warm obserwacje oraz nieudane próby one-boot/read-only continuation
pozostają zachowane z pierwotnym wynikiem. Późniejszy przebieg pogodowy nie
zmienia ich na sukces ani nie zastępuje odbioru v9 przy bezczynnym host SDK.

## Dowody host i zamrożone źródła

Pierwotny przebieg formatowania i pasów wykonano po ich zamrożeniu:

```powershell
python -m unittest tools.tests.test_ha_layout tools.tests.test_ha_formatting tools.tests.test_native_tile_geometry -q
```

Historyczny wynik: **147/147 PASS**, bez pominiętych testów na tej maszynie. W tym 28 testów
formatowania i adapterów korzysta z atrap HA, a 7 testów geometrii sprawdza
prostokąty, rozdzielenie pasów, krzywizny kart oraz dostępne lokalne metryki
fontów. Opcjonalna część FreeType/cache może być pominięta na innej maszynie;
kontrole strukturalne geometrii działają niezależnie. To nie render LVGL.
Przechodzą także Ruff, kontrola whitespace i niezależny test wrogiego kontekstu
Decimal z włączonymi wszystkimi pułapkami. Następnie root potwierdził
**167/167 PASS** po dodaniu odrębnych 15 testów stateless i 5 testów katalogu ikon
oraz uporządkowaniu importów; Ruff default również PASS. Nie należy dodawać
do tej liczby wcześniejszego wyniku Node 61/61.

Lokalny pakiet v4 `0.4.0.dev2` zawiera 18 plików, w tym formatter i odrębny
przyrost stateless. ZIP
`C:/aeh-build/feature-wave2-20261024/ha-integration-package-v4/atmosfera_echo_hub-0.4.0.dev2.zip`
ma SHA256 `91474ca82ed8371f8f30d89822f8c26692cf80f90d9dddb27bdde56639ab5921`;
manifest potwierdza CRC i identyczny deterministyczny rebuild. Pakiet nie został
zainstalowany. Dostęp do HA został już przekazany; odbiór instalacji, restartu,
logów i rzeczywistych usług/stanów pozostaje PENDING. Syntetyczne projekcje
wyświetlone na v8 nie zastępują tej bramki.

Lokalne raporty dowodowe pozostają poza Git:
`C:/aeh-build/feature-wave2-20261024/formatting-independent-review.md`,
`formatting-independent-review-evidence.json` w tym samym katalogu oraz
`C:/aeh-build/feature-research-20261024/native-tile-text-bands-review/handoff.md`.

Pierwotne hashe formatowania pozostają w zachowanych raportach niezależnego
review. Poniższa tabela identyfikuje aktualne źródła po przyjęciu stateless,
poprawce fontów i późniejszym porządkowaniu importów; nie przypisuje tych
nowszych hashy historycznemu przebiegowi 147 testów.

| Plik | Aktualny SHA256 |
| --- | --- |
| `custom_components/atmosfera_echo_hub/formatting.py` | `f71c96a92a0d7283b2274ee002b9303cec03b18372d794879ccaad61f44b6517` |
| `custom_components/atmosfera_echo_hub/cards.py` | `3a2b265f4152afa7de7ab50dc65483a792ef8a44a8fcfb79c7f0e2b7f38278de` |
| `modules/lvgl/fonts.yaml` | `c4de8a815786a7360f950d207c020cfe75a27438b4f6a13798b0eb321bce0747` |
| `modules/lvgl/pages/tiles_m3.yaml` | `6cda62666390bea82765124991e9c64796e2a98f6baf67af0f20c71b669203be` |
| `tools/tests/test_ha_formatting.py` | `979a5d808da344589bfae2a335a33fc0d8ecf9da3a79c265fefb724c64a045ac` |
| `tools/tests/test_ha_stateless.py` | `5df40090191a05d398e72f4f620f468c9f5b3742f0daab8bdbad917ab4e5cca4` |
| `tools/tests/test_tile_icon_catalog.py` | `3dfffaf256717c04a5546cd7071a2de3e85f50da0502fa7fdcddcfcb3c72f306` |
| `tools/tests/test_ha_layout.py` | `888c517e27dc343230b5de853e5478c5b094cd9b0e4ca567bee080e4b4fd10bf` |
| `tools/tests/test_native_tile_geometry.py` | `776b492d34de7042c5cf9c5cebeb555315e5da094f70f57cf14bd175fcfd518b` |

## Pola dowodów do odbioru przez root

Poniższe pola są propozycją kompletnego zapisu maszynowego, a nie wynikami
oczekujących prób. `null` oznacza brak pomiaru; nie należy zastępować go zerem.

| Grupa | Minimalne pola |
| --- | --- |
| Tożsamość źródeł | `source_manifest_path`, `source_manifest_sha256`, `runtime_hashes_before`, `runtime_hashes_after`, `unexpected_source_changes` |
| Konfiguracja/build | `config_status`, `config_log_path`, `build_status`, `build_exit_code`, `build_log_path`, `esphome_version`, `idf_version`, `elf_sha256`, `app_sha256`, `build_marker` |
| Flash/start | `flash_status`, `device_mac`, `reported_elf_sha256`, `reported_build_marker`, `uptime_after_boot`, `first_sticky_fault`, `recovery_count` |
| Model i aktualizacja | `injection_kind` (HA/native API), `input_payload_sha256`, `readback_sha256`, `full_title_match`, `full_subtitle_match`, `same_payload_dirty_before_after`, `accepted_revision`, `pending_slots`, `snapshot_ready` |
| Obrazy/ocena | `capture_complete`, `original_image_paths`, `original_image_sha256`, `reviewer`, `slots_reviewed`, `pl_en_40char_cases`, `raw_timestamp_case`, `overlap_or_missing_glyphs`, `visual_status` |
| Nawigacja | `home_pages_tested`, `hidden_cards_tested`, `swipe_cancel_tested`, `repeated_reveal_status`, `touch_evidence_kind` (diagnostyczne/fizyczne) |
| Para wydajności | `baseline_artifact`, `candidate_artifact`, `present_counter_delta`, `elapsed_seconds`, `present_fps`, `loop_time`, `internal_free`, `internal_largest`, `psram_free`, `psram_largest`, `home_raw_slots`, `home_raw_bytes`, `dsi_fault_counters` |
| Przywrócenie | `original_presentation_restored`, `preferences_restored`, `cleanup_errors`, `final_sticky_fault`, `final_home_page`, `final_cache_window` |

Raport ma osobno podać wynik host, kompilacji, flash/hash, obrazu, wydajności
i rzeczywistego HA. Wstrzyknięcie prezentacji przez diagnostyczne API nie dowodzi
wykonania usługi HA, działania aktuatora ani fizycznego dotyku GT911. Wcześniejsze
udane obrazy i pomiary v7 pozostają bazą porównania, nie odbiorem v9. Root dopisze
kolejne wyniki sprzętowe v9 dopiero po ich faktycznym uzyskaniu.
