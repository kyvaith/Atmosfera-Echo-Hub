# Kontynuacja i walidacja — 31 października 2026

Użytkownik jawnie wznowił pracę. Zmiany pozostają lokalne, bez staging,
commitów i wysyłki. Dowody: `D:\aeh-build\feature-continuation-20261031`;
zamrożone źródła i obrazy nadal w katalogu `feature-continuation-20261030`.

## Świeży stan przed zmianą

### HA50–52: nastawa, HVAC i początkowy akcent edytora

HA50/native40:564Python(3skip)/289Node/35hashy. Climate-temperature-v4 to dwa
rzeczywiste targetcommands22.0/21.5 przed feedback i zero HVACmode. Endpoints,
unknown/offgrid/auto/outage/step/unit mismatch/recovery/heldABA, PL/EN,16oryginałów
i browser review/Confirm/twoUndo/noSave PASS; exact cleanup133. Próby48/v1 i49/v2-v3
zakończyły się przed bindem, źródła QA usunięte; faktyczna przyczyna to Core
UnitOfTemperature StrEnum na ścisłej granicy plainstr NumericDomain. Str po
sprawdzeniu zgodności jednostek naprawia50, bez osłabienia NumericDomain.
DATA_COMPONENT/HassKeystr nie był przyczyną. Pierwszy post-performance timeout
list_entities PRZED inputem pozostajeFAILED; świeży v2:79klatek/53sourceFPS/
avg16340us/max23134us/failed0, app_work/scroll/close0. Ograniczenia cross-unit,
range/auto target i wspólnego retained-result caption są w projekcie nastawy.

HA51:570Python(3skip)/292Node/35hashy. Climate-hvac-v1: cztery realne broker
commands heat/auto/cool/off przed feedback, zero targetcommands. Cancel/no-op/
heldABA/reordered/reducedlist/outage/recovery/PL/EN,15oryginałów i rzeczywisty
browser review/Confirm/twoUndo/noSave PASS; cleanup135.80klatek/54sourceFPS/
avg16266us/max24959us/failed0, PSRAM4810KiB/largest2688/internal21/JPEG927,
app_work/scroll/close0. Receipts ha50-temperature-scoped-acceptance.json oraz
ha51-hvac-scoped-acceptance.json; we wszystkich 16kart/3kamery/8preferencji
zachowane, własne helper/topics/token usunięte, faults[].

Osobny defekt przy restarcieHA51: nativeAEE2FF, APIpodglądu36BCF0, potwierdzone
bez zmiany preferencji i pikselami oryginalnego browserJPEG. HA52 bierze świeży,
typed, nie-stale TextState z aktualnego runtime Core po podpięciu istniejącego
obserwatora; nie nadpisuje nowszego callbacku ani legacywire/locale/opcji.
573Python(3skip)/292Node/35hashy, atomowy exchange i1restart. Po restarcie
native/API AEE2FF, oryginalny browser podgląd ma dominantRGB175/226/255,
czysty układ135/noSave.80klatek/54sourceFPS/avg16235us/max24889us/failed0,
PSRAM5156KiB/largest2688/internal25/JPEG918, app_work/scroll/close0. Pogoda
zmieniła się na sunny2192KiB, więc zmian heapu nie nazywać optymalizacją.
Finalny Home sprawdzony, ELF40 potwierdzony, opcje135 identyczne z51.
Receipt ha52-accent-scoped-acceptance.json. Brak nowej deklaracji odbioru
fizycznego HVAC/GT911/Sendspin/cold-start. Wszystko pozostaje lokalne.

### HA47: wybór kierunku odebrany

555Python(3skip)/286Node i focused static/diff checks PASS.34 frozen/installed
pliki zgodne po jednej atomowej instalacji i jednym restarcie; dane/opcje bez
zmian poza rewizją. Fan-direction-v1 na native40: dokładnie jeden realny
fan.set_direction reverse i jeden broker command przed feedback; zero power.
Lokalny wybór/cancel/no-op/held kierunekABA, zmiana języka zamykająca selekcję,
PL/EN, outage/loss i10oryginałów PASS. Rzeczywisty browser potwierdził kierunek,
review/Confirm/dwaUndo/czysty szkic/noSave. Cleanup131 zachował16kart/3kamery/
8preferencji, usunął własny MQTThelper/topics i unieważnił token, faults[].
Normalna trasa81klatek/54sourceFPS/avg15998us/max23975us/failed0,
PSRAM4828KiB/largest3200/internal22/JPEG913; app_work/scroll/close0.
Kontakt10oryginałów, provenance i finalny Home sprawdzone. Pełny ELF40 ponownie
potwierdzony; jest to adapterHA bez nowego firmware. Fizyczny silnik/GT911,
długie audio/Sendspin/cold-power pozostają osobnymi bramkami.
Receipt `ha47-direction-scoped-acceptance.json` w katalogu dowodów31.

### Odebrane później: manual40/HA45 i oscylacja HA46

Końcowa kampania manual-v10 na przywróconym native40 przeszła realny MQTT,
nullable expected_index, cancel/no-op/ABA/list/outage/loss, PL/EN,12oryginałów
i browser review/Confirm/twoUndo/noSave. Cleanup127 i osiem preferencji
zachowane. Normalna trasa Home/Settings:79klatek/54sourceFPS/avg16656us/
max23150us/failed0,4820KiB PSRAM, largest2752KiB, internal22KiB, JPEG920KiB,
app_work/scroll/close0. Receipt `manual40-ha45-scoped-acceptance.json`.

HA46:549Python(3skip)/283Node; atomowa instalacja34plików i jeden restart,
dane/opcje zachowane. Kampania fan-oscillation-v1: dwa faktyczne broker payload
OSC_ON/OFF przed feedback, dokładnie dwa fan.oscillate i zero power. Held
availability ABA/offline/capability loss/recovery, PL/EN,9oryginałów i rzeczywisty
browser draft/edit/twoUndo/noSave PASS. Cleanup129:16kart/3kamery/8preferencji,
unikalny MQTT helper/topics usunięte, token unieważniony, faults[]. Świeża
inwentaryzacja34/34hashy; znormalizowane opcje nadal88e55ff72673c011624afb20b69fa1558eb1a7f0e179ea27f76e59937165f500.
Normalna trasa:79klatek/53sourceFPS/avg16634us/max24658us/failed0,
PSRAM4822KiB/largest3200KiB/internal22KiB/JPEG917KiB; app_work/scroll/close0.
Średni koszt klatki jest porównywalny; różnica sourceFPS nie jest pomiarem
fizycznego panelu. Kontakt z9oryginałów, provenance i finalny Home sprawdzone.
Receipt `ha46-oscillation-scoped-acceptance.json`. Firmware native40, jego pełny
ELF potwierdzony ponownie; oscylacja jest zmianą HA bez nowego firmware.
Fizyczny silnik, dotykGT911, długie audio/Sendspin/cold-power pozostają osobnymi
bramkami. Poniższe wcześniejsze próby i błędy zachowano jako historię.

### Późniejsza kontynuacja: manual/empty-choice w odbiorze

HA44 zainstalowane atomowo,33/33 pliki zgodne; dane/opcje zachowane przy109.
Native40: config i pełny ESP-IDF build PASS,527 wygenerowanych źródeł zgodnych
z pinem,205 fork TU i2308 compile commands. Źródła
`source-v40-build.json` SHA`ac25455e08e150790a947f7e80d8c595b1400d20fb7f43c884ba1770ec0bba32`.
540Python(3skip),280Node i26native/248subtests PASS. Nie zaliczać wcześniejszych
host prób z błędem kompilacji ani z naruszonym pinem podczas testu.

Jedno OTA40 i świeża pełna tożsamość urządzenia PASS: marker
`2026-10-31 12:53:38 +0100`, ELF
`d02f30cb4a388e2dc5e577abfd3d72c495ab6ec1b369f9eca2ede22b121944a5`.
Artefakty `C:\aeh-build\native-context-v40`; statyczny RAM296512B (+168B względem39),
OTA7981584B (+3984B). Brak nowego taska/timera/bufora; sdkconfig/defines bez zmian.

**Runtime nadal nieodebrany.** Kampania fan-manual-v1 z rzeczywistym resetem
MQTT presetu do None: początkowy brak zaznaczenia, lokalny wybór, browser
„Tryb ręczny”, review/Confirm/dwa Undo bez Save przeszły. Po zamknięciu i
ponownym otwarciu Apply nie wysłał polecenia: FAILED `No broker command`.
V2 błędnie wymagało wyzerowania `opening` w diagnostyce; ten bit opisuje
ostatni kierunek także po zakończeniu animacji. V3 sprawdza rzeczywiste
active/pending/running i ponownie ujawnia brak polecenia. Oryginał
`fan-manual-v3/manual-before-apply-original.jpg` został początkowo błędnie
odczytany w podglądzie jako brak nagłówka i Apply. Późniejsza kontrola pikseli
oryginalnych JPEG oraz wyciętego nagłówka nie potwierdziła tego artefaktu.
Ten wniosek wizualny jest wycofany; rzeczywisty brak polecenia naprawia HA45.
Wszystkie trzy próby wykonały strzeżony inverse/cleanup do111/113/115,
usunęły własne encje/topics i unieważniły token; zero usterek w obserwowanym logu.
Rzeczywisty browser v3 ponownie potwierdził manual/choice przy114.

Native41 zawiera wyłącznie dodatkową geometrię/widoczność choice na istniejące
żądanie debug_scalar_performance, pod istniejącą domyślnie wyłączoną flagą.
Konfiguracja/build/audyt PASS, źródła SHA
`6b09eb991616d96d9c2b8af68e154c39e5df410ef0d86524c76962be30f50dc5`.
Nie jest to naprawa. Odebrać faktyczne uruchomienie i diagnozę osobno.

### Korekta odczytu zrzutów i wycofanie eksperymentów display

W źródłowych11JPEG kampanii manual-v8 nagłówek ma zawsze1634 jasne piksele,
a ikony807, także w manual-applied-preset i EN. Crop oryginalnego EN potwierdza
obecność obu elementów (`english-header-crop-proof.png`). Odczyt podglądu jako
fizycznego zniknięcia niezmienionych elementów był błędny. Nie przypisywać tego
urządzeniu ani nie nazywać naprawy43/44 potwierdzoną optymalizacją.

Dochodzenie do braku polecenia potwierdziło rzeczywisty błąd: schema usługi
report_entity_control odrzucała nullable expected_index przed dopasowaniem
negocjowanego ownera. HA45 używa wspólnego decode_report do struktury/kierunku;
owner zachowuje ścisłą walidację kanału/negocjacji przed autoryzacją.
Osobny pakiet541Python(3skip)/280Node/33pliki jest zainstalowany, a rzeczywisty
MQTT/null command/provider feedback/PL/EN/ABA/cleanup przechodzą w v7–v9.

Sześć plików eksperymentów display43/44 przywrócono dokładnie do hashy40,
z ochroną przed nadpisaniem cudzej edycji; manifest display-experiments-retired.json.
Zachowano legalne manual-choice z40 i WIP oscylacji HA46. Build44 przerwano,
nie został wgrany. Wgrywany jest ponownie zachowany native40 z pełną pre-
tożsamością43, w jednej próbie; odbiór tego powrotu i kampania v10 są osobne.
Nie edytowano przypiętych źródeł ani wcześniejszych surowych receipts.

Zweryfikowana kopia kompilatorowego cache jest używana na C przez
manual40-hostenv.ps1. Stara kopia na D pozostała: końcowe usunięcie zostało
zablokowane automatycznie; nie ponawiano obejściem. D jest exFAT, kompresja
NTFS niedostępna. Nie usunięto SDK ani aktywnych build dependencies.

### Historyczny początek dnia

Native38 / HA39 / rewizja95 potwierdzone na żywo. Marker
`2026-10-30 23:38:50 +0100`, ELF
`71ec85684792b041078b6a059d7e1ee13c0a2b0fbfa8a234c27dda487395a6bd`.
HA: 33/33 pliki zgodne z lokalnym źródłem; hashe danych i opcji zgodne
z końcowym checkpointem. Zachowane 16 kart, trzy kamery i osiem preferencji.
Nocny timeout nie jest obecnie odtwarzany; jego przyczyny nie ustalono.

## Dokończenie przerwanych scenariuszy native38

Każdy przebieg używał jednego właściciela wejścia, normalnych gestów Home
i sprawdzenia pełnego ELF; nie używano skrótu `debug_navigation_home`.

| Przebieg | Segmenty | FPS źródłowe | Średnia / maksimum | Failed |
| --- | ---: | ---: | --- | ---: |
| Wznowiony Home1→Home2→Settings→Home2→Home1 | 1 | 53 | 16941 / 24415 us | 0 |
| Po pierwszym Gallery+Camera | 1 | 54 | 16196 / 23973 us | 0 |
| Po drugim Gallery+Camera | **2** | **53** | 16541 / 23214 us | 0 |

W dwóch ostatnich wierszach Gallery i Camera były obserwowane po 40 s każda.
Nie wystąpiły nieoczekiwane przejścia do Voice/Home, rozłączenia ani błędy
DSI/fatal. Pierwsza kamera: 496 prezentacji, 14,9 presentation FPS,
queue_drop=0/stale_drop=0. To nie jest porównanie identycznego strumienia
z poprzednim dniem. Oryginalne obrazy Galerii, Kamery i pełnego Home obejrzano;
Home przeszedł też kontrolę pikseli wszystkich czterech obszarów.

Rzeczywisty fallback dwóch segmentów miał pool=NO/attached=NO, wymagane
3 657 600 B, największy blok po trim 3264 KiB. Potwierdza poprawę wariantu
pamięciowego względem wcześniejszych 47 FPS / 14 części, przy różnej historii
cache. Po zamknięciu Settings: scroll=0, app_work=0, close=0 i trzy sloty
Home (5625 KiB). Przed/po tym przebiegu PSRAM 3452/3454 KiB, największy blok
1856/1856 KiB. Nie jest to twierdzenie o identycznej pamięci między wersjami
ani długotrwałym braku wycieku.

Oryginały Cover-v6 również obejrzano: poprawny separator, czytelny aktywny Stop,
zablokowane polecenia ruchu podczas pending, poprawny stan braku dostępności
i odebranych możliwości. Odbiór fizycznego silnika i przeglądarki pozostaje
oddzielny; nie zamykać całej rodziny Cover.

## Odkryty błąd pozycji podczas odświeżania

`native38-segmented-refresh` przechodzi sprawdzenia funkcjonalne i przywraca
Wake Sound, ale obrazy ujawniły przesunięcie listy. Nie przyjmujemy go jako
pełnego odbioru wizualnego. Agregat 107 klatek / 11 FPS zawiera postoje
i dwa zapisy preferencji; koszt klatki wynosi 16404 us, failed=0, segments=2.

Osobny `native38-refresh-position-diagnostic` ustawia listę na końcu normalnym
benchmarkiem i dopiero potem dwukrotnie zmienia Wake Sound. Log: finish y=724,
refresh y=724, następny refresh y=615. Odtworzono błąd geometrii: przywrócenie
wysokości 800 po ostatnim segmencie 691 wymaga przeliczenia layoutu przed
przywróceniem offsetu. Inaczej LVGL przelicza granice na podstawie starej
wysokości, zmieniając rzeczywisty scroll o 109 px.

Odczyt źródła wskazał tę samą kolejność w capture i refresh. Osobny eksperyment
z niezmienioną rzeczywistą biblioteką LVGL odtworzył 724→615→506→397. Dodanie
przeliczenia layoutu przed przywróceniem offsetu zachowało wszystkie 48
pozycji: wysokości segmentu 109/691/833/1524, pozycje 0/100/500/724, trzy
powtórzenia każdej kombinacji. To test semantyki LVGL i mechanizmu naprawy,
nie wykonanie pełnej funkcji firmware na hoście. Zachowane źródło, wyjście
i hash w `scroll-layout-host-proof.json` oraz `.log`.

Diagnostyczny Swipe Debug i Wake Sound wróciły do false; cztery zapisy
preferencji, bez zmiany ośmiu wartości końcowych, bez domowych poleceń.

## Native39 — kompilacja i OTA zakończone, odbiór sprzętowy w toku

Jedyna zmiana wykonawcza od native38: dwa wywołania `lv_obj_update_layout`
w `lvgl_esphome.cpp`, po odtworzeniu wysokości i przed offsetem, w capture
i refresh. Snapshot nadal należy do otwartej sesji Settings; worker musi
zostać zatrzymany przed zmianą geometrii. Bez nowej alokacji, taska, formatu,
kopiowania CPU ani zmiany czasu życia. Produkt wykonawczy bez zmian.

Źródła: `source-v39-build.json`, SHA256
`62fe9756741ec37422df3d6c1ff0d50b640c7efed6829a403834dac4a813ffc0`;
332 pliki produktu, 11751 forka; delta forka dokładnie jeden plik.
17 skupionych testów geometrii, spanów, błędów alokacji, drain i schematu PASS.
Formatowanie dwóch zmienionych linii i diff-check PASS. Pełny dry-run
clang-format nadal wskazuje dwie wcześniejsze, niezmienione linie12677/12931;
nie jest pełnym PASS formatowania całego pliku. Nie rozszerzano naprawy.

Pełne config/ESP-IDF build PASS (Ninja4), źródła po buildzie zweryfikowane.
Audyt:527 plików,205 jednostek forka,2308 komend. Statyczny RAM296344 B
bez zmiany, OTA7977600 B (+16 B); sdkconfig i defines identyczne z native38.

- Marker: `2026-10-31 09:35:47 +0100`.
- ELF: `805cfca533fd20053db3331714cb18ff4db00265abdedaaa81fb4010d69317c4`.
- Zachowany `native-context-v39/manifest.json`, SHA256
  `e0862eaa12f2af5ec3fdea340af8dafc021ab783e5aeffdf21c82ec5141c05a5`.
- OTA SHA256 `e9d744060e6cd18218d6dae822d91c81d07af97305301f721029000916f398dd`.
- Jedno OTA PASS, zakończone08:48:33 UTC; stary obraz zweryfikowany przed
  zapisem. Nie ponawiano OTA po błędzie narzędzia opisanym niżej.

Pierwszy preflight zatrzymał własną zbyt wczesną asercję revision==95, jeszcze
przed dotykiem. Pierwszej rzeczywistej wartości rewizji nie zachował; nie
przypisywać jej konkretnego zera. Kolejny odczyt wykazał95. Wersja v2 czeka
na konfigurację przed testem gotowości i zachowuje odczyty. `native39-preflight-v2`
PASS: pełny ELF, CoverStop1, revision95, Home1, accepted blank tap/release,
osiem preferencji bez zmiany, faults=[] i zero zapisów/domowych poleceń.
Pierwsza nieudana próba pozostaje osobnym raportem.

Pierwsza kampania `run_native39_validation.py` ukończyła pięć normalnych
przebiegów Home/Settings i cztery cykle Gallery+Camera. Wyniki53/54/55/54/54FPS,
failed0, bez DSI/fatal/disconnect; jednak wszystkie używały jednego segmentu.
**Raport zbiorczy pozostaje FAILED** na asercji braku próbek fallbacku,
nie na błędzie firmware. Nie przepisano tego raportu na PASS.

Rozszerzenie: Player otwarty/zamknięty bez playback i bez uruchamiania Voice,
zwykłe gesty do Home4, Settings:2 segmenty,54FPS,16352/23694us,failed0.
Kolejne osobne wejścia z Home2/4/3 sprawdzały poprawną pozycję, lecz znowu
trafiały w jeden segment. Test musi zachować tę samą sesję Settings, gdy
rzeczywiście uda się otrzymać partycję; zamknięcie może zmienić układ heapu.

`run_segmented_refresh_search.py` ma ograniczone cztery okna Home i zmienia
preferencje dopiero po wykryciu rzeczywistej partycji. Pierwszy przypadek
Home4 po otwarciu Playera uzyskał2 segmenty,**55FPS**,16657/23525us,failed0.
W tej samej sesji trzy odświeżenia utrzymały **y=724 / segments=2**.
Zmiana/przywrócenie Wake Sound:dy=0/0px, średni błąd obrazu0,00097/0,0
w badanym stałym obszarze, przy wykluczeniu pola wartości. Cztery zapisy
(Swipe Debug i Wake Sound), wszystkie osiem wartości końcowych identyczne.

Oryginały powyższego przypadku obejrzano w `native39-final-segmented-review.png`:
wiersze bez przesunięcia i widocznych szwów, poprawne ON/OFF, czytelny Player
z akcentem i kompletny Home4. Powrót na Home1 zachowuje zegar, pogodę,
mikrofon i status. Bramka scroll/refresh native39 ma ten ograniczony odbiór
sprzętowy; nie stanowi ponownego testu fizycznego silnika Cover, akustycznego
dialogu, długiego Sendspin ani niewyjaśnionego starszego incydentu native35.

## Pasywne daty — HA40 / native39

HA owns strict Gregorian calendar formatting only for `sensor` entities with
`device_class: date`. PL:DD.MM.YYYY, EN:YYYY-MM-DD. Exact user mappings win,
exceptional states remain explicit, precision is ignored for these dates.
The formatter does not convert timezones or change timestamp/uptime/action
semantics. The preview uses the same shared golden cases.

519 Python tests OK (3 skipped),273 Node tests PASS, focused Ruff F checks PASS.
Thirty shared vectors cover valid/leap/boundary years, malformed separators,
Unicode digits, whitespace, non-string input and impossible dates. Additional
tests cover overrides, timezone independence and unaffected domains.

Five installed files change from HA39:formatting/cards/editor/manifest/panel.
Source pin `ha40-source-pin.json`,33/33 installed hashes match. One atomic
exchange and one Core restart, backup outside the component loader. Before
and after installation, data/options hashes,revision95,16cards/3cameras match.
Actual API and panel registration passed. Browser interaction remains unrun
pending desktop-unlock confirmation; Node tests are not a browser acceptance.

Firmware remains the exact flashed native39: this slice changes HA projection,
not firmware code. It adds no wire field, task, subscription, timer or raw
surface; the existing tile label and dirty-slot path render the bounded text.

`calendar-date-v1`:one owned real MQTT date sensor. Actual installed Core2026.7.1
source confirms invalid input becomes unknown. Eight physical screenshots
and HA/native states passed:PL date, leap2000, mapped label, invalid1900,
unavailable, EN, restored PL and an offscreen update. Two passive taps caused
no service. Locale changed twice and returned; all eight preferences match.
Originals were visually reviewed in `calendar-date-v1-review.png`.

The exact layout was restored, normal CAS revision95→96→97, all16 cards unchanged
after normalizing only revision. Own MQTT discovery/state/availability were
cleared and the entity removed after unbinding. Ephemeral auth token revoked;
faults=[]; no household commands. Data hash unchanged,three cameras retained.
`ha40-date-layout-scope-proof.json` and the after-cleanup inventory retain proof.

Post-feature normal Home1→Home2→Settings→Home2→Home1:80frames,**53FPS**,
16406/25760us,failed0, no DSI/fatal. Both final Home originals pass pixel
completeness. Settings scroll/app-work/close allocations are0 after close,
three Home slots remain5625KiB. PSRAM3456→4316KiB while JPEG backing shrinks
1770→918KiB; this is cache/history accounting, not cross-version memory parity
or a general leak claim. This accepts the passive date slice, not all W10.

## Date/time helpers — HA41 trial, HA42 correction / native39

All three `input_datetime` capability modes are implemented as passive
information. HA validates exact ASCII dates/times and boolean capability flags,
keeps seconds and local literals, preserves exact user mappings and explicit
outages. No native protocol, widget, font, buffer, task or timer changes.

The first HA41 campaign `datetime-info-v1` passed source/native values,
PL/EN, passive taps, offscreen updates and cleanup (97→98→99), but **failed
visual acceptance**: the 19-character combined value clips in slot15's 136 px
Roboto16 caption. Its aggregate status still says visual pending; it must not
be promoted to visual PASS. Its first browser stage timed out, with two later
stages separately observed. Preserve those original receipts and images.

HA42 restricts helper placement to slots3/5/8/9/10/11/12, based on actual
caption widths at least172 px. A helper's capabilities may change after saving,
so date-only helpers use the same maximum-width contract. Both server and
editor gate assignment, swap, clipboard, import, draft recovery and save.
The inspector explains the requirement and offers only Information/no action.
A product-source test checks the declared captions, rather than tile widths.
Host evidence:523 Python OK (3 skipped) before the extra caption test;
the focused file now has5 passing tests.277 Node PASS, focused Ruff F PASS.
The first adjusted Node run exposed an occupied mock clipboard destination;
its receipt remains failed, followed by the corrected test-fixture run.

Atomic HA42 installation and one restart passed,33/33 installed source pins;
entry data/options and revision99 were unchanged by installation. A too-early
`datetime-info-v2` probe saw unknown_command during Core startup. It created no
helper, made no layout/preference changes, and revoked its token. A fresh v3
campaign waits for real API registration instead of treating process start as
readiness.

`datetime-info-v3` passed date/time/combined, exact mapping, EN→PL and offscreen
source updates. All seven originals plus final Home were visually reviewed in
`datetime-info-v3-review.jpg`; the full combined value is readable in the
172 px slot10 caption. All three browser stages now have actual live preview,
read-only inspector, permitted-place observations and saved screenshots.
The user explicitly confirmed the desktop was unlocked before this work.

Two passive native taps sent no services. Only owned helper set_datetime calls
were observed. Exact field restoration99→100→101, helper definitions before/
after identical, own entity deleted after unbinding,8 preferences restored,
faults=[], temporary auth token revoked. `ha42-datetime-layout-scope-proof.json`
and the after-cleanup inventory preserve16cards/3cameras and33/33 source hashes.

Post-feature normal Home/Settings route:79frames,**54FPS**,16260us average,
25915us maximum,failed0, no recorded DSI/fatal fault. Home slots remain5625KiB;
scroll/app-work/close allocations are0 after close, JPEG925→914KiB. This short
same-run observation is not long-run audio, heap parity or physical touch proof.
Firmware remains the exact flashed native39 ELF; these subsequent HA-only
changes neither replace nor reflash that image.

## Live calendar preview completed

After the explicit desktop-unlock reply, `calendar-date-v2` checks the separate
sensor.date preview in the real HA panel:31.10.2026 despite precision6, passive
tap disabled, clean draft/no browser Save. Its owned MQTT/native repeat and
cleanup101→102→103 also pass. `date-pl-browser.jpg` records the actual panel;
`ha42-calendar-browser-scope-proof.json` verifies the exact layout inverse.
This closes the earlier browser gap for this fragment, not all W10 formats.

## Fan preset adapter — HA43 / native39

HA43 reuses the accepted choice/app6 runtime for available fans with an existing
known preset. PRESET_MODE8, a registered set_preset_mode service, bounded exact
preset_modes and an on/off power state are required. Power and preset are
distinct observations; the adapter sends preset_mode, never an inferred power
toggle. The tile and preview show the preset. The existing default fan toggle
is unchanged. None/manual remains an explicit unavailable choice under this
first adapter; it never becomes option0. Speed/direction/oscillation and choosing
the first preset from manual mode remain separate W06 work.

532 Python tests OK (3 skipped),279 Node PASS, focused Ruff F PASS. Tests cover
IntFlag metadata, service/capability loss, complete list rejection, exact Unicode
and whitespace, stale preset ABA, expired list, matching state vs service-only
acceptance, preview, draft review and Undo. The initial focused assertions used
the wrong existing terminal label and omitted native support in projection;
preserve those failures and their corrected passing runs.

HA43 installation: one guarded atomic exchange, one Core restart. The before
data/options and revision103 were preserved; final installed33/33 hashes match
ha43-source-pin.json. No firmware source, protocol, widget, task, timer or raw
buffer changed for this adapter.

Owned real MQTT fan campaigns retain all failures honestly:

- v1 failed in an inherited date assertion before binding. Its cleanup observer
  also missed scalar logs; a separate guarded recovery removed only that own
  unbound fixture and proved the original layout unchanged at103.
- v2 passed real Apply/MQTT feedback and actual browser review/Confirm/two Undo
  to a clean original draft. It stopped when the negative-input helper required
  acceptance after a legitimate selection revocation. Exact cleanup105 passed.
- v3 passed unavailable input suppression too, then the readiness observer
  missed a delayed header by sampling only200ms. Preserved log headers already
  show selected0/view_ready0/pending0. Cleanup107 passed.
- v4 waits for its own bounded log header and records rejected negative input
  separately. The complete device campaign passes, with cleanup109. Browser
  evidence is explicitly the separate v2 observation on identical HA43/native39,
  not a fictional browser rerun inside v4.

v4 confirms initial Eco, a local Komfort candidate with zero command, cancel,
reopen, Apply Cichy nocą, no-op, list reordering/revocation, unavailable and loss
of the preset capability. Exactly one fan.set_preset_mode and one actual
non-retained broker preset payload preceded the QA provider's state feedback.
No power command was emitted. Matching native current/header then appeared.
This is a software/broker round trip, not physical fan or acoustic acceptance.

All seven scenario originals plus final Home were visually reviewed in
fan-preset-v4-review.jpg: readable accent/contrast/current-vs-candidate, disabled
Apply and clear changed/unavailable states. The separate browser modal and
clean-after-Undo screenshots are preserved in fan-preset-v2.

Exact field inverse107→108→109, own entity/topics removed after unbinding,
all8 preferences match, faults=[], temporary auth revoked. Final normal
Home1→Home2→Settings→Home2→Home1:80frames,**55FPS**,16626us average,
23809us maximum,failed0, no recorded DSI/fatal fault. Scroll/app-work/close0;
three Home slots5625KiB; JPEG929→909KiB. Both final Home originals pass pixel
completeness and the final original was visually inspected. Short cadence and
buffer-release evidence do not establish p95, long audio or heap parity.

`whole-day-protected-options-proof.json` compares actual HA storage with the
fresh day baseline: data and **all options** identical after normalizing only
revision109→95 in a read-only copy.16cards and3cameras preserved; no storage
revision was rolled back. No staging, commit or GitHub publication occurred.

## HA53 climate program / native40 unchanged

580Python(3skip)/295Node and static/diff checks passed. Atomic35file installation preserved135 data/options. Real climate-preset-v1 binds136/inverts137;4 actual set_preset_mode/broker commands eco/comfort/sleep/none, each observed before provider feedback. No mode/target command, no local candidate/cancel/no-op/heldABA duplicate. List reorder/reduction, capability loss, outage/recovery, PL/EN accepted.16 original800x800 JPEGs/contact provenance and actual browser review/Confirm/twoUndo/noSave reviewed. Fixture discovery/topics/registry removed and ephemeral token revoked. Preferences8 restored; faults[]. Native40 ELF reverified; no new native binary was needed or flashed. Performance79frames/53sourceFPS/avg16348us/max24440us/failed0; PSRAM5619/largest3456/internal35/JPEG928; app_work/scroll/close0. Weather now clear-night1792KiB; heap deltas are not causal optimization evidence. Acceptance receipt ha53-preset-scoped-acceptance.json in D:\aeh-build\feature-continuation-20261031. Nullable climate policy host tests remain distinct from actual MQTT literal none and separately hardware accepted generic native40 empty-choice protocol. Physical HVAC not tested.

## HA54 climate fan mode / native40 unchanged

587Python(3skip)/298Node/static passed;35pinned installed files. Climate-fan-v1 binds138/inverts139:4actual set_fan_mode/MQTT commands low/medium/high/auto before feedback,0separateHVAC/target/preset commands; cancel/no-op/heldABA/list/reorder/caploss/outage/recovery/PLEN.16originals/contact and actual browser review/Confirm/2Undo/noSave reviewed. HA labels Auto/Low/Medium/High retained in both locales; project Polish fallbacks host-tested. Extra generic inspector hint cosmetic follow-up. Fixture/topic/registry cleanup and token revocation passed;8prefs restored/faults[]. Final Home reviewed. Post80frames/54sourceFPS/avg16347us/max23622us/failed0; PSRAM5629/largest2816/internal35/JPEG916/weather1792/work-scroll-close0. Native40 ELF reverified; no new native binary/flash. Physical HVAC absent. Receipt ha54-climate-fan-scoped-acceptance.json under original D work root. Next test artifacts move to C:\aeh-build\feature-continuation-20261031-next due low free D space, preserving all evidence.

## HA55 climate swing32 / native40 unchanged

594Python(3skip)/301Node/static/diff passed;35source hashes match installed. Climate-swing-v1 binds140/inverts141:5actual set_swing_mode/MQTT commands vertical/horizontal/both/on/off beforefeedback,0separateHVAC/target/preset/fan. Cancel/no-op/heldABA/list/reorder/reduction/caploss/outage/recovery/PLEN accepted.17originals/contact and actual browser review/Confirm/2Undo/noSave reviewed. Separate fan-only draft proved corrected short hint/no generic slider text, Undo restored swing. Fixture/topics/registry removed, token revoked,8prefs restored/faults[]. Final Home reviewed. Post80frames/53sourceFPS/avg16786us/max24347us/failed0; PSRAM5623/largest2688/internal35/JPEG922/weather1792/work-scroll-close0. No extra native task/buffer or new native binary/flash; ELF40 verified. Physical HVAC absent; distinct horizontal512 remains next. Receipt ha55-swing-scoped-acceptance.json under new C work root. Failed focused testv1 was a wrong mock translation key (.state.auto for off), corrected to actual .state.off; focusedv2 and full suite passed without changing runtime for that test error.

## HA56 independent horizontal512 / native40 unchanged

602Python(3skip)/304Node/static/diff passed;35pinned source hashes match installed. Climate-horizontal-v1 binds142/inverts143:3actual set_swing_horizontal_mode/MQTT commands Prawy Żółty/on/off beforefeedback,0separateHVAC/target/preset/fan/swing32. Actual feature512loss while32retained revokes horizontal; cancel/no-op/heldABA/list/reorder/reduction/caploss/outage/recovery/PLEN accepted.15originals/contact and actual browser review/Confirm/2Undo/noSave reviewed. Exact fixture/topics/registry cleanup, token revoked,8prefs restored/faults[]. Post81frames/54sourceFPS/avg16074us/max23082us/failed0;PSRAM5629/largest2688/internal35/JPEG917/weather1792/work-scroll-close0. Final Home original reviewed. Native40 ELF verified; no new native runtime/binary/flash. Physical HVAC absent. Receipt ha56-horizontal-scoped-acceptance.json under C work root.

## HA57 humidifier/dehumidifier domain and power / native40 unchanged

612Python(3skip)/307Node/static/diff passed;35source hashes match installed. V1 failed an invalid Core behavior expectation (MODES1 is sticky after mode-list removal); actual events/source pin retained, exactcleanup145/prefs/token/faults[] confirmed. No source workaround. V2 starts real fresh feature0 MQTT humidifier, then adds modes/dehumidifier. Bind146/invert147:4actual turn_on/off services and HUM_ON/HUM_OFF broker commands beforefeedback,0mode/target, heldavailabilityABA/offline/recovery/PLEN/color accepted.12original Home800x800 images/contact and actual browser library assignment/Undo, color opt-out/Undo/noSave reviewed. Exact fixture/topic/registry cleanup/token revoked/8prefs/faults[]. Post80frames/54sourceFPS/avg16559us/max24296us/failed0;PSRAM5633/largest2816/internal35/JPEG912/weather1792/work-scroll-close0. Final Home original reviewed, ELF40 verified. No new native binary/flash; physical humidity devices absent. Receipt ha57-humidifier-power-scoped-acceptance.json in C work root.

## HA58 humidifier mode / native40 unchanged

621Python(3skip)/310Node/static/diff and35installed source hashes passed. Humidifier-mode-v1 binds148/inverts149:4actual set_mode/MQTT commands eco/sleep/ Żółty /normal beforefeedback,0power/humidity; actual None reset blocks candidate/Apply; actual stickyMODES1+empty available_modes revokes selection. Cancel/no-op/heldABA/list/reorder/reduction/outage/recovery/PLEN accepted.18originals/contact, actual browser review/Confirm/2Undo/noSave and final Home original reviewed. Exact fixture/topics/registry cleanup/token revoked/8prefs/faults[]. Post79frames/53sourceFPS/2segments/avg16284us/max22973us/failed0;PSRAM5631/largest2048/internal35/JPEG916/weather1792/work0. Total heap flat, largest free block differs; monitor next slice without claiming optimization or hiding by reboot. Native40 ELF verified, no new native binary/flash; physical devices absent. Generic service option metadata guard skips malformed None/string/map while keeping legacy list/tuple descriptors; native Choice still strict list. Focusedv1 test fixture had copied climate expected-domain and omitted expected ProtocolError for an unavailable command; corrected in focusedv2, runtime unchanged for those test mistakes. Receipt ha58-humidifier-mode-scoped-acceptance.json under C work root.


## Native45 Number current-value caption / HA58

Config, complete ESP-IDF build, public-LVGL focused5tests/15scenarios and
527generated/205fork-TU/2308-command audit passed. Registry dependency versions
and hashes, SDK values/disabled options and generated defines match40; SDK header
only reordered four equivalent defines. StaticRAM296512bytes unchanged. Source45b
manifest and independent ZIP/OTA are pinned by
C:/aeh-build/feature-continuation-20261031-next/native45-caption-scoped-acceptance.json.
One successful OTA, full ELF c74f3f2172234acbfb96dfe45f154dcbb5f89d8700384997f50ca8ed988586d5 verified.

Real native temperature campaign sends2broker commands before provider feedback,
zero HVAC command; heldABA/endpoints/None/offgrid/auto/unavailable/domain and unit
changes/PLEN passed.18original800x800 images and contact reviewed, including both
unavailable captions and final complete Home. Exact cleanup151/fixture/topics/
registry/token revoked/8prefs restored/faults[]. Post79frames/54sourceFPS/avg16633us/
max24061us/failed0 vs pre80/55/16600us/23591us/0. PSRAM5636KiB/internal35KiB,
app-work/scroll/close0; control241KiB retained setup. Largest2112KiB varies with
cache lifecycle; no sustained total-memory loss observed in this short route.
No physical panel-FPS, finger/actuator, audio or long-duration acceptance claim.

Failed build attempts were environment failures: F was a virtual disk backed by
full D; later incomplete dependency download/console encoding and disk space.
Retained logs; final compile-space-r2 exit0 and immutable source recheck passed.
Recovered space by lossless NTFS compression, preserving files. Automatic review
rejected removing the new failed download directory; action was not retried and
that directory remains. Old rejected D Zig cache remains too.
Initial read-only readiness check incorrectly required all pages to have no
pending slots before any navigation; corrected to identity/configuration readiness
plus actual target-slot fencing. Original startup raw header/weather/mic/indicator
pixels were complete despite incremental preview. No renderer workaround added.

## HA59 humidity target - installation only, runtime acceptance pending

630Python(3skip)/314Node/Ruff/diff passed;35files frozen and atomically installed
over58 with151/protected options unchanged, one Core restart. New explicit
humidity Number facet reuses app6. Device/MQTT/browser/visual/performance and exact
cleanup remain pending; see humidifier-humidity-design-2026-10-31.md.


## HA60 humidity target / native45 unchanged - accepted scope

Receipt C:/aeh-build/feature-continuation-20261031-next/ha60-humidity-scoped-acceptance.json.630Python(3skip)/314Node/static/diff;35source files frozen/canonical/installed match. Real MQTT/native v3:5exact integer set_humidity/broker commands46/45/50/45/46 beforefeedback,0power/mode, feature0 then1+eco; current_humidity99 stays independent. Step5/offgrid46/max71-tail70 versus71/present-null step/real discovery fractional min30.5/None/ABA/outage/recovery/PLEN/endpoints pass.21native originals/contact and step50 original reviewed. Separate actual source60 browser v2 review/Confirm/2Undo/noSave/short hint; no forged v3 ACK. Final browser157 clean shows original cards and all saved. Exact fixture/topic/registry cleanup/token revoked/8prefs/faults[]. Post80frames/55sourceFPS/avg16310us/max23878us/failed0; PSRAM5640/largest2688/internal35/JPEG907/weather1792/control241/appwork-scroll-close0. Final Home original reviewed; ELF45 verified, no new native code/build/flash for HA59/60. Physical humidity actuator, panel FPS/input latency/audio and long duration not qualified. V1 readiness test error after correct revocation retained/clean153; V2 protected intrinsic MQTT min attribute ignored in JSON extras retained/clean155. V3 changes only fixture to real positive_float discovery; backend unchanged. HA60 removes generic slider hint and bumps asset cache; full final source retested.

## HA61 — efekty światła, native45, czysty układ161

640Python(3skip)/319Node/Ruff/diff przeszły;35plików zamrożonych HA61 są zgodne
z canonical i zainstalowanym komponentem. Jedna atomowa wymiana i restart Core
zachowały ustawienia. Nie ma nowego firmware ani ponownego flash dla HA61.
Pozostaje odebrany native45, pełnyELF c74f3f2172234acbfb96dfe45f154dcbb5f89d8700384997f50ca8ed988586d5.

Własne rzeczywiste MQTT JSON light:5light.turn_on(effect) i5dokładnych JSON
ON/effect odebrane przez broker przed feedbackiem. None przy off/on, zachowana
wewnętrzna nazwa przy off, Unicode ze spacjami, anulowanie, no-op, trzymany
przycisk przy A-B-A, off-list, zmiana kolejności,1/9/pusta lista przy sticky4,
outage/recovery oraz PL/EN przeszły. Brak barepower/koloru w poleceniach tej
onoff fixture.23oryginalne800x800/contact oraz końcowy Home przejrzane.

Pierwotne okno testu przeglądarki wygasło; wynik zachowany jako STAGE_ACK_TIMEOUT.
Oddzielna fixture na identycznym source61 dała rzeczywisty review z ostrzeżeniem
o możliwym włączeniu światła, Confirm,2Undo/noSave i czysty szkic. Nie przypisano
jej ACK do starego właściciela. Dokładne inverse159/161, brak fixture/retained
topic/registry, tokeny odwołane,8preferencji zachowane, faults[]. Finalny edytor
161 pokazuje Wdomu, Wilgotność6 i Światło7 oraz wyłączone Zapisz.

Normalna trasa:78klatek/53sourceFPS/avg16775us/max23948us/failed0, PSRAM5631KiB,
largest2688KiB/internal35KiB, JPEG915KiB/weather1792KiB/control241KiB;
app_work/scroll/close0. Jest to krótki porównywalny przebieg w dotychczasowym
zakresie53–55sourceFPS, nie pomiar fizycznego panelu, audio ani lifetime.
Żarówka fizyczna nie była podłączona. RGB i temperatura barwowa pozostają.
Receipt: C:/aeh-build/feature-continuation-20261031-next/ha61-effect-scoped-acceptance.json.

## HA62 — precyzyjna temperatura barwowa, native45/163

648Python(3skip)/323Node i8focused po uporządkowaniu importów passed. Ruff
E9/F63/F7/F82/diff passed; legacy I001 w3starych plikach jest osobną sprawą,
nowy test i number mają uporządkowane importy.35plików frozen62=canonical/live.
Jedna atomowa wymiana i restart zachowały161, po fixture dokładny inverse163.
Bez nowego native code/build/flash: nadal zweryfikowany native45.

Własna rzeczywista MQTT JSON light używa natywnego trybu Kelvin.5dokładnych
light.turn_on(color_temp_kelvin=int2701/2700/6535/2002/2701) i5broker JSON
ON/color_temp przedfeedback; bez brightness/rgb/effectfields. Przeszły off ze
zachowaną temperaturą,hs,None,ułamek,outside,range2001..6536,odrzucenie min999,
held mode A-B-A,outage/recovery,PL/EN,granice/no-op.22oryginały800x800/contact
i końcowy Home przejrzane. Rzeczywisty browser: review co1K/aktywnego trybu,
Confirm/2Undo/noSave, krótki poprawny hint, końcowy czysty163. Fixture/retained
topics/registry usunięte, token odwołany,8prefs zachowane/faults[]. Dane i opcje
poza monotonicznym revision zgodne z chronioną bazą95.

Normalna trasa79klatek/54sourceFPS/avg16501us/max26006us/failed0. PSRAM5642KiB,
largest1984/internal35,JPEG904/weather1792/control241;app_work/scroll/close0.
To ograniczony pomiar porównawczy. Fizyczna żarówka/panelFPS/audio/lifetime
nie są odebrane. Pierwszy zakres to precyzyjne1K, nie szeroki suwak ani RGB.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha62-kelvin-scoped-acceptance.json.

## HA63 — rzeczywiste biegi wentylatora, native45/169

657Python(3skip)/327Node/9focused po sortowaniu importów, Ruffcritical/diff
passed;35frozen=canonical/live. Jedna atomowa wymiana i restart zachowały163.
Bez nowego native code/build/flash; native45pozostaje zweryfikowany.

Rzeczywiste MQTT range1..3/1..7:6int fan.set_percentage66/100/0/42/100/33,
6fizycznych kodów brokera2/3/0/3/7/1 przedfeedback,0power/presetservices.
Przeszły0/100%,anulowanie/noop/heldABA,off z zachowanym procentem,None bez
inferencji0,zmiana count/off-list/8wierszy,count8/100 rejection,utratafeature,
outage z odrzuceniem nowego press i świeże otwarcie po recovery,PL/EN.
21oryginałów800x800/contact i kompletne Home/8wierszy przejrzane. Surowe piksele
potwierdzają header także tam, gdzie incremental preview pominął statyczną część.

V1 iV2 pozostają FAILED z prawidłowym cleanup165/167. V1 miał zły oracle
selectedTrue podczas outage, gdy Core usuwa percentage_step; poprawna polityka
unieważnia wybór. V2 błędnie wymagał przyjęcia dotknięcia unieważnionego widoku.
V3 potwierdza odrzucony press i brak dodatkowej usługi. Bez zmian kodu produktu
między próbami. Rzeczywisty browser proof63 zV1 pozostaje osobnym dowodem
review z ostrzeżeniem start/stop/Confirm/2Undo/noSave, bez nowego fikcyjnego ACK.
Finalny edytor czysty169, oryginalne Wdomu/Wilgotność6/Światło7. Fixture/topics/
registry usunięte, tokeny odwołane,8prefs zachowane/faults[], opcje poza revision
zgodne z chronioną bazą95.

Normalna trasa80klatek/54sourceFPS/avg16160us/max23706us/failed0; PSRAM5625KiB,
largest2688/internal35/JPEG921/weather1792/control241/app_work-scroll-close0.
Fizyczny silnik/panelFPS/audio/lifetime i katalogi większe niż7biegów pozostają.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha63-speed-scoped-acceptance.json.

## HA64 — docelowa wilgotność Climate, native45/171

664Python(3skip)/330Node/7focused/Ruffcritical/diff passed. Pierwsza pełna
próba miała jedno historyczne oczekiwanie, że climate humidity jest zabronione;
zastąpiono je zakazaną kontrolą current_humidity. Nowe dodatnie testy dotyczą
jawnego nowego kontraktu; v2przeszedł w całości.35frozen64=canonical/live,
atomowa wymiana/restart zachowały169. Bez nowego nativebuild/flash, nadal45.

Rzeczywista własna MQTT Climate:TARGET_HUMIDITY4 bez target-temperature1/2,
target45 vsmeasurement99.5exactintclimate.set_humidity46/45/50/45/46 i5broker
messages przedfeedback.0usług/pólHVAC/temperatury. Przeszłyauto/dry/off,
None/PLEN/endpoints/heldtargetABA,step5/None/offgrid,range71tail70 vs71,
discoveryfractionalmin30.5,utratafeature4,outage/recovery.23oryginały800x800/
contact/step50original oraz pełny postHome/rawheaders przejrzane. Rzeczywisty
browser ownerb57e9d1485be46efadcfec3314f32adb:review/Confirm/2Undo/noSave,
ownhint i końcowy czysty171. Dokładnyinverse,fixture/topics/registry usunięte,
token odwołany,8prefs/faults[],protected95hash unchanged.

Normalna trasa80klatek/55sourceFPS/avg16634us/max24756us/failed0;PSRAM5640KiB,
largest2176/internal35/JPEG906/weather1792/control241/work-scroll-close0.
FizycznyHVAC,pozostałe tryby pozaauto/dry/off,panelFPS/audio/lifetime pozostają
odrębnymi bramkami (pozostałe znane tryby mają testyhost). Dual-temperature
range i cross-unit nie są częścią tego adaptera.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha64-climate-humidity-scoped-acceptance.json.

## HA65 — wybór mocy odkurzacza, native45 / układ173

671 testów Python (3 pominięte), 333 Node, 7 focused, krytyczny Ruff i diff
przeszły. 35 plików frozen65 = canonical = HA. Atomowa instalacja i jeden
restart zachowały układ171. Firmware45 pozostał bez zmiany: brak nowego kodu
native, bufora, zadania, timera, subskrypcji czy protokołu; bez nowego flash.

Własny rzeczywisty MQTT vacuum: FAN_SPEED32, exact fan_speed_list1..8,
pięć vacuum.set_fan_speed i pięć surowych komunikatów przed feedback:
normal / ` Żółty ` / quiet / quiet / Power7. Zero start/stop/dock. Wszystkie
sześć aktywności, None/off-list/unknown, literalnone, katalogi1/8/9/empty,
reorder/featureloss/outage/recovery, cancel/noop/heldABA i PL/EN przeszły.
30 oryginałów800x800 i contact przejrzane, pełny Home po trasie potwierdzony.
Rzeczywisty browser owner b6eb4e0eda3440d9aa67ae98e0eff668:
review/Confirm/2Undo/noSave oraz końcowy czysty edytor173. Pierwszy actor
odrzucony przed przypisaniem przez nieobsługiwaną ikonę testową; jego fixture
i token usunięte. Drugi zmienia tylko testową ikonę, nie źródło65.

Dokładny inverse do173, fixture/topics/registry usunięte, token odwołany,
8 preferencji i chronione options poza rewizją zachowane, faults[].
Normalna trasa79 klatek/54sourceFPS/avg16385us/max23806us/failed0;
PSRAM5631KiB/largest2560/internal35/JPEG915/weather1792/control241,
app_work/scroll/close0. Fizyczny robot, panelFPS/input latency/audio/lifetime
pozostają odrębnymi bramkami. Mapy/pokoje/routines nie są częścią tego odbioru.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha65-vacuum-power-scoped-acceptance.json.

## HA66 — procent otwarcia rolety, native45 / układ175

677Python(3skip)/336Node/6focused/krytyczny Ruff/diff przeszły.35frozen66=
canonical=HA. Atomowa instalacja i restart zachowały173. Brak nowego kodu,
buforów, zadań, timera, subskrypcji czy protokołu native; bez nowego flash.
Jawny Number/propertyposition, SET_POSITION4 i current_position, zakres0..100
ze skokiem1. Pozycja nie pochodzi z tilt ani ze zgadywania open/closed.

Własna rzeczywista MQTT Cover:6integer usług cover.set_cover_position
46/45/99/1/46/46 przed feedback; broker46/45/99/1/46/54. Ostatnia54 wynika
z normalizacji odwróconego zakresu sterownika100closed/0open przez Core.
Zero open/close/stop/tilt. Przeszły początkowy brak pozycji, endpoints,
opening/closing, cancel/reopen, heldABA, featureloss, outage/recovery, PL/EN.
Niepoprawny payload None zachowuje poprzednią pozycję po stronie Core;
test potwierdza ten rzeczywisty stan, nie udaje uzyskania None.
22oryginały800x800/contact, pełny postHome i realny browser review/Confirm/
2Undo/noSave przejrzane. Ownercda0898a61674c399140b08b6424659d, końcowy
czysty175. Exactinverse/fixture/topics/registry/token/8prefs/faults[];
protected95 hash unchanged.

Normalna trasa79frames/54sourceFPS/avg16353us/max24063us/failed0;
PSRAM5636KiB/largest2688/internal35/JPEG911/weather1792/control241,
app_work/scroll/close0. Fizyczny silnik, rzeczywisty Stop, panelFPS/latency,
audio/lifetime, szeroki suwak i tilt pozostają osobno. Obserwacja pozycji
nie oznacza dowodu zatrzymania silnika.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha66-cover-position-scoped-acceptance.json.

## HA67 — pochylenie lameli, native45 / układ177

683Python(3skip)/339Node(v2)/6focused/krytyczny Ruff/diff przeszły. V1Node
miał skopiowane oczekiwanie Redo propertyposition; poprawiono test na rzeczywiste
tilt_position, bez zmian produktu między próbami.35frozen67=canonical=HA.
Atomowa instalacja i restart zachowały175. Brak nowego native kodu/bufora/
zadania/timera/subskrypcji/protokołu i brak nowego flash.

Rzeczywista własna MQTT Cover, feature128 bezposition4: początkowo tiltunknown,
potem tilt45 przy niezależnym current_position99.6integer usług
cover.set_cover_tilt_position46/45/99/1/46/46 przedfeedback; broker
46/45/99/1/46/54 przez Core normalizujący odwrócony tilt_min/max. Podniesienie
pozostało99; zero dodatkowych open/close/stop/primary position. Przeszły
endpoints, opening/closing, unknown cover state/recovery, invalidpayload Core
retained value, heldABA, close/reopen, feature128loss, outage, PL/EN.
24oryginały800x800/contact i pełny postHome przejrzane; świeży browser
owner19a31eead89445f1990c867b3550b0ac review/Confirm/2Undo/noSave i finalclean177.
Exactinverse/fixture/topics/registry/token/8prefs/faults[], protected95same.

Normalna trasa79frames/53sourceFPS/avg16482us/max23396us/failed0;
PSRAM5640KiB/largest2432/internal35/JPEG906/weather1792/control241/work0.
Wahanie53–55sourceFPS jest w dotychczasowym zakresie krótkich tras, bez
wnioskowania o fizycznym panelFPS. Fizyczny silnik, Stop tilt, latency/audio/
lifetime i szeroki suwak pozostają odrębnie.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha67-cover-tilt-scoped-acceptance.json.

## HA68 — jedno wydarzenie kalendarza, native45 / układ193

690Python(3skip)/343Node(v2)/7focused/krytyczny Ruff/diff przeszły;
35frozen68=canonical=HA. Pasywne CalendarEntity.event tylko w szerokim slot12,
publiczne pola Core w lokalnej strefie, timed/all-day, PL/EN, ograniczony zwykły
tekst40znaków i jawne skrócenie. Brak description/location/URL na ekranie,
nowych pollerów/buforów/zadań/protokołu/native kodu/flash.

Rzeczywisty własny LocalCalendar V3:13scenariuszy+Home=14oryginałów/contact,
empty/timed/all-day/active/PLEN/long/markup/offscreen update/missing404/recovery.
8zapisów wydarzenia wyłącznie we własnym fixture (create6update/delete), zero
usług od pasywnych tapów. Rzeczywisty browser readonly/caption/titleedit/close/
Undo/noSave; owner31b53f860b7b4bf38cfc6f71fed0220c. Final browser clean193,
Save disabled. Dokładny inverse wszystkich własnych pól slot12; pozostałe15kart,
3kamery/8prefs/protected95/data bez zmian. Niezależny SSH potwierdził brak
wszystkich7własnych Calendar wpisów i plikówICS. Tokeny revoked/faults[].

Zachowane nieudane próby: V1 niepotrzebny MQTT hook przed bindingiem; V2 błędne
nazwy pól WS start/end zamiast dtstart/dtend. V4/V5 błędnie czekały na snapshot
ukrytej strony; benchmark nie ruszył. Poprawiono wyłącznie harness: projekcja
przed nawigacją, rzeczywista nawigacja, capture fence dopiero na widocznej stronie.
V6/V7 przeszły. Nie zmieniano runtime/renderer ani nie wymuszano hidden render.
Nodev1 oracle skorygowano do istniejącej etykiety Offline. Core odrzucił request
DST z różnymi offsetami; preflight UTC/fold i test formatowania nie dowodzą
obsługi takiego requestu przez provider.

Wszystkie11tras i24oryginały performance zachowane. Pierwsze próby52/51FPS
(avg16957/16987us, max32481/30278us) spowodowały rzeczywiste A/B67→68:
53FPS/avg16704/max24079 oraz54FPS/avg16254/max23762. V6 aktywny52FPS vs
cleanup54FPS; wykonano więc przeplatane control/active/control/active z tym
samym załadowanym providerem bez zapisów wydarzenia podczas pomiarów.
Wyniki54/54/54/54sourceFPS, avg16380/16470/16700/16082us,
max24270/23749/28134/23815us, frames81/79/79/80. Postcleanup53FPS/79frames/
avg16759/max23645. Wszystkiefailed0/segments1. Nie ma utrwalonego spowolnienia
w dopasowanych próbach; przyczyna wcześniejszych okien51–52 pozostaje nieustalona.
Nie interpretować dwóch par jako efektu statystycznego/optymalizacji.

Control PSRAM5642KiB vs active5634KiB, largest3264/internal35 bez zmian.
JPEG905→915KiB wynika z bogatszej zawartości kadru i wraca po cleanup;
snapshot6530→6540KiB; weather1792/control241/work-scroll-close0. To nie jest
twierdzenie o zerowej zmianie pamięci ani fizycznym panelFPS/latency/audio/
long-run. Wszystkie oryginalne nagłówki Home i aktywny kalendarz kompletne.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha68-calendar-next-scoped-acceptance.json.

## HA70 — osoba, strefa i rzeczywista szerokość podpisu; native45 / układ209

Odebrano pasywną kartę Person: wynik Core home/not_home/custom zone, główne
tłumaczenia z HA (PL „w domu”/„poza domem”, EN Home/Away), brakujące PL/EN w
projekcie. Nazwa strefy zachowuje case/underscores po usunięciu markup.
Opcjonalny akcent wyłącznie dla dokładnego home; unknown/outage/pozostałe
stany mają surface. Katalog nie eksportuje account/source/tracker/GPS/photo.
Brak encji w edytorze pokazuje offline zamiast starego stanu katalogu.
Tylko szeroki slot12, sensor/actionnone i brak raw/legacy actuators.

699 testów Python (3 pominięte), 346 Node, w tym 16 istotnych Python (9 nowych),
krytyczny Ruff/diff przeszły. 36 frozen70 = canonical = HA. Dwie instalacje
69→70, każda atomowa/jeden restart, chronione options/data bez zmian. Native45
pozostał bez zmian: brak nowego kodu/bufora/zadania/protokołu i nowego flash.

V1 zatrzymało błędne wielkoliterowe oczekiwanie etykiety PL; zachowano pierwotne
tłumaczenie HA, cleanup195. V2 funkcje/browser/cleanup199 przeszły, lecz oryginał
W255 ujawnił rzeczywisty clipping; nie odebrano wizualnie. HA70 poprawia oba
podpisy Person/Calendar: pole wewnętrzne ma290px, mimo440px całego kafelka.
319 metryk rzeczywiście działającego Roboto16 odczytano z podpisanego hashami
native45 main.cpp. Fitter ogranicza advance/final ink extent do288px i40znaków,
rezerwując końcowe...; nie uruchamia fontów hosta. Zmiana fontu/geometrii wymaga
regeneracji. Dwa testy obejmują wszystkie319glyphów, szerokie W i znaki spoza
tabeli. V3 ruszył przed pełnym startem Core: unknown_command, bez fixture i
bindingu; token revoked. Po sprawdzeniu RUNNING wykonano V4.

Rzeczywista własna CorePerson z user_idNone i MQTTrouter trackerem, in_zones[]
zapobiega legacy dopisaniu współrzędnych domu. V4:17scenariuszy+Home =18oryginałów;
brak trackerów, home/away/strefy, W255 z widocznym..., markup, offscreen update,
outage→unknown, odpięcie/powrót trackera, PL/EN, brak encji/recovery. Pasywne
tapy bez usług. Browser owner07b1fb789a9c4f1ba83025a050106508: readonly/statecolor,
titleedit-close/Undo/noSave. Kalendarz V8:13scenariuszy+Home =14oryginałów, pełna
regresja timed/all-day/PLEN/empty/active/markup/offscreen/missing i szerokie W;
browser owner0d52e7dfc5fd4d87865d3583556ad3df również przeszedł. Kontakty i pełne
Home przejrzano, dot... mieści się w polu. Nie maskowano clippingu rendererem.

Własny Person performance fixture208 przetestowano bez zmian providera w czasie
pomiaru, sekwencyjnie: probe odłącza API, dopiero potem rzeczywista trasa dotyku,
potem osobny capture widocznej strony i cleanup209. Brak równoległych native
aktorów i wymuszania snapshotów ukrytej strony.

| Próba | Klatki | sourceFPS | Średnio µs | Max µs | Wolna PSRAM KiB | JPEG KiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ha70-person-calendar-width-post-performance | 79 | 53 | 16434 | 24645 | 5638 | 908 |
| ha70-active-person-performance | 79 | 53 | 16390 | 28230 | 5638 | 910 |
| ha70-post-active-person-performance | 79 | 53 | 16564 | 27909 | 5634 | 912 |

Wszystkie failed0/segments1, largest3264KiB/internal35KiB, raw Home5625KiB,
weather1792KiB/control241KiB i app_work/scroll/close0. Krótkie wyniki nie wskazują
na regresję względem poprzednich53–54FPS. PSRAM/JPEG różnią się o kilka KiB wraz
z rzeczywistą treścią stron; nie jest to dowód długiego braku wycieków ani
pomiar panelFPS/finger latency/audio. 7 dodatkowych oryginałów performance.

Dokładny inverse własnych pól slot12, końcowe209/16kart/3kamery/8prefs/protected95
i data bez zmian. Niezależny SSH potwierdził brak wszystkich5identyfikatorów
testowych Person (V3 nic nie tworzył), tracker registry, Calendarentry i ICS.
Tokeny revoked/faults[]; finalny edytor: Zaległa kopia, wszystkie zmiany zapisane,
Save disabled. Funkcje zdjęć/mapy i fizyczny tracking pozostają poza odbiorem.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha70-person-calendar-width-scoped-acceptance.json.

## HA73 — jawne akcje kosiarki; native45 / układ226

Odebrano wybór działania karty w edytorze: start_mowing (także wznowienie),
pause i dock. Przyciski zmieniają wyłącznie szkic/Undo; nowa karta actionnone.
Zastosowano istniejące negotiated press_enabled, bez nowego ekranu, native
kodu/bufora/tasku/protokołu/flash. Stan na karcie pochodzi z HA; brak
optymistycznego potwierdzania ruchu. Polityka ponownie sprawdzana w HA:
start=docked/paused; pause=mowing/returning; dock=mowing/paused. Błąd/outage/
unknown/brak features lub usługi/redundant movement blokują dotyk. Możliwości
konfiguracji pozostają oddzielone od bieżącej dostępności wykonania.

709Python(3skip)/350Node/10focused/krytyczny Ruff/diff przeszły;37frozen73=
canonical=HA. Instalacje71/72/73 atomowe, każda jeden restart, options/data
zachowane. Realny Core2026.7.1 posiada5stanów i3akcje; nie dodawano idle/stop
z nowszych dokumentów. Główne etykiety HA zachowane, częściowe generic PL
Error/Returning zastąpiono Błąd/Powrót. Specific entity translations wygrywają.

Zachowane błędy i poprawki: V1 rzeczywisty IntFlag w State.attributes odrzucony
przez exactint, brak poleceń/inverse211. Faktyczny CoreState proof potwierdza
typ LawnMowerEntityFeature (JSON7), po poprawce3możliwości, bool nadal odrzucony.
V2 harness ruszył przed RUNNING, bez fixture/bindingu. V3 zażądał capture podczas
heldinput; worker ma wtedy prawo odroczyć snapshot. Pressfalse już w projekcji;
po release cleanup215,2poprawne polecenia. HA73 poprawił też fastpath tłumaczeń
dla localepl takiego samego jak serwer. V4 miał race między nowym HAunknown
a starszym natywnym podpisem offline; cleanup219,2poprawne polecenia. V5 czeka
łącznie na caption/pressflag/revision/visiblecapture, podczas hold jedynie
obserwuje projekcję; nie osłabia touch/capture gates i nie wymusza hiddenrender.

V5 rzeczywista własna MQTTmower, optimisticfalse: dokładnie6usług i6komunikatów
brokera start_mowing/pause/start_mowing/dock/pause/dock. Każdy broker odczytany
PRZED feedbackiem; stan HA wciąż poprzedni, dopiero własny provider publikuje
nowy stan. Wznowienie, pauza w returning, returning→docked, featureloss/restore,
error/unknown/outage, redundant taps, held error→paused ABA, rzeczywisty drag
z karty i aktualizacja poza stroną przeszły. Brak dodatkowych komend od tych
gestów/stanów. PL/EN oraz poprawne Błąd/Powrót potwierdzone na urządzeniu.
25scenariuszy+Home =26oryginałów800x800/contact przejrzano, bez clippingu/
ghosthover i brakujących elementów. Polecenia dotyczą wyłącznie własnej encji.

Rzeczywisty browser ownerf41e6a4d29bf45759215eeab5c2617af: Pause wybrany gdy
docked, potem Dock i2Undo, bez Save. Po scrollu PRAWEGO panelu widoczne wszystkie
3przyciski i wybrana pause; po mutacji scroll resetował się, więc pełnostronicowy
screenshot bez scrollu nie wystarczał. Osobny viewport PNG zapisano i pokazano.
Finalny edytor226: W domu/Wilgotność/Światło1 w oryginalnych miejscach, allsaved,
Save disabled. Pierwszy zbyt szybki wybór zakładki podczas reload resetował się
po zakończeniu ładowania; po świeżym odczycie wybrano Sterowanie poprawnie.

Po cleanup standardowa rzeczywista trasa Home1→2→Settings→2→1:
78frames/53sourceFPS/avg16611us/max23918us/failed0/segments1. To pomiar tej
trasy, nie activeHome4FPS czy panelFPS. PSRAM5633KiB/largest3264/internal35,
JPEG911/rawHome5625/weather1792/control241/app_work-scroll-close0. Stałe native
bufory bez zmiany; różnice kilku KiB treści JPEG nie dowodzą lifetime ani
fizycznej latencji/audio.2postHome oryginały/nagłówki przejrzane.

Exact inverse wszystkich własnych pól slot15 do W domu; końcowe226/16kart/
3kamery/8prefs/protected95/data bez zmian. Wszystkie5testowych identyfikatorów
(V2 nic nie tworzył) niezależnie sprawdzono w registry i referencjach storage:
brak; discovery/topics usunięte przez actor, tokeny revoked/faults[]. Fizyczna
kosiarka i nowsze idle/stop pozostają poza odbiorem. Bez publikacji.
Receipt C:/aeh-build/feature-continuation-20261031-next/ha73-mower-actions-scoped-acceptance.json.
