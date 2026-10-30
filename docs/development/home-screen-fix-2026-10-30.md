# Spójność Home po przejściach — 30 października 2026

Zakres: poprawka przekazania obrazu do natywnego LVGL, pełna kompilacja,
wgranie i testy urządzenia. Migracja nowych funkcji pozostaje wstrzymana.
Bez commitów i push. Katalog dowodów:
`C:\aeh-build\home-screen-fix-20261030`.

## Korekta wcześniejszego rozpoznania

Wcześniejszy przegląd podglądów JPEG błędnie zakwalifikował trzy obrazy jako
niekompletny Home. Ponowny odczyt **tych samych oryginalnych plików** przez
Pillow wykazuje obecność chipu pogody, mikrofonu, ikon statusu i wskaźników
stron. Bezstratne zapisanie odczytanych pikseli do PNG daje kompletny obraz.
Nie zmieniano ani nie domalowywano elementów. Również nowa kontrola native30
po restarcie i sekwencji Galeria→Kamera→Home2→Ustawienia→Home1 jest kompletna.

`original-jpeg-audit.json` obejmuje trzy dawne obrazy oznaczone negatywnie
oraz nową kontrolę po restarcie. W każdym z czterech obszarów obecne są
odpowiednio 25999, 6273, 559 i 932 jasne piksele. To korekta interpretacji,
nie nowy dowód odtworzenia awarii urządzenia. Historyczne pliki, logi i
`final-verification.json` pozostają niezmienione, lecz ich trzy negatywne
oceny wizualne są wycofane. Nie przypisujemy im już statusu potwierdzonej
usterki firmware ani regresji native26/native30.

## Rzeczywista niezgodność w kodzie

W `snapshot_swipe_finish_now()` sukces `realign(false)` był traktowany jako
potwierdzenie synchronizacji obrazu i pozwalał odrzucić oczekujące odświeżenia.
Ta operacja wyrównuje wskaźnik, ale nie kopiuje spójnej bazy do buforów.
LVGL pracuje w DIRECT również przy ustawionym `full_refresh: true`, więc
następne odświeżenie zegara nie musi odmalować statycznych kontrolek.
To naruszenie udokumentowanego kontraktu, niezależnie od błędnej oceny JPEG.
Nie ma podstaw do twierdzenia, że właśnie ono wywołało dawne podglądy.

Poprawka w forku ESPHome obejmuje dwa miejsca:

- Zakończenie przewijania Home wywołuje istniejące
  `direct_handoff_to_lvgl(100)` przed odrzuceniem invalidacji. Brak sukcesu
  pozostawia dotychczasową ścieżkę natywnego odświeżenia.
- Zakończenie przejścia aplikacji najpierw oddaje pożyczone źródło animacji,
  następnie synchronizuje pulę i dopiero przygotowuje natywny widok oraz
  zwalnia hold/work buffer. Nieudana synchronizacja zachowuje fazę i zasoby;
  zwykła pętla ponawia próbę. Oddanie źródła jest idempotentne.

Obie operacje wykonuje właściciel LVGL. Istniejąca pauza pracowników regionów
pozostaje własnością odpowiednio swipe cleanup albo application hold; helper
jej nie przejmuje. Po opróżnieniu kolejki DSI istniejące DMA2D kopiuje ostatnią
zaprezentowaną klatkę do bezczynnych buforów. Nie dodano tasku, alokacji
pełnoekranowej, kopii CPU ani kosztu na każdą klatkę przewijania. Zachowano
RGB888, dwa pełne bufory LVGL DIRECT i trzy bufory należące do DSI.

## Źródła i walidacja

Native31 bazuje na zamrożonym native30. Konfiguracja produktu i poprzednie
optymalizacje pozostają identyczne; zmieniono tylko dwa powyższe pliki runtime.
Prace Sun/HA20 z brudnego checkoutu nie zostały dołączone do tego builda.
Dokładna różnica: `runtime-v31-from-v30.patch`.

- Manifest źródeł `source-v31-build.json`, SHA
  `54491377821176afe248449b1ab06972ce973ad4b38d629367cc7e075df0bcbb`.
- Walidacja konfiguracji: PASS. Pełny build natywnym ESP-IDF 5.5.6: PASS;
  tożsamość źródeł sprawdzona przed i po kompilacji.
- 54 testy komponentów: PASS (`focused-tests-final.log`). Osiem nowych
  testów kompiluje rzeczywiste ciała obu funkcji z kontrolowanymi właścicielami
  buforów. Sprawdzają spójność statycznego piksela, końcową pozycję gestu,
  fallback, edge bounce, kolejność oddania źródła i odroczenie/retry aplikacji.
- Ten sam nowy test uruchomiony przeciw zamrożonemu staremu runtime:
  oczekiwane 7 FAIL / 1 PASS (`native-handoff-old-negative-control.log`).
  Negatywna kontrola dotyczy kontraktu w kodzie, nie odtworzenia awarii ekranu.
- Ruff i kontrola whitespace: PASS. Istniejące ostrzeżenia deprecacji LVGL
  w pełnym buildzie nie były przedmiotem zmiany.
- Zachowany manifest artefaktów `native-context-v31/manifest.json`, SHA
  `5a9a9ee9e554685f39c7f49645a5e9932a6a7071f87036efadafb8e00d539100`.
- Pełny ELF:
  `f78afc026eb0da1d2d536560871bbf2c521134cc0858b462888eb939f5f1bd59`.
- Marker: `2026-10-30 12:42:45 +0100`.
- OTA bin SHA:
  `05908b72b2281b3d234ab1bc43891b7f32130464a3a8c3edd7ce1da2d5f62879`.

## Odbiór urządzenia — PASS w opisanym zakresie

OTA zakończone **11:53:31 UTC**, jedna próba. Wszystkie dziewięć scenariuszy
ponownie sprawdzało MAC `30:ED:A0:E2:0B:CD`, marker i pełny ELF native31.
Kampania `campaign-native31.json` trwała od 11:54:02 do 11:58:02 UTC:

1. Ustawienia i pomiar przewijania po starcie.
2. Home1→2→3, Home4→1, otwarcie/zamknięcie Playera i widoku asystenta.
3. Galeria i kamera, normalne zamknięcia do Home.
4. Home1→2 przez rzeczywisty listener LVGL, Ustawienia, przewijanie,
   zamknięcie do Home2 i gest2→1.
5. Drugi pomiar przewijania Ustawień.
6. Druga sekwencja rzeczywistego wejścia Home2/Ustawienia/Home1.
7. Ponowne otwarcie i zamknięcie Galerii oraz kamery.
8. Trzecia sekwencja rzeczywistego wejścia Home2/Ustawienia/Home1.
9. Końcowy pasywny odczyt, bez dodatkowego wybudzania.

Po pierwszym przygotowaniu nie wysyłano wybudzeń ani naprawczych redraw pomiędzy
scenariuszami. Zebrano 30 oryginałów 800×800. Wszystkie 18 obrazów Home1 zawiera
chip pogody, mikrofon, ikony statusu i wskaźniki; sprawdzono dane oryginałów
oraz wybrane pełne obrazy i wycinki kontrolek. Podglądy `*.decoded.png` są
bezstratnym odczytem JPEG; skrypt sprawdza identyczność pikseli po ponownym
odczycie PNG. Nie traktować mylnego pojedynczego podglądu jako dowodu utraty
elementów, jeśli oryginalne piksele i ich wycinki temu przeczą.

| Pomiar przewijania | FPS źródłowe | Średnio | Maksimum | Nieudane |
|---|---:|---:|---:|---:|
| native30, wcześniejszy v1 |54|16404 µs|24196 µs|0|
| native30, wcześniejszy v2 |53|16241 µs|23814 µs|0|
| native31, po starcie |54|16430 µs|27273 µs|0|
| native31, rozgrzany |54|16090 µs|22686 µs|0|

To pomiary istniejącego kontrolera, nie FPS matrycy. `max_loop` w tych
przebiegach: native30 111/115ms, native31 114/111ms; nie widać wzrostu
typowego czasu przewijania ani nowego maksimum pętli. Jednorazowe maksimum
klatki w pierwszym przebiegu wzrosło o około 3ms; nie uśredniamy go poza tabelą.

Statyczny RAM obu buildów wynosi **295584B**, wielkość aplikacji wzrosła o 48B.
Po sekwencji Player/Voice: native30 miał 4638KiB wolnego PSRAM i 28KiB internal,
native31 4628/28KiB; różnica 10KiB odpowiada pojemności JPEG preview 938→948KiB.
Po rozgrzanych mediach: native30 3331/19KiB, native31 3416/20KiB. To nie jest
ścisłe A/B tych samych zdjęć, więc różnic nie przypisujemy optymalizacji.
Końcowy pasywny odczyt native31: 3420KiB PSRAM, 20KiB internal; Home raw 5625KiB,
JPEG 1972KiB, raw/app_work/scroll/close=0. Nie pozostawiono dużego bufora aplikacji
ani przewijania; utrzymano trzy sloty Home.

Pierwszy screenshot Galerii po 12s nadal pokazuje loader (frames=0); nie
zaliczamy go jako udanego odczytu zdjęcia. Drugi pokazuje rzeczywistą fotografię,
95 zaprezentowanych klatek, 37,7FPS i 0 rejected. Nie wyizolowano przyczyny
opóźnienia pierwszego zdjęcia; brak podstaw, by nazywać ją naprawioną albo
przypisywać synchronizacji. Kamera w obu przebiegach prezentowała obraz:
55/150 klatek, 8,4/6,9FPS; źródło sieciowe było to samo, bez zmiany konfiguracji.

Brak nieoczekiwanych rozłączeń, restartów, watchdog, błędów synchronizacji
handoff i DSI underrun w tej kampanii; unsafe=0/0/0, DMA invalid/event/first_fatal=0.
Osiem preferencji zachowano, bez ich zapisu i bez komend sterujących domem.
Rewizja układu 16; końcowe pending_context_slots=0, pending_slots=49152,
snapshot_ready=false. To nie jest odbiór wszystkich off-window kart HA.

Końcowy dowód `final-verification.json`, SHA
`f5c3317ddf83aeb87901dec8c0d82dc6ae2f39ea8d866c714e13e031b1c5a4f8`,
potwierdza źródła runtime zgodne z buildem, niezmienione Git HEAD, hashe
raportów/logów/testów i zakres oceny wizualnej. Poprzedni native30 pozostaje
zachowany do rollback. Nie wykonywano ciągłego rzeczywistego audio, fizycznego
GT911 ani cykli odłączenia zasilania. Nie deklarujemy odtworzenia i naprawy
dawnego objawu wyłącznie na podstawie błędnych podglądów; usunięto konkretną
niezgodność kontraktu i potwierdzono kompletny Home na nowym firmware.

Wybrane dowody:

- [Home po trzecim powrocie z Home2](C:/aeh-build/home-screen-fix-20261030/native31-08-real_home/home-real-input-after-original.decoded.png).
- [Końcowy Home](C:/aeh-build/home-screen-fix-20261030/native31-09-baseline/home-original.decoded.png).
- [Kontrolki końcowego Home](C:/aeh-build/home-screen-fix-20261030/native31-09-baseline/controls-inspection.png).
- [Ustawienia po przewinięciu](C:/aeh-build/home-screen-fix-20261030/native31-05-benchmark/settings-after-original.decoded.png).
