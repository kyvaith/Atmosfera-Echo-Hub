# Optymalizacje po analizie TouchDeck — 30 października 2026

**Wynik końcowy: native30 wgrany i sprawdzony na urządzeniu.** W porównaniu
przy działającym HA przewijanie Ustawień wzrosło z 30 do 53–54 FPS, a średni
czas klatki spadł z 32,97 do 16,32 ms (około 50,5%). Dodatkowe 1219200 bajtów
snapshotu istnieje tylko podczas otwartych Ustawień. Po ich zamknięciu nie
zostaje dodatkowy surowy bufor. W rzeczywistym scenariuszu fragmentacji po
Galerii/kamerze działa także 14-segmentowy fallback: 46 FPS, 0 nieudanych
klatek. Szczegółowy odbiór i ograniczenia są w sekcji końcowej.

**Otwarty błąd niezależny od tej zmiany:** po sekwencji media→Home2→Ustawienia
→Home2→Home1 część statycznego Home1 nie pojawia się na pierwszym zrzucie.
Odtworzono to również po rzeczywistym przywróceniu zachowanego native26.
Nie deklarujemy naprawy tego błędu ani pełnego odbioru wszystkich tras Home.

Zakres: wydajność istniejącego UI. Przenoszenie nowych funkcji pozostaje
wstrzymane. Bez commitów, push ani wdrażania integracji HA. Kandydaci nowych
funkcji są dopisani do istniejącego roadmapu; nie zostali zaimplementowani.

## Decyzje na podstawie porównania

TouchDeck również zatrzymuje LVGL i przesuwa snapshoty. Jego obraz RGB565
320×480 zawiera 6,25 raza mniej bajtów niż nasz RGB888 800×800; nie jest to
pomiar różnicy szybkości. Atmosfera ma już asynchroniczny compositor Home,
ograniczoną pulę snapshotów i porównywanie wartości przed zmianą kafelków.
Nie przypisujemy tych istniejących mechanizmów nowej poprawce.

Pierwsze próby objęły pomijanie identycznych pozycji przewijania i ponowne
używanie raz zsynchronizowanego, niezmiennego źródła DMA. Eksperyment cache
nie wykazał zysku FPS i **został wycofany ze źródeł końcowego kandydata**;
jego oryginalne źródła i testy są zachowane w katalogu dowodów. Pozostaje
pomijanie identycznych pozycji z obowiązkową ostatnią klatką.

Profil native28 wskazał acquire=25 µs, compose=31922 µs, present=890 µs.
Etap compose obejmuje PPA i obsługę jego cache, więc ten pomiar nie izoluje
samej arytmetyki konwersji. Następny kandydat, native29, dopasowuje format
przewijanej listy do RGB888 wyświetlacza i wykorzystuje istniejące kopiowanie
DMA2D, zamiast rozszerzać RGB565 w każdej klatce. To odpowiednik zasady
TouchDeck: zachować natywny format transportu. Native29 nie został wgrany;
przyjętym wariantem jest native30 z poprawką pierwszej rezerwacji.

Nie przenosimy sterownika SPI/QSPI, czasów TE ani wcześniejszego potwierdzania
LVGL flush. Tam bufor pośredni oddziela LVGL od transportu, podczas gdy u nas
bufory LVGL są skanowanymi buforami DSI. Usunięcie oczekiwania mogłoby pozwolić
LVGL pisać do aktywnego obrazu. Buforów, zadań, trybu DIRECT, renderowania PPA
i synchronizacji docelowego framebufferu nie zmieniono.

## Własność pierwszego eksperymentu cache — wycofany

Główny wątek LVGL tworzy i odświeża RGB565 snapshot Ustawień. Przed zapisem
odświeżenie zatrzymuje i opróżnia worker przewijania. Segment otrzymuje flagę
gotowości do odczytu DMA dopiero po udanym C2M. Worker pożycza jego dokładny
zakres istniejącemu hookowi cache tylko na czas blokującego PPA SRM; po powrocie
cofa pożyczkę, także przy błędzie PPA. Osobny zakres nie nadpisuje znaczników
innych presenterów. Przy nieudanym C2M pozostaje dotychczasowa synchronizacja
SDK przed klatką. M2C docelowego bufora jest zachowane.

Odświeżenie unieważnia gotowość segmentów przed ich modyfikacją. Częściowo
nieudany snapshot jest odrzucany, a timeout opróżniania zachowuje źródła.
Zamknięcie Ustawień oddaje pamięć po zakończeniu workera. Pomijanie tej samej
pozycji całkowitej nie zmienia czasu easing ani obowiązku wysłania ostatniej
klatki. Nie dolicza pominiętych klatek do FPS.

## Walidacja źródeł pierwszego kandydata i obraz porównawczy

Katalog dowodów: `C:\aeh-build\touchdeck-performance-20261030`.
Kandydat jest zamrożonym native26 z czterema zmienionymi plikami runtime
komponentu LVGL; YAML produktu jest taki sam jak dla native26. To świadomie
nie wdraża wszystkich innych niezakończonych prac z brudnych checkoutów.
Nowy nagłówek to `immutable_dma_source.h`; pozostałe pliki to
`lvgl_esphome.cpp`, `lvgl_esphome.h` i `scroll_snapshot_geometry.h`.

- 22 testy komponentowe: PASS, w tym wykonywany hostowy C++, granice i overflow
  zakresu DMA, nieudany commit, wycofanie zakresu, współbieżny odczyt przy
  100000 publikacji, geometria segmentów i pomijanie duplikatów.
- Ruff F/E9 zmienionych testów: PASS.
- Konfiguracja i generacja pełnego firmware ESP-IDF: PASS.
- Pierwsza walidacja konfiguracji wykazała brak lokalnego `secrets.yaml`
  w kopii publicznych źródeł. Do prywatnego katalogu build skopiowano istniejący
  plik native26; jego hash włączono do `source-v27-build.json`. Nie zmieniano
  danych logowania ani plików sekretów w repozytoriach.
- Pełna kompilacja natywna ESP-IDF 5.5.6: PASS, `compile-process.json`,
  09:46:16–09:54:37 UTC. Wygenerowana kopia zmienionych źródeł została
  porównana hashami z zamrożonym wejściem. Wyniki OTA i odbioru tego kandydata
  opisano niżej; native27 nie jest wersją końcową.

Nowy obraz native27: marker `2026-10-30 10:46:10 +0100`, pełny ELF
`7c41c9935a231be37f75720f961cfd5dd0b7a906b4537f91031fd508966bec1b`.
Manifest źródeł `source-v27-build.json` ma SHA
`0d76b96a25cc6286bda1fbfa63a60f92899b26170e0b967540d27372d375d40c`.
Manifest zachowanych artefaktów `native-context-v27/manifest.json` ma SHA
`92cfe86e2f726589cebabb0e1cb3d2015e7039bbadf4e0fcf22138f0f514c694`.
Poprzednie artefakty native26 są zachowane niezależnie w
`C:\aeh-build\feature-wave2-20261024\native-context-v26`.

## Bazowy native26 na urządzeniu

MAC `30:ED:A0:E2:0B:CD`, pełny ELF
`f69bb7698034f29127d984358d10f759d1b0a79cd7cd6bbd9aed81ae5698719a`.
System Logs ON, Performance Logs OFF, Swipe Debug Logs OFF, Voice Assistant
Mute OFF, Voice Assistant Timing Logs ON. Benchmark chwilowo włącza własną
diagnostykę i ją przywraca; nie zapisuje preferencji. HA pod ostatnim adresem
nie odpowiada, więc nie jest to test dostarczania świeżych danych z HA.

| Przebieg | Klatki | FPS źródła | Średnia klatka | Maksimum | Nieudane | Segmenty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-scroll-v1 | 46 | 29 | 33276 µs | 40002 µs | 0 | 1 |
| baseline-scroll-v2 | 47 | 30 | 32701 µs | 40287 µs | 0 | 1 |

Po obu zamknięciach app_work/scroll/close=0, trzy sloty Home obecne (5625 KiB).
W drugim przebiegu po zamknięciu wolne PSRAM 4889 KiB, internal 32 KiB;
rozmiary wolnych bloków i kompresowanych JPEG zależą także od rozgrzania UI.
To pomiar źródłowych klatek compositora, nie niezależny pomiar klatek panelu.

## Istniejący błąd wykryty podczas rozszerzonej kontroli

`baseline-suite-v1` potwierdził starą wersję pełnym ELF i wykonał łańcuch Home,
Player, zamknięcie, asystenta i zamknięcie. API przeszło bez restartu, ale ocena
oryginalnych screenshotów **nie przeszła**: przycisk Playera 244×244 pozostał
w widoku asystenta i częściowo na Home. Log zachował slot overlay 278,278
również po zamknięciu. To dowód błędu istniejącego przed nową zmianą, a nie
dowód poprawności całego UI. Dodatkowo Home po bazowym przewijaniu Ustawień
utracił widoczną grafikę pogody. Nie traktować odpowiedzi API ani braku
underrun jako potwierdzenia poprawnego obrazu. Wyniki po aktualizacji wymagają
osobnego przeglądu.

## Pierwszy kandydat native27 — wynik bez potwierdzonego przyspieszenia

OTA zakończone 09:56:17 UTC, jedna próba. Każdy poniższy przebieg potwierdził
MAC, marker i pełny ELF nowego obrazu, nie tylko odpowiedź hosta na ping.

| Przebieg | Klatki | FPS źródła | Średnia klatka | Maksimum | Nieudane |
| --- | ---: | ---: | ---: | ---: | ---: |
| candidate-scroll-v1 | 45 | 28 | 32764 µs | 40262 µs | 0 |
| candidate-scroll-v2 | 45 | 29 | 33014 µs | 40011 µs | 0 |

Nie wykazano przyspieszenia względem native26. Mniej oddanych klatek jest
zgodne z pomijaniem duplikatów, ale samo w sobie nie dowodzi oszczędności CPU.
Po zamknięciu app_work/scroll/close=0 i trzy sloty Home; pierwszy przebieg ma
4887 KiB wolnego PSRAM, 33 KiB internal. Oryginalny obraz przewiniętej listy
oraz Home po drugim przebiegu obejrzano: czytelne napisy, grafika pogody
widoczna, bez korupcji ze starego Playera.

`candidate-refresh-v1` nie jest wynikiem benchmarku: zmiana języka zamknęła
Ustawienia według dotychczasowej polityki produktu. Język polski przywrócono,
ale kolejny benchmark nie wystartował. Helper poprawiono, zachowując ten
nieudany przebieg. `candidate-refresh-v2` używał przełącznika samego dźwięku
wybudzenia, bez uruchamiania asystenta. Dwa obejrzane oryginały pokazują
OFF→ON→OFF w tym samym miejscu listy; mikrofon i inne preferencje zachowano.
Po zamknięciu zarejestrowano **jeden DSI underrun**; brak restartu nie zmienia
wyniku tej próby na PASS. Średniego FPS tego scenariusza nie porównujemy,
ponieważ okres licznika obejmuje też postój i odświeżanie listy.

`candidate-suite-v1` zatrzymano przed testem: zastano asystenta, nie Home.
`candidate-suite-v2` jawnie przygotował Home zwykłym wybudzeniem/zamknięciem,
przeszedł łańcuch karuzeli, Player i widok asystenta, po czym wrócił na Home1.
API bez awarii; obejrzane oryginały asystenta i Home są poprawne. Stary artefakt
Playera nie powtórzył się w tej konkretnej próbie; nie przypisujemy jego
usunięcia optymalizacji przewijania.

O 10:08 UTC ponownie sprawdzono HA: porty 8123 i22 na 192.168.88.3 odpowiadają.
Pomiary z wcześniejszego okresu offline i późniejszego online nie są ścisłym
porównaniem przy identycznym obciążeniu. Dla wyjaśnienia czasu klatki powstał
native28 z pomiarami acquire/compose/present, aktywnymi tylko z istniejącym
wyłączonym domyślnie logowaniem swipe.

## Następny kierunek: format natywny i pierwsza rezerwacja

Native28 wgrano 10:10:17 UTC; jego pełny ELF to
`e0bba898428bd00a6ce907426ed9d35a8c18974ec33535460c9d087787967726`.
`profile-scroll-v1` potwierdza 31 profilowanych klatek: acquire=25 µs,
compose=31922 µs, present=890 µs. Cały benchmark: 45 klatek, 28 FPS,
32758 µs średnio, 40055 µs maksimum, 0 nieudanych.

Następnie przywrócono zachowany native26, potwierdzając jego pełny ELF.
Nowe dwa pomiary z HA online i tymi samymi siedmioma preferencjami:

| Przebieg | FPS | Średnia | Maksimum | Wolne PSRAM w Ustawieniach | Segmenty |
| --- | ---: | ---: | ---: | ---: | ---: |
| online-baseline-scroll-v1 | 30 | 32972 µs | 39958 µs | 8836 KiB | 1 |
| online-baseline-scroll-v2 | 30 | 32970 µs | 40267 µs | 8844 KiB | 1 |

Oba mają 46 klatek i 0 nieudanych. Drugi kończy z wolnym PSRAM 4902 KiB,
internal 33 KiB; app_work/scroll/close=0. Dodatkowy
`online-baseline-refresh-v1` (kontrolerowy drag, OFF→ON→OFF dźwięku wybudzenia,
przewijanie i zamknięcie) również przeszedł bez nowego underrun i restartu.

Native29 przeszedł konfigurację i pełną kompilację, ale **nie został wgrany**.
Przegląd wykazał, że pożyczka Galerii jest liczona przed pierwszym configure
kontrolera i mogłaby nadal mieć rozmiar RGB565. Nie akceptujemy równoczesnego
zatrzymania tej za małej pożyczki oraz nowej powierzchni RGB888.

Native30 dodaje odczyt `get_required_bytes()` z formatu własnego kontrolera
i używa go w istniejącej polityce pożyczki. Legacy C helper zachowuje domyślny
RGB565 i przyjmuje jawny format. Źródła końcowego kandydata nie zawierają
eksperymentu pomijania cache. Pozostają pomijanie identycznych pozycji,
format natywny oraz wyłączona domyślnie diagnostyka acquire/compose/present.
Produkt zmienia wyłącznie `modules/lvgl/base.yaml`; pozostałe publiczne wejścia
produktu są zamrożone z native26. Prywatny plik sekretów jest tą samą lokalną
kopią co w native26, bez zmiany wartości.

Manifest źródeł native30: `source-v30-reviewed-build.json`, SHA
`872e9681121f4de9938f68fa400e899ccf963a2b07d7caa00c00f867a36fac3c`.
Konfiguracja: PASS. Testy: **29 PASS**, `native-format-tests-v5.log`, w tym
725 pozycji RGB888/1524 px, granice podziałów, błędy alokacji każdego z 14
segmentów, oddanie cudzej pożyczki i zachowanie domyślnego RGB565. W wariancie
RGB888 źródło 800×1524 wymaga 3657600 bajtów zamiast 2438400; limit 8MB oznacza
8000000 bajtów według walidatora ESPHome. Pełna kompilacja i odbiór native30
zakończyły się wynikami opisanymi poniżej.

## Odbiór końcowego native30

- Konfiguracja i 29 testów komponentowych: **PASS**.
- Pełna kompilacja ESP-IDF 5.5.6: **PASS**, 10:28:05–10:36:34 UTC;
  `compile-v30-process.json` i `compile-v30.log`.
- OTA: **PASS**, jedna próba, zakończona 10:37:59 UTC;
  `upload-v30-process.json`. Native29 nie był flashowany.
- Tożsamość po OTA: MAC `30:ED:A0:E2:0B:CD`, marker
  `2026-10-30 11:28:27 +0100`, pełny ELF
  `9811a3c63d91d73de1f1bb52713e93ed5661c28a01e4c397c3b8d5b7ce86520f`.
  Każdy scenariusz sprawdzał marker i pełny ELF przed sterowaniem UI.
- Artefakty: `native-context-v30/manifest.json`, SHA
  `a74104da7b78b282b5779f4036175dd1048c5f778481bd6a7a034ca31e210067`.
  OTA SHA `988f8bc9e84e39c70cb0b590ce139e4c52069dd895fb66d8339e7bc97c6a7bdc`.
- Przegląd oryginalnych screenshotów Ustawień, odświeżenia, 14 segmentów,
  Playera/asystenta, Galerii i kamery: **PASS**. Odbiór powrotu Home2→1 po
  mediach: **FAIL w obu wersjach**, osobno opisany niżej. Nie wnioskujemy
  poprawności obrazu z samego PASS API.

### Porównanie przy takim samym obciążeniu bazowym

HA online, Home1, język polski, akcent AEE2FF, mikrofon niewyciszony.
Logi systemowe i Voice Timing ON, Performance/Swipe OFF, Wake Sound OFF.
W obu wersjach użyto tego samego istniejącego benchmarku. Zrzuty wykonywano
przed i po ruchu, nie w oknie pomiaru.

| Wersja / przebieg | Klatki | FPS źródła | Średnia | Maksimum | Nieudane |
| --- | ---: | ---: | ---: | ---: | ---: |
| native26 online v1 | 46 | 30 | 32972 µs | 39958 µs | 0 |
| native26 online v2 | 46 | 30 | 32970 µs | 40267 µs | 0 |
| native30 v1, pierwsze otwarcie | 80 | 54 | 16404 µs | 24196 µs | 0 |
| native30 v2 | 79 | 53 | 16241 µs | 23814 µs | 0 |

Średnia z dwóch średnich: 32971→16322,5 µs, spadek **50,49%**.
To FPS compositora i czas całej klatki źródłowej, nie niezależny pomiar FPS
matrycy ani koszt samego LVGL. `comparison-native30.json` zawiera hashe
raportów wejściowych. Profil native30 v1: acquire=1076 µs, compose=14766 µs,
present=661 µs. Maksimum w tych próbach spadło z około 40 do około 24 ms;
nie podajemy percentyli na podstawie samych podsumowań.

### Pamięć i własność

Pierwsza pożyczka po restarcie: `pool=YES attached=YES bytes=3657600
required=3657600`. Nie ma równoczesnej za małej pożyczki RGB565 i drugiej
pełnej powierzchni. Otwarte Ustawienia: wolne PSRAM 7642/7648 KiB wobec
8836/8844 KiB w native26. Po zamknięciu: 4903/4901 KiB wobec około 4902 KiB
w wersji bazowej; internal 33 KiB w obu. `app_work=0 scroll=0 close=0`,
trzy raw sloty Home (5625 KiB) zachowane.

Wątek LVGL nadal tworzy/odświeża źródło po opróżnieniu workera. Worker
kopiuje RGB888 przez istniejący DMA2D do wolnego bufora DSI; PPA pozostaje
zgodnym fallbackiem i ścieżką RGB565. Nie pomijamy wymaganej synchronizacji
cache celu ani źródła. Nie zmieniono puli trzech buforów, dwóch buforów
LVGL DIRECT, zegara, zadań, audio ani przekazania końcowej klatki do LVGL.

Po otwarciu Galerii i kamery rosną ich istniejące **kompresowane** preview JPEG.
Nie jest to wyciek nowego scroll snapshotu: przed tym testem wolne PSRAM po
aplikacjach wynosiło 4638 KiB (native26: 4636 KiB), po mediach 3331 KiB,
po kolejnym zamknięciu Ustawień i powrocie na Home1 około3,3 MiB.
Zwolnienie raw scroll/app work/close jest w każdym z tych stanów osobno
potwierdzone. Nie porównujemy tych różnych stanów rozgrzania jako regresji.

### Rzeczywista fragmentacja i pozostałe scenariusze

- `native30-refresh-v1`: kontrolerowy drag, odświeżenie widocznej listy
  OFF→ON→OFF dźwięku wybudzenia, dalsze przewijanie i zamknięcie. Oryginały
  potwierdzają nową i przywróconą wartość, bez starych pikseli.
- `native30-suite-v1`: łańcuch Home1→2→3, Home4→1, Player i asystent,
  normalne zamknięcia i Home1. Obejrzane oryginały czytelne, bez pozostałości
  przycisku Playera i bez utraty grafiki pogody. Pamięć po scenariuszu:
  4638 KiB PSRAM /28 KiB internal, wobec 4636/28 KiB w identycznym bazowym
  `online-baseline-suite-v1`. Stary sporadyczny artefakt nie wystąpił również
  w tej nowej próbie native26; nie uznajemy go za naprawiony tą zmianą.
- `native30-media-v1`: rzeczywiste zdjęcie z Galerii, 80 zaprezentowanych
  klatek ruchu /38,7 FPS w odczycie; kamera streaming: received 53, decoded 52,
  **presented 51 /8,2 present FPS**, jeden odrzucony frame, queue/stale_drop=0.
  Zdjęcie i obraz kamery obejrzano w oryginalnych screenshotach. Zamknięcia
  przywróciły Home, camera=0 i żaden raw scroll/app work nie pozostał.
  To test poprawności/lifecycle, nie porównanie wydajności tych aplikacji z 26.
- `native30-warm-page2-v1`: po mediach, otwarcie Ustawień z Home2. Największy
  blok miał 2880 KiB, więc pożyczka 3657600 bajtów została prawidłowo odmówiona.
  Kontroler użył 14 segmentów: **69 klatek, 46 FPS, 19417 µs średnio,
  28568 µs maksimum,0 nieudanych**. Obejrzany oryginał listy nie ma pasków,
  brakujących wierszy ani uszkodzonych napisów. Powrót zachował Home2,
  a 14 segmentów zostało zwolnionych. Tego wyniku nie mieszamy z A/B Home1.
- `native30-final-home-v1`: wcześniejsza negatywna ocena podglądu została
  wycofana po ponownym odczycie pikseli oryginału. Plik zawiera kompletny Home.
  Szczegóły korekty i osobnej poprawki kontraktu buforów są w
  [raporcie Home](home-screen-fix-2026-10-30.md).

W wymienionych końcowych przebiegach native30: brak nieoczekiwanych rozłączeń,
restartów i nowych komunikatów DSI underrun; benchmarkowe `unsafe=0/0/0`,
DMA invalid/event/first_fatal=0. Pojedynczy underrun z wycofanego native27
pozostaje zapisany jako nieudana wcześniejsza próba, nie jako wynik native30.

### Granice odbioru i dalsza praca

Nie testowano ciągłego rzeczywistego audio Sendspin ani pięciu fizycznych
odłączeń zasilania; ta zmiana nie modyfikuje audio ani boot ownership.
Kontrolerowy replay nie emuluje transportu GT911 i nie jest ręcznym testem
każdego gestu. Testy nie dowodzą bezbłędności wszystkich innych ekranów.
Status przed kontrolnym przywróceniem bazowej wersji: rewizja 16,
pending_context_slots=0, pending_slots=49152, snapshot_ready=false.
Nie deklarujemy pełnego odświeżenia wszystkich off-window JPEG.

Surowe źródła, logi, oryginalne JPEG, manifesty i rollback 26 pozostają lokalnie.
`runtime-v30.patch` obejmuje wyłącznie siedem publicznych plików runtime
względem zamrożonego native26; nie zawiera sekretów. Git HEAD obu repozytoriów
pozostał bez zmiany. **Bez commitów i push.** Migracja nowych funkcji nadal
wstrzymana, pięć kandydatów TD-01…05 pozostaje tylko na roadmapie.

## NAV-HOME-20261030: korekta rozpoznania i osobna poprawka buforów

**Wcześniejsza kwalifikacja trzech obrazów jako niekompletnego Home jest
wycofana.** Ocena na podstawie podglądów była błędna. Ponowne odczytanie
tych samych plików przez Pillow oraz bezstratny podgląd PNG potwierdzają obecność
chipu pogody, mikrofonu, statusu i wskaźników. Nie zmieniano zawartości obrazu.
`original-jpeg-audit.json` w `C:\aeh-build\home-screen-fix-20261030` zapisuje
cztery zgodne kontrole obszarów, w tym świeży przebieg native30 po restarcie.

Kontrolne wgranie native26 i sekwencje Galeria→Kamera→Home2→Ustawienia→Home1
rzeczywiście wykonano, ale nie dowodzą odtworzenia usterki ekranu. Obrazy
`native30-real-input-roundtrip-v1`, `native26-regression-roundtrip-v1` i
`native30-final-home-v1` zawierają kompletne elementy. Nie należy już cytować
ich jako negatywnej wizualnej kontroli regresji. Pomiary przewijania pozostają
ważne: native26 w tej próbie miał30 FPS /32998 µs i0 nieudanych.

Przegląd kodu wykazał niezależną niezgodność: zakończenie swipe uznawało
wyrównanie wskaźnika za synchronizację całej bazy w trybie DIRECT. Poprawka
native31 używa istniejącego spójnego handoff również po przejściu aplikacji.
Zakres, testy i aktualny wynik sprzętowy są w
[raporcie naprawy Home](home-screen-fix-2026-10-30.md). Nie przypisujemy temu
naruszeniu kontraktu przyczyny dawnych mylnych podglądów JPEG.

Po kontroli porównawczej przywrócono ten sam obraz native30, OTA zakończone
**11:03:37 UTC** (`upload-v30-final-restore-process.json`).
`native30-final-restored-v3` potwierdza pełny ELF podany powyżej, osiem zachowanych
preferencji i Home1. Oryginał obejrzano: kompletny chip pogody, mikrofon,
status, wskaźniki i grafika pogody. Wolne PSRAM 4891 KiB, internal 34 KiB,
raw scroll/app work/close=0. Zimny status po tym restarcie: rewizja 16,
pending_slots=65532, pending_context_slots=65532, snapshot_ready=false;
nie traktujemy go jako pełnego odbioru wszystkich kart HA.

Historyczny `final-verification.json` pozostaje niezmieniony. Jego klasyfikacja
17 poprawnych /3 niekompletnych podglądów jest zastąpiona powyższą korektą.
Zgodność siedmiu publicznych plików runtime z buildem, Git HEAD, hashe testów
i końcowa tożsamość są odrębnymi dowodami i nie zostały unieważnione.

Wybrane oryginalne screenshoty 800×800:

- [Ustawienia po przewinięciu](C:/aeh-build/touchdeck-performance-20261030/native30-scroll-v1/settings-after-original.jpg).
- [Ustawienia przy 14 segmentach](C:/aeh-build/touchdeck-performance-20261030/native30-warm-page2-v1/settings-after-original.jpg).
- [Player](C:/aeh-build/touchdeck-performance-20261030/native30-suite-v1/player-original.jpg).
- [Końcowy Home po przywróceniu native30](C:/aeh-build/touchdeck-performance-20261030/native30-final-restored-v3/home-original.jpg).
- Oryginały z wycofanej negatywnej oceny: [native26](C:/aeh-build/touchdeck-performance-20261030/native26-regression-roundtrip-v1/home-real-input-after-original.jpg)
  i [native30](C:/aeh-build/touchdeck-performance-20261030/native30-real-input-roundtrip-v1/home-real-input-after-original.jpg).
