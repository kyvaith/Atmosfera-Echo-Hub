# Plan funkcji Atmosfera Echo Hub — 2026-10-24

**Aktualny stan, 05.11.2026: native96 / HA118 / układ379.**
Dedykowane panele urządzeń, w tym Osoba i Słońce, opisuje
[aktualna mapa zakresu i braków](device-panels-roadmap-2026-11-04.md).
Następna nowa funkcja to edytor daty/czasu. Poprawka początkowego ładowania
podglądu w HA118 została odebrana. Szczegółowy punkt wznowienia:
[checkpoint](resume-2026-11-04-panels.md). Odbiory i wskazania „następnego
pakietu” poniżej są historyczne. Cały rejestr researchu nie jest zakończony.

**Odbiór 03.11.2026 native69 / HA97 / układ300.** Dedykowany termostat
pokazuje nastawę, odczyt, aktywność HVAC i pierścień zakresu w kolorze akcentu.
Regulacja korzysta z potwierdzonego kroku integracji. Podgląd działa także bez
zgodnego kontraktu edycji. Odbiór na urządzeniu obejmuje PL/EN, dwie nastawy
przez HA/MQTT i podgląd z blokadą przycisków. Histereza czeka na interfejs
providera. [Kontrakt i wyniki](thermostat-contract-2026-11-02.md).
Następny jest [podgląd dzwonka W15](doorbell-design-2026-11-01.md).

**Odbiór 02.11.2026 native49 / HA95 / układ298:** wdrożono górny baner,
centrum i historię powiadomień100/24h (8 wierszy, tap/detail, swipe/dismiss),
PL/EN i motyw oraz właściwe ikony robota/kosiarki. Typowane akcje i obrazy
pozostają w planie. [Odbiór i screenshoty](notifications-acceptance-2026-11-02.md).
Następny pakiet: [dedykowany termostat](thermostat-contract-2026-11-02.md).
Starsze aktualizacje poniżej są historyczne, nie określają bieżącego firmware.



**Aktualizacja 02.11.2026:** obowiązuje [kierunek rozwoju po uwagach użytkownika](priorities-2026-11-02.md).
Główne aplikacje to dedykowane Player i Kamera. Najbliższe pakiety: ikony i
powiadomienia/centrum od góry, termostat, dzwonek, dodatkowe strony. Opcjonalne
adaptery zewnętrznych mediów nie są główną ścieżką rozwoju. [Konkretna lista
wdrożonego zakresu i braków](status-2026-11-02.md). HA94 naprawia tylko Wi-Fi
w podglądzie; native46 i układ298 zachowane. Pełne pomiary grupujemy według
nowej polityki walidacji. Poniższe odbiory/historyczne plany pozostają dowodami
ich ściśle określonego zakresu.



**Odbiór 01.11: native46 / HA93 / układ298.** W14/MED003 otrzymał stały cel
głośności z kafelka, ustawiany procentowo w HA. Dokładne cele47,25%/0%/100%
przeszły przez publiczną usługę Core i własny MQTT; źródło nie zmieniało stanu
przed feedback. 33 scenariusze,36 oryginałów urządzenia, edytor procentów i trzy
Undo bez zapisu. 796 Python(3pominięte),397 Node,5 testów adaptera.
Trasa54 source FPS, średnio15989/max22739us, failed0 i DSI0; PSRAM3515KiB,
wewnętrzna23KiB, największy blok2560KiB, JPEG2090KiB, rawwork/scroll/close0.
Native46 bez zmian; brak nowej kompilacji/flash dla HA93. Zachowano16kart,
3kamery,8preferencji oraz dane/opcje; własne źródła testowe zarchiwizowano.
[Projekt i dowody](media-volume-target-design-2026-11-01.md). Pełny suwak na
urządzeniu pozostaje osobnym etapem; nie zmieniono kontraktu NumericDomain.
Fizyczny głośnik i panelowy FPS nie są objęte tym odbiorem. Bez commit/stage/push.



**Odbiór 01.11: native46 / HA92 / układ294.** W14/MED003 otrzymał Stop
odtwarzacza HA, dostępny podczas playing/paused/buffering. Trzy dokładne
polecenia Core/MQTT, bez optymistycznej zmiany stanu. 32 scenariusze i 35
oryginalnych zrzutów urządzenia; edytor, Undo, PL/EN, held ABA, przeciąganie,
stany nieaktywne i utrata obsługi przeszły. 791 Python (3 pominięte), 393 Node,
7 testów Stop. Trasa: 54 source FPS, średnio16744/max23770us, failed0 i DSI0.
PSRAM3507KiB, wewnętrzna23KiB, JPEG2099KiB, raw work/scroll/close0.
Brak nowego kodu natywnego, buforów i flash dla HA92; bieżący native46
wgrano wcześniej dla naprawy deferred tap. Zachowano16kart/3kamery/8preferencji
i chronione dane/opcje. [Projekt i dowody](media-stop-design-2026-11-01.md).
Fizyczne zatrzymanie głośnika pozostaje osobnym testem. W14 nadal częściowy.
Bez commit/stage/push.



**Odbiór01.11 native46/HA91/układ292.** W14/MED003: wybór trybu dźwięku
z rzeczywistego sound_mode_list,bit65536/select_sound_mode. Istniejący Choice/
app6/1..8nazw32UTF8b; bez nowych buforów/tasków/protokołu/nativeflash.
5exactstrusług+MQTT przedfeedback, w tymUnicode/spacje i długa nazwa; playback,
source,volume,mute,repeat,shuffle,title bez zmian.32case/35oryginałów800×800,
aktualny91browser/review/dwaUndo/noSave,cleanup39plików/16kart/3kamer/8prefs.
784Python(3skip)/389Node/7focused/criticalRuff/diff. Trasa54sourceFPS/avg16399/
max24821us/failed0/DSI0. PSRAM3501/internal23/largest2560KiB/JPEG2104,rawwork0;
free−6vs poprzedni media-check odpowiadaJPEG+5 i zaokrągleniu, stałe pule te same.
[Projekt i dowody](media-sound-mode-design-2026-11-01.md). Fizyczny amplituner/DSP
osobno; W14 nadal częściowy. Bez commit/stage/push.



**Odbiór01.11 native46/HA90/układ290.** W14/MED003: Głośniej/Ciszej z kafelka,
Core volume_up/down i rzeczywisty krok odtwarzacza, opis obserwowanego%.25case,
35oryginałów800×800,actual90browser/dwaUndo/noSave,2exactpublicactions+2Core
poziomy przedfeedback,cleanup39plików/16kart/3kamer/8prefs.777Python(3skip)/
385Node/6focusedVolume/3realLVGL+6codegen. Wykryto i naprawiono opóźniony
deferred tap po zmianie opisu podczas przytrzymania: raw generation przed
PRESSED,bez nowychbuforów/tasków/protokołu. Native46 zbudowany i wgrany1OTA.
Dwie trasy54sourceFPS vs54przed; średnio16673/16704us vs16256,failed0/DSI0.
Nie widać narastającej straty pamięci; zmienna fragmentacja sprawdzona także
rzeczywistą galerią i kamerą(60presentów/10.1presentFPS). Brak fizycznego
odsłuchu/GT911 i nowego odbioru audio/lifetime. [Projekt głośności](media-volume-actions-design-2026-11-01.md),
[poprawka dotyku](deferred-tap-context-design-2026-11-01.md). W14 nadal częściowy:
pełny suwak,seek,browse/favourites/detail pozostają planem. Bez commit/stage/push.



**Odbiór01.11 native45/HA89/układ283.** MED003/W14: jawne Losowo/Po kolei
z kafelka,shuffle_set bool/bit32768.2exact usługi Core/MQTT przedfeedback,
bez zmian playback/volume/mute/repeat/title.19przypadków/22oryginały,actual89
browser/requiredBool/dwaUndo/noSave/cleanup.771Python(3skip)/382Node/39plików.
Trasa54sourceFPS/avg16204/max23957us/failed0,PSRAM4892/internal27KiB/work0,
DSI0; nadal52–55. [Projekt i dowody](media-shuffle-design-2026-11-01.md).
W tej serii odebrano mute,source,repeat,shuffle i kompaktowe opisy. W14/MED003
nadal częściowy; fizyczne odtwarzanie muzyki osobno. Bez nativeflash/Gitpush.



**Odbiór01.11 native45/HA88/układ278.** Długie nazwy źródeł mają na Home
widoczne... w budżecie136px; HAeditor dzieli dokładnie ten caption. W Choice
i usłudze zachowano pełne nazwy.8przypadków/11oryginałów,1exact nieskrócona
komenda HDMI2-Salon-Telewizor przedfeedback, final88browser/review/twoUndo/
noSave/cleanup.763Python(3skip)/379Node/39zgodnych plików. Trasa53sourceFPS/
avg16298/max30282us/failed0,PSRAM4886/internal27KiB/work0,DSI0; nadal52–55.
[Zakres](media-source-design-2026-11-01.md). Aktualna seria dodała mute/unmute,
źródła i powtarzanie dla HAmedia_player. W14/MED003 pozostaje częściowy.
Bez nowego nativebuild/flash i bez commit/stage/push. Starsze wpisy niżej.



**Odbiór01.11 native45/HA87/układ276.** MED003/W14: powtarzanie off/one/all
przez istniejący Choice/Apply,bit262144, rzeczywisty CoreRepeatMode.4exact
usługi/MQTT przedfeedback; playback/track/volume/mute/shuffle bez zmian.
35przypadków/39oryginałów (w tym odrzucony stary opis86 i zaakceptowane87),
final87browser/review/dwaUndo/noSave, cleanup.762Python(3skip)/378Node/39plików.
Trasa53sourceFPS/avg16906/max24447us/failed0,PSRAM4884/internal27KiB/work0,
zgodna z52–55. [Projekt i granice](media-repeat-design-2026-11-01.md).
Skrócone opisy Home wPLEN mieszczą się w136px; długie tłumaczenia dostają...
Fizyczne zapętlenie muzyki/GT911 osobno; bez nativebuild/flash/publikacji Git.



**Odbiór01.11: native45/HA85/układ272.** MED003/W14: wybór źródła dowolnego
HA media_player przez istniejący Choice/Zastosuj;1..8różnych nazw/32UTF8b,
bit2048 i aktywny stan.5exact usług Core/MQTT przedfeedback,30ukończonych
przypadków/33oryginały800×800, rzeczywisty final85browser/review/dwaUndo/noSave,
niezależny cleanup.755Python(3skip)/374Node,39zgodnych plików. Trasa54sourceFPS/
avg16805/max23134us/failed0,PSRAM4880/internal27KiB/work0,DSI0. Zgodna z
poprzednim zakresem52–55. [Projekt i dowody](media-source-design-2026-11-01.md).
Fizyczny TV/HDMI/GT911 i większe listy osobno; bez nativebuild/flash/publikacji.
MED003 pozostaje częściowy: mute i source odebrane, bogatsze media dalej plan.



**Odbiór 01.11: native45 / HA83 / układ268.** MED003/W14: jawne Wycisz i
Przywróć dźwięk dla HA media_player, wymagany bool/bit8/świeży stan. Dwie
dokładne usługi Core/MQTT przed feedback, bez zmiany odtwarzania, utworu ani
głośności.19 przypadków/22 oryginały800×800, rzeczywisty browser/dwaUndo/noSave,
niezależny cleanup.749Python(3skip)/371Node,39 zgodnych plików. Trasa55 source
FPS/avg16575/max23453us/failed0, PSRAM4884/internal27 KiB, work0; zgodna z
poprzednim zakresem52–55. [Zakres i dowody](media-mute-design-2026-11-01.md).
Domyślne Play/Pause bez zmian; fizyczny głośnik/GT911 osobno. Bez native flash
i publikacji Git. Starsze wpisy poniżej.


**Odbiór 01.11: native45 / HA81 / układ263.** Wybór aktywności pilota przez
istniejący Choice i Zastosuj, również z off. Cztery dokładne komendy Core/MQTT
przed feedback, 25 przypadków/28 oryginałów, final browser/Undo/cleanup;
742 Python (3 skip), 368 Node, 39 zgodnych plików. Krótka trasa53 source FPS
(wcześniej52–55)/failed0, PSRAM4886/internal27 KiB, work0.
[Projekt i ograniczenia](remote-activity-design-2026-11-01.md). Fizyczny IR/RF,
keypad i duże katalogi osobno; bez nowego native flash lub publikacji Git.

**Odbiór 01.11: native45 / HA79 / układ259.** Jawne Włącz/Wyłącz dla
`remote.*`, bez domyślnego przełączania. Dwie dokładne komendy Core/MQTT przed
feedback, 14 scenariuszy native i 18 oryginałów, browser/Undo/cleanup. 735 Python
(3 skip), 365 Node, 39 zgodnych plików. Krótka trasa54 source FPS / failed0,
PSRAM4878/internal27 KiB. [Zakres i dowody](remote-power-design-2026-11-01.md).
Fizyczny IR/RF, aktywności i keypad osobno. Bez native flash i publikacji Git.

**Odbiór 01.11: native45 / HA77 / układ254.** Podgląd czasu trwania używa
kompaktowego formatu zgodnego z urządzeniem i precyzji HA. Brakujący zapisany
pokój jest jawnie niedostępny, bez automatycznej zamiany celu. 731 Python
(3 skip), 363 Node, 15 oryginałów, browser i cleanup; krótka trasa 54 source
FPS / failed0, PSRAM4878/internal27 KiB. [Dowody](duration-preview-design-2026-11-01.md).
Zmiana frontendu HA, bez nowego flash i bez publikacji Git. Starsze wpisy niżej.

**Najnowszy odbiór01.11: native45/HA76/układ246.** Sprzątanie jednego
rzeczywiście przypisanego obszaru HA na kafelek;3exact Core/MQTT commands,
24cases+Home25oryginałów/browser/cleanup. Registry-only mapping loss, heldABA,
drag i usunięcie pomieszczenia poprawnie blokują tap.39frozen=canonical=live,
729Python(3skip)/360Node. Siedem serii kontrola75:52–54FPS/mediana53,
76:53–55/mediana54,failed0; internal27both, zmianaPSRAM10KiB odpowiadaJPEG11KiB.
Wszystkie4fixtures/8obszarów usunięto; źródła76 i układ zachowane poA/B.
[Dowody i ograniczenia](validation-2026-11-01.md). Fizycznyrobot/GT911, wiele
obszarów naraz i mapy/routines osobno. Bez nowego firmware/commit/push.
Starsze aktualizacje poniżej.

**Najnowszy odbiór01.11: native45/HA75/układ236.** Jawne akcje odkurzacza:
start/wznowienie, pauza, stop, baza, locate i sprzątanie punktowe. 10exact usług
HA/MQTT przedfeedback,32scenariusze+Home33oryginały/browser/cleanup. Native45
bez zmian. Dopasowana trasa przed/po54sourceFPS/failed0, PSRAM4880→5610KiB,
internal32KiB, work0; różnicy pamięci nie przypisujemy jako optymalizacji.
719Python(3skip)/356Node,38frozen=canonical=installed. Fizyczny robot/GT911,
mapy/pokoje/routines osobno. [Dowody](validation-2026-11-01.md).
Bez commit/push. Starsze aktualizacje poniżej.

**Najnowszy odbiór31.10: native45/HA73/układ226.** Jawne akcje kosiarki:
start/wznowienie, pauza, powrót do bazy;6exactMQTTcommands przedfeedback,
26oryginałów/browser/cleanup. HeldABA, drag, error/outage/unknown i featureloss
bez dodatkowych komend. Standardowa trasa53sourceFPS/failed0,PSRAM5633KiB/
largest3264/internal35/work0; brak nowych native buforów i flash. Fizyczny robot
osobno. [Dowody](validation-2026-10-31.md). Bez commit/push. Starsze wpisy niżej.

**Najnowszy odbiór31.10: native45/HA70/układ209.** Pasywna osoba i nazwa
strefy, główne etykiety z HA, akcent tylko home;18oryginałów/browser. Poprawka
rzeczywistej szerokości Person i Calendar:319 metryk Roboto16/288px, widoczne...;
14oryginałów regresji kalendarza. Aktywna osoba i cleanup53sourceFPS/failed0,
7dodatkowychoryginałów; fixed native buffers bez zmian. Wszystkie dane testowe
usunięte, układ/prywatne ustawienia zachowane. Zdjęcia/mapa osobno.
[Dowody](validation-2026-10-31.md). Bez nowego flash/commit/push. Starsze wpisy niżej.

**Najnowszy odbiór31.10: native45/HA68/układ193.** Pasywne pojedyncze
wydarzenie CalendarEntity,14oryginałów+24performance/browser/cleanup. Dopasowane
control/active/control/active54sourceFPS,failed0; JPEG+10KiB/freePSRAM−8KiB
tylko przy bogatszym aktywnym kadrze, po cleanup wraca. Zachowano pierwsze
51–52FPS i pełne A/B, bez ukrywania słabszych prób. Agenda/booking osobno.
[Dowody](validation-2026-10-31.md). Bez nowego firmware i publikacji.
Starsze aktualizacje poniżej.

**Najnowszy odbiór31.10: native45/HA67/układ177.** Niezależne pochylenie
lameli128/co1%,6integercommands/0primary movement;24oryginały/browser/cleanup.
Odwrócony zakres i nieznany stan przeszły.53sourceFPS/failed0,PSRAM5640KiB/
internal35KiB/work0. Fizyczny silnik/szeroki suwak/Stop tilt osobno.
[Dowody](validation-2026-10-31.md). Bez nowego firmware i publikacji.
Starsze aktualizacje poniżej.

**Najnowszy odbiór31.10: native45/HA66/układ175.** Dokładny procent otwarcia
Cover0..100/co1%,6integercommands przedfeedback/0open-close-stop-tilt,
odwrócony zakres Core,22oryginały/browser/cleanup.54sourceFPS/failed0,
PSRAM5636KiB/internal35KiB/work0. Fizyczny silnik/szeroki suwak/tilt osobno.
[Dowody](validation-2026-10-31.md). Bez nowego firmware i publikacji.
Starsze aktualizacje poniżej.

**Najnowszy odbiór31.10: native45/HA65/układ173.** Wybór mocy odkurzacza:
FAN_SPEED32 i rzeczywisty katalog1..8,5exact commands przedfeedback/0start-dock,
30oryginałów/browser/cleanup.54sourceFPS/failed0,PSRAM5631KiB/internal35KiB,
work0. HA76 jeden przypisany obszar HA/card:3exact services/MQTT/25oryginałów/browser/cleanup246/mediana54sourceFPS. Fizyczny robot, wiele obszarów naraz, mapa i routines osobno. Bez nowego firmware.
[Dowody](validation-2026-10-31.md). Bez publikacji. Starsze aktualizacje poniżej.

**Najnowszy odbiór31.10: native45/HA64/układ171.** Docelowa wilgotność Climate:
TARGET_HUMIDITY4 bez temperature1/2,5intcommands/realMQTT/23oryginały/browser/
cleanup. Auto/dry/off,targetniepomiar,step/range/None/ABA/feature/outage passed.
Normalna trasa55sourceFPS/failed0,PSRAM5640KiB/internal35KiB,work0. FizycznyHVAC,
dual-temperature range i cross-unit nadal osobno. [Dowody](validation-2026-10-31.md).
Bez publikacji. Poniższe aktualizacje są historyczne.

**Najnowszy odbiór31.10: native45/HA63/układ169.** Wybór1..7rzeczywistych biegów
wentylatora plus0 korzysta z przeliczeńCore:6exactintcommands/realMQTTcodes,
21oryginałów/osobny realny browser/cleanup169. Outage unieważnia katalog bez
kroku; stary press odrzucony, recovery wymaga świeżego otwarcia. Normalna trasa
54sourceFPS/failed0,PSRAM5625KiB/internal35KiB,work0. Większe katalogi/scalar/
silnik fizyczny osobno. [Dowody](validation-2026-10-31.md). Bez publikacji.
Poniższe starsze aktualizacje są historyczne.

**Najnowszy odbiór31.10: native45/HA62/układ163.** Precyzyjne dostrajanie barwy
co1K: rzeczywiste min/max i aktualny color_temp,5exactintcommands przedfeedback,
22oryginały/realny edytor/cleanup. Off/innytryb/unknown nie udają temperatury.
Normalna trasa54sourceFPS/failed0,PSRAM5642KiB/internal35KiB,work0. Szeroki
suwak/RGB, fizyczna lampa i lifetime nadal osobno. Brak nowego firmware dlaHA62.
[Dowody](validation-2026-10-31.md). Bez publikacji. Starsze aktualizacje poniżej.

**Bieżący odbiór31.10: native45/HA61/układ161.** Native45 naprawia podpis
Number przy utracie wartości; pełny build/flash/ELF, obrazy i pomiar mają osobny
odbiór. HA60 docelowa wilgotność:5int commands/21oryginałów/browser/cleanup157.
HA61 efekty światła:5dokładnych efektów przedfeedback/23oryginały/osobny realny
browser/cleanup161. Brak nowych zadań/buforów/firmware dla obu adapterów.
Normalne trasy53–55sourceFPS/failed0,8preferencji i cały układ zachowane poza
rewizją. Fizyczne aktuatory, audio/lifetime i RGB/temperatura barwowa nadal osobno.
[Dowody i ograniczenia](validation-2026-10-31.md). Bez publikacji.
Poniższe starsze aktualizacje są historyczne.

Aktualny odebrany fragment 31 października: native40 / HA58 / rewizja149.
W10: pasywne daty sensorów i input_datetime (trzy tryby) z realnym źródłem,
PL/EN, obrazami, edytorem i cleanup. W06: preset wentylatora także z jawnego
None/manual, bez fikcyjnej opcji; oscylacja niezależna od zasilania. Realny MQTT,
negatywne przypadki, PL/EN, oryginały, browser Undo i cleanup są odebrane.
Kierunek HA47 jest odebrany; speed i fizyczny silnik pozostają otwarte.
Pojedyncza nastawa Climate HA50 i wybór trybu HVAC HA51 są odebrane. HA52
przywraca zgodny pastelowy podgląd po restarcieHA bez zmiany preferencji.
HA53: programy Climate,4polecenia przedfeedback,16oryginałów/browser,cleanup137.
HA54 nawiew i HA55 żaluzje32 są odebrane, cleanup139/141 i17oryginałów.
HA56 osobna oś512 odebrana, cleanup143/15oryginałów.
HA57 domena humidifier, power obu klas, feature0/PLEN/MQTT/browser/12oryginałów
cleanup147/54sourceFPS odebrane. HA58 mode: None/sticky-list guards,4commands/0powerHumidity,18oryginałów/browser/cleanup149.
Humidity i dual-range pozostają W07.
Post-feature53–54sourceFPS/failed0, średnio16,6ms; naprawiony wcześniej
dryf109px ma osobny odbiór dwóch segmentów. Wszystkie opcje HA zachowane poza
rewizją. [Dowody i granice](validation-2026-10-31.md). Bez publikacji na GitHub.

Status dokumentu: mapa zakresu i rozpoczętej implementacji P0. Rejestr obejmuje 108 rodzin funkcji; nie jest deklaracją ich wdrożenia. Bieżące dowody pierwszego fragmentu są w [rejestrze walidacji](ha-dashboard-2026-10-24.md). Porównanie i pochodzenie źródeł: [analiza trzech projektów](../research/project-comparison-2026-10-24.md).

**Konkretna kolejność wdrożenia:** [plan implementacji W00–W26](implementation-plan-2026-10-24.md) przypisuje wszystkie 108 ID do pakietów, plików właścicielskich, zależności, budżetów i kryteriów odbioru. Ten rejestr nadal przechowuje zakres/status, a plan wyjaśnia jak wykonać pracę.

## Punkt odniesienia i sposób aktualizacji

Opublikowany 2026-10-24 punkt odniesienia:

- produkt Atmosfera: [65683789d83ceb4510b202ce98979043c8f5e2f6](https://github.com/kyvaith/Atmosfera-Echo-Hub/commit/65683789d83ceb4510b202ce98979043c8f5e2f6);
- companion ESPHome: [41e735733078651443b7c0bf56ede4c94f7f5d25](https://github.com/kyvaith/esphome/commit/41e735733078651443b7c0bf56ede4c94f7f5d25).

Ich istniejące dowody runtime opisuje [validation.md](validation.md). Publikacja tego checkpointu nie potwierdza nowych funkcji edytora, nowych regulatorów ani przyszłych układów. Badania obcych projektów były odczytem źródeł, nie testem ich urządzeń.

Kolumna Baza dotyczy powyższego checkpointu i pozostaje historyczna: O — obecna funkcja; C — częściowy zakres; B — brak odpowiednika; HW — wymaga innej konfiguracji sprzętu. Stan źródłowy O nie oznacza osobnego testu sprzętowego każdego wariantu. Zależności HA/FW/host/model/usługa są jawne; model może być samodzielnie hostowany, więc nie każda funkcja AI wymaga chmury publicznej.

Kolumna Realizacja nowa jest bieżąca. Dopuszczalne wartości: plan, w toku, kod, testy HA/host, config, build, flash, runtime, visual, zaakceptowano lub odłożono. Wpis kod/build nie może automatycznie przejść na zaakceptowano. Przy zmianie statusu dopisać commit/source manifest, test/scenariusz, datę i ograniczenia w dzienniku na końcu. Nie zmieniać ani nie używać ponownie ID; podział funkcji wymaga nowych ID z odwołaniem do pierwotnego.

## Priorytety

| Etap | Efekt użytkowy | Główne ID | Granica ukończenia |
| --- | --- | --- | --- |
| P0 | Wizualna konfiguracja w HA, biblioteka encji, DnD, backup i przewidywalny zapis | CFG-001..009, CFG-011, CFG-020, UI-002/004 | Działa edytor i kontrakt; nie deklaruje nowych suwaków ani dowolnych stron |
| P1 | Rzeczywiste działania i regulatory zamiast informacyjnych atrap | CFG-010, CTL-001..013/017/020/029/031, MED-003, DEV-002 | Każda oferowana kontrolka ma działający HA action, feedback i dowód sprzętowy |
| P2 | Własne strony/podstrony i rozmiary w ograniczonych szablonach | CFG-012..018, CTL-030, DEV-013 | Admission control i rejestracja navigation; nadal trzy surowe sloty Home |
| P3 | Historia, prognoza, powiadomienia, kolejne domeny i polityka idle | pozostałe CTL/MED/SYS wg rejestru | Każdy kosztowny widok ma bounded lifetime oraz scenariusze współbieżności |
| P4 | Instalator, preview host/WASM, rozszerzenia, opcjonalny agent | CFG-019, DEV-003..011, część SYS/MED | Osobne produkty/protokoły z pochodzeniem i zależnościami |
| X | Bluetooth Classic, moduły, magnetyczne ekrany, Matter/Thread | HW-001..008 | Osobny scope sprzętu, nie opcja dodana do obecnego firmware |

Skróty w tabeli oznaczają pełne ID z prefiksem AEH-. Etapy są kolejnością zależności, a nie terminami kalendarzowymi. P0 i P1 można rozwijać w małych, niezależnych pionowych fragmentach; zakończenie P0 nie zamyka całego rejestru. Następny fragment ma osobny [plan regulatora jasności](p1-light-brightness-plan-2026-10-24.md), ze ścisłym budżetem renderowania, pamięci i korelacji poleceń. Jest częściowo wdrożony: v16 ma odbiór grafiki i pojedynczego dispatchu, lecz gotowość przycisków, stan/aktuator i pełny odbiór runtime pozostają otwarte; v18 wgrano i potwierdzono pełny działający ELF oraz Home1, lecz pięć zakończonych cykli nadal ujawniło błąd gotowości kontrolek. Osobny ograniczony odbiór Auto Home przeszedł; [dowody z 25 października](validation-2026-10-25.md) nie zamykają fizycznego dotyku, ruchu, audio ani pełnych pomiarów wydajności. Native19 jest zbudowany, zweryfikowany i wgrany, z potwierdzonym pełnym ELF i Home1. Pierwszy pilot zatrzymał się na niesklasyfikowanym raporcie; późniejsza nieudana próba wykazała odrzucenie callbacku kamery przez helper. Obie porażki pozostają zachowane. Poprawiony końcowy pilot przeszedł pięć par otwarcie/zamknięcie i wszystkie dziewięć stałych obserwacji gotowości kontrolek, z odbiorem oryginalnych obrazów i zerem jawnych wywołań On/Off/Toggle wybranej lampy w pełnym sparowanym obserwatorze HA przez 180 s. Ten pilot nie odebrał raportu kamery, więc nie dowodzi współbieżności filtra na urządzeniu. Stan/aktuator, fizyczny GT911, sustained drag, FPS/p95, audio i lifetime pozostają otwarte; nie zamyka to całego W03 ani P1.

## Pierwszy konkretny zakres: echo-hub-m3-v1

Profil jest decyzją produktu dla rozpoczętej po checkpointcie implementacji, a nie opisem już zwalidowanego rozszerzenia. Bazowy kontrakt miał 11 definicji, z 0 i 1 always_hidden. Pierwszy etap rozszerza rejestrację do 16 prekompilowanych slotów 0..15; nie tworzy nowych surowych framebufferów ani dowolnego drzewa LVGL. Pięć istniejących kart otrzymuje brakujące bindingi i rejestrację.

Profil zawiera home-1 Home i home-3 Apps jako strony tylko do podglądu. Edytowalne są home-2 Security i home-4 Controls. Prostokąty są w przestrzeni produktu 800×800 i pochodzą z bieżącego tiles_m3.yaml, nie są stałymi w komponencie reusable. Domyślny radius 200 jest ograniczany geometrią LVGL; wyjątki podano poniżej.

| Slot | Strona | Obiekt produktu | Prostokąt x,y,w,h | Stan |
| --- | --- | --- | --- | --- |
| 0 | zgodność legacy | Light | niewyświetlany | reserved, hidden, nieedytowalny |
| 1 | zgodność legacy | Climate | niewyświetlany | reserved, hidden, nieedytowalny |
| 2 | home-2 Security | tile_cover_button | 55,176,220,248 | edytowalny |
| 3 | home-2 Security | tile_lock_button | 290,176,220,248 | edytowalny; radius 72 |
| 4 | home-2 Security | tile_alarm_button | 525,176,220,248 | edytowalny |
| 5 | home-2 Security | tile_garage_button | 94,462,296,116 | edytowalny |
| 11 | home-2 Security | tile_door_window_button | 410,462,296,116 | nowa rejestracja istniejącego widżetu |
| 12 | home-2 Security | tile_presence_button | 180,606,440,76 | nowa rejestracja istniejącego widżetu |
| 6 | home-4 Controls | tile_fan_button | 60,168,210,190 | edytowalny |
| 7 | home-4 Controls | tile_fan_speed_button | 295,168,210,190 | edytowalny; radius 62 |
| 15 | home-4 Controls | tile_webhook_button | 530,168,210,190 | nowa rejestracja istniejącego widżetu |
| 8 | home-4 Controls | tile_switch_button | 58,392,216,116 | edytowalny |
| 9 | home-4 Controls | tile_scene_button | 292,392,216,116 | edytowalny |
| 10 | home-4 Controls | tile_trigger_button | 526,392,216,116 | edytowalny |
| 13 | home-4 Controls | tile_sensor_button | 112,548,276,112 | nowa rejestracja istniejącego widżetu |
| 14 | home-4 Controls | tile_clock_button | 412,548,276,112 | nowa rejestracja istniejącego widżetu |

Źródła bazowej geometrii i poola: [A-HOME] [A-POOL]. Zmiany slots 11..15 wymagają osobnych dowodów config/build/flash/runtime. Edytor pokazuje maskę fizycznego ekranu; nie udostępnia ukrytych kompatybilnych kart jako rzekomo widocznych.

Umowa pierwszego zakresu:

1. HA przechowuje wersjonowany dokument z trwałym card.id, profile=echo-hub-m3-v1, revision, kartami i typowanymi akcjami. Przesunięcie zmienia slot, nie tożsamość karty.
2. Profil, geometria i capabilities pochodzą z zaufanej definicji produktu, nie z klienta. Brak resize, custom_pages i nowych native_controls jest widoczny w capabilities.
3. Edytor może zamieniać/przenosić treść tylko między zarejestrowanymi edytowalnymi slotami. Sloty 0/1 pozostają hidden/reserved.
4. Native wire v1 pozostaje formatem prezentacji. Projekcja musi uwzględniać puste/ukryte wpisy dla nieprzypisanych slotów, aby stara karta nie została po ruchu.
5. configured action z brightness_pct lub temperature wysyłane po tap to ustalona akcja. Nie jest to dowód istnienia interaktywnego suwaka, color pickera czy panelu climate; te mają osobne ID i etap P1.
6. saved_revision oznacza trwały zapis HA. sent_revision dopiero zakończone wywołanie API. applied_revision pozostaje null do rzeczywistego hooka firmware; opcjonalne pole revision w JSON samo nie jest ACK prezentacji.
7. Stary raport dotyku zawiera tylko slot. Nowy, jawnie negocjowany raport zawiera slot/card.id/revision, a firmware unieważnia gest po zmianie kontekstu. Walidacja tego rozszerzenia jest osobna od testów starszego firmware i od rzeczywistego wykonania akcji HA.
8. Import jest atomowy i najpierw sprawdzany; początkowo tylko zgodny profil. Eksport pomija sekrety, HA entry/device IDs, runtime attributes i adresy tokenów kamer.
9. Native API, dotychczasowy debounce/deduplikacja/retry i autoryzacja administratora HA pozostają właścicielami istniejącego transportu. P0 nie wprowadza drugiego serwera konfiguracji na ESP32.

Dokładne nazwy komend WebSocket i wewnętrzne moduły są częścią wdrażanego kontraktu kodu; nie tworzyć osobnej, sprzecznej kopii schematu w dokumentacji.

## Rejestr funkcji

Dowody przy pozycjach prowadzą do wersji bazowych lub przypiętych źródeł porównawczych. Nie są automatycznie dowodem bieżącej implementacji.

### Konfiguracja i edytor

| ID | Funkcja | Baza | Zależności | Etap | Realizacja nowa | Warunek i dowód |
| --- | --- | --- | --- | --- | --- | --- |
| AEH-CFG-001 | Wersjonowany model kart, trwałe IDs i profil urządzenia | C | HA | P0 | testy HA/host | Migracja v1; IDs niezależne od slotu; profil z zaufanego źródła. [A-CARD] [T-PAGES] |
| AEH-CFG-002 | Biblioteka encji i możliwości HA | C | HA | P0 | częściowo: HA/host/browser | HA21: filtrowanie nazwy/domeny/obszaru przed limitem, możliwości z serwera; aktualne etykiety bez utraty fokusu i szkicu. Zmiana unknown→on→unavailable→usunięta potwierdzona w prawdziwym HA; zero usług i zapisów układu. Pełna macierz możliwości nadal ma osobne odbiory domen. [A-EDITOR] [T-CAT] [E-CARDS] [odbiór 30 października](validation-2026-10-30.md) |
| AEH-CFG-003 | Wizualny edytor rzeczywistego ekranu | B | HA | P0 | testy HA/host | Rozdzielczość, maska okręgu i istniejąca geometria, live state. [A-EDITOR] [E-LAYOUT] [T-PAGES] |
| AEH-CFG-004 | Przeciąganie i zamiana kart w istniejących slotach | B | HA | P0 | testy HA/host | Trwałe IDs; blokada reserved slots; jedna operacja undo. [A-POOL] [T-PAGES] |
| AEH-CFG-005 | Walidacja i podgląd przed zastosowaniem | B | HA | P0 | testy HA/host | Cały dokument i zgodność profilu; brak częściowych zapisów. [T-STORE] [E-STORE] |
| AEH-CFG-006 | Rewizje i konflikty wielu edytorów | B | HA | P0 | testy HA/host | expected_revision; konflikt nie nadpisuje nowszej pracy. [A-PANEL] [T-STORE] |
| AEH-CFG-007 | Eksport/import i odtwarzanie konfiguracji | B | HA | P0 | testy HA/host | Wersjonowany backup bez kluczy/tokenów; dry run i atomowy import. [E-SYSTEM] [T-STORE] |
| AEH-CFG-008 | Undo/redo | B | HA | P0 | rzeczywisty HA/browser i host | Jedno Undo cofa pełne przeniesienie; dev8 potwierdza również Ponów i poprawne komunikaty PL, bez zmiany zapisanego układu. [T-PAGES] |
| AEH-CFG-009 | Typowane akcje i walidowane parametry usług | C | HA | P0 | testy HA/host | Rejestr pól/ranges/options; walidacja przy zapisie i tap. [A-CARD] [E-CARDS] [T-CAT] |
| AEH-CFG-010 | Rozdzielone saved/sent/applied i potwierdzenie firmware | C | HA+FW | P1 | częściowo: host/browser | UI pokazuje odebraną rewizję i gotowość snapshotów, starszy kontekst/offline/unknown; physical applied nadal null. [A-PANEL] [A-HA] [T-DELIVERY] |
| AEH-CFG-011 | Szkice i odzyskanie pracy po przeładowaniu | B | HA | P0 | testy HA/host | Draft oddzielony od opublikowanego układu; wykrywanie konfliktu. [T-STORE] |
| AEH-CFG-012 | Multiwybór, copy/cut/paste i przenoszenie między ekranami | B | HA | P2 | częściowo: rzeczywisty HA/browser | Dev9: grupowe Pokaż/Ukryj/Usuń; dev10: kopiowanie grupy z mapą miejsc i poprawiony kontrast. Dev11: Cut/Move, zamiana zajętych miejsc i między stronami, jedno Undo, no-op bez historii, odmowa po zmianie źródła, poprawny podgląd/fokus i clean Reload w rzeczywistym HA. Dev12: modal do 14 kart/5 semantycznych palet, pełny CAS, zmiana samej palety w jednym Undo i no-op bez historii; Cancel/Escape/Tab oraz osiem oryginałów odebrane w HA. 200 Node/250 HA shim; bez Save i zmian FW/backendu. Import grupy i wiele urządzeń pozostają planem; urządzenie i telefon wymagają osobnego odbioru. [E-LAYOUT] [T-PAGES] |
| AEH-CFG-013 | Wiele ekranów i identyfikacja urządzenia | C | HA | P2 | częściowo: rzeczywisty HA/browser | dev6: wybór ekranu, profil i zapisane w rejestrze HA nazwa/producent/model/wersja, z jawnym stanem offline; bez potwierdzania aktualnego firmware. Fizyczne identify i test wielu urządzeń pozostają planem. [A-EDITOR] [T-BUILD] |
| AEH-CFG-014 | Dodawanie, kolejność i ukrywanie stron runtime | B | HA+FW | P2 | plan | Rejestracja bounded templates; trzy raw sloty Home pozostają. [A-NAV] [T-PAGES] |
| AEH-CFG-015 | Rozmiary kart, siatka, resize i kontrola kolizji | B | HA+FW | P2 | plan | Tylko wspierane geometrie; budżet przed przyjęciem układu. [E-LAYOUT] [T-PAGES] [T-MEM] |
| AEH-CFG-016 | Home, detail, Back i agregacja skrótu podstrony | C | HA+FW | P2 | plan | Obecny More to skompilowana karuzela; potrzebne stabilne page IDs. [A-HOME] [E-SUB] [T-PAGES] |
| AEH-CFG-017 | Edytowalny pasek strony: zegar, encje, łączność | C | HA+FW | P2 | plan | Mały bounded zestaw elementów; poprawne invalidation. [A-HOME] [T-PAGES] |
| AEH-CFG-018 | Zdalna nawigacja do strony/karty/modala | C | HA+FW | P2 | plan | Jawne cele i lifecycle; brak emulowania animacji w lambdzie. [A-NAV] [E-SUB] |
| AEH-CFG-019 | Migracja backupu między profilami/rozdzielczościami | B | HA+FW | P4 | plan | Raport kompatybilności; żadnego cichego obcinania kart. [T-PAGES] [E-SYSTEM] |
| AEH-CFG-020 | Spójna strona ustawień i widoczny stan konfiguracji | C | HA | P0 | częściowo: host/browser | Zwijany profil pokazuje geometrię, sloty/strony i ograniczenia definicji HA; nie udaje wykrycia możliwości firmware. [A-SET] [A-OTA] |

### Rzeczywiste funkcje kart i encji

| ID | Funkcja | Baza | Zależności | Etap | Realizacja nowa | Warunek i dowód |
| --- | --- | --- | --- | --- | --- | --- |
| AEH-CTL-001 | Switch/light/input_boolean i wizualny stan aktywny | C | HA+FW | P1 | częściowo: HA/runtime/visual/browser | HA24/native31: opcjonalny kolor dla dokładnego on, surface dla off/braku źródła; istniejące role i kontrast. Własny Boolean off→on→off, zmiana poza ekranem i powrót, zgodne konteksty HA, obrazy oraz czysty układ 26. 54 FPS, pamięć przed/po bez spadku w badanym cyklu. Pełne pending/error/result, fizyczny aktuator/audio/lifetime pozostają otwarte. [A-CARD] [E-CARDS] [odbiór](validation-2026-10-30-continuation.md) |
| AEH-CTL-002 | Scene/script/button/input_button jako wykonanie | C | HA+FW | P0 | częściowo: availability/runtime/visual | HA18/native26: shared availability obejmuje button/scene/script; Scene disabled/held bez akcji, nowy tap wywołuje1Scene i faktyczne off→on wirtualnego przełącznika; oryginały i cleanup do14 PASS. Input_button ma wcześniejszy odbiór native24. Dwa Settings31sourceFPS/failed0; mixed CPU windows bez kontrolowanego porównania. Pending/error/result całej rodziny, fizyczny dotyk/aktuator i lifetime nadal otwarte. [A-CARD] [T-CAT] [walidacja](validation-2026-10-26.md) |
| AEH-CTL-003 | Regulator jasności światła | B | HA+FW | P1 | częściowo: runtime/visual | Native21: Power i pięć cykli/NoOp PASS. Native23: izolowany test Off/On/jasność60 ma trzy state_matches, dokładnie trzy usługi/stany HA i oryginały PASS. Nie jest to odbiór fizycznej lampy; brak lampy potwierdził użytkownik. Pozostałe bramki: [walidacja](validation-2026-10-25.md). [A-POOL] [E-CARDS] [T-CAT] |
| AEH-CTL-004 | Temperatura barwowa, RGB i efekty światła | B | HA+FW | P1 | częściowo: efekty i precyzyjne Kelvin HA/runtime/visual/browser | HA62 precyzyjne1K/on-color_temp,5intcommands/22oryginały/browser/cleanup163/54sourceFPS/failed0; szeroki suwak iRGB pozostają. HA61/native45:5effect commands przedfeedback, None/off/ABA/list/outage/PLEN,23oryginały i osobny rzeczywisty edytor;cleanup161/53sourceFPS/failed0. RGB i szeroki picker barwy nadal plan. [Projekt i odbiór](light-effects-design-2026-10-31.md). [E-CARDS] [T-CAT] |
| AEH-CTL-005 | Cover/garage/gate: open/close/stop/position | C | HA+FW | P1 | częściowo: HA/runtime/visual/browser | HA66 dokładna pozycja0..100/co1%,6integercommands/realMQTT/odwrócony zakres/22oryginały/browser/cleanup175/54sourceFPS/failed0. Istniejący Cover open/close/stop ma osobny kontrakt; HA67 niezależne lamele128:6integercommands/current_position99bez zmian/24oryginały/browser/cleanup177/53sourceFPS/failed0. Fizyczny silnik, szeroki suwak i Stop tilt osobno. [Projekt i odbiór](cover-position-design-2026-10-31.md). [A-CARD] [E-CARDS] |
| AEH-CTL-006 | Cover tilt i ustawienia pozycji lameli | B | HA+FW | P1 | plan | Niezależny capability i zakres; brak fikcyjnej wartości unknown. [T-CAT] [E-CARDS] |
| AEH-CTL-007 | Fan: speed/direction/oscillate/preset | C | HA+FW | P1 | częściowo: HA/runtime/visual/browser | Preset z manual/None,oscylacja,kierunek odebrane wcześniej. HA63 wybór1..7rzeczywistych biegów plus0:6intcommands/realMQTT/21oryginałów/browser/cleanup169/54sourceFPS/failed0. Większe katalogi,scalar i fizyczny silnik pozostają. [Projekt i odbiór](fan-speed-design-2026-10-31.md). |
| AEH-CTL-008 | Climate: setpoint/range/HVAC/fan/swing/preset | C | HA+FW | P1 | częściowo: HA/runtime/visual/browser | HA50: pojedyncza nastawa przez dokładny Number/app6,0.5°C, endpoints/unknown/offgrid/mode/step/unit guards, realne MQTT bez polecenia HVAC. HA51: jawny choice trybu heat/auto/cool/off, etykiety zHA,4brokercommands bez targetcommand, list/ABA/outage/PL/EN. Oryginały/browser/cleanup135 i54sourceFPS/failed0. HA53: programy none/eco/comfort/sleep,4brokercommands/0osobnychHVACtarget,16oryginałów/browser/cleanup137/53sourceFPS. HA54 fan_mode i HA55 swing_mode32: realne MQTT/oryginały/browser/cleanup139/141. HA56 independent512 odebrane MQTT/browser/15oryginałów/cleanup143/54sourceFPS. HA57 humidifier/dehumidifier power: real MQTT feature0/4power commands/0modeTarget/12originals/browser/cleanup147/54sourceFPS. Cross-unit/range/auto target, HA58 humidifier mode odebrane MQTT/None/sticky-list/18originals/browser/cleanup149. HA64 Climate humidity:5intcommands/23oryginały/browser/auto-dry-off/step-range-None-ABA-feature-outage/cleanup171/55sourceFPS/failed0. HA60 humidifier humidity odebrane w CTL-016; fizyczne urządzenia pozostają. HA52 zamyka osobny błąd podglądu akcentu. [Nastawa](climate-temperature-design-2026-10-31.md), [tryb](climate-hvac-choice-design-2026-10-31.md), [odbiór](validation-2026-10-31.md). |
| AEH-CTL-009 | Number/input_number: slider/stepper | C | HA+FW | P1 | częściowo: runtime/visual/browser | HA34/native35: input_number oraz encje number urządzeń we wspólnym stepperze. Rzeczywiste30→35→30, dwa polecenia i potwierdzenia HA/native; held ABA bez komendy, cztery warm-open i browser/Undo PASS. Odtworzone16 kart/rev79, parametr30,3 kamery i8 preferencji. Warm PSRAM6359–6362KiB/largest3776KiB, Settings53FPS/failed0. Physical/audio/lifetime nadal otwarte. [A-CARD] [T-CAT] [odbiór](validation-2026-10-30-continuation.md) |
| AEH-CTL-010 | Select/input_select: wybór opcji | B | HA+FW | P1 | częściowo: runtime/visual/browser | HA31/native35: 1..8 pełnych opcji po32 bajty, lokalny wybór i jawne Apply we wspólnym app6. Input_select: pięć komend/stany, unknown/ABA/list-held, 1/8/9 opcji i brak glyph; select: rzeczywiste PL→EN→PL urządzenia. Obrazy, panel/Undo, cleanup do58 i ciepła pamięć PASS; Settings54/55FPS/failed0. Większe listy/paginacja, physical/audio/lifetime pozostają otwarte. [T-CAT] [E-CARDS] [kontrakt i odbiór](choice-selection-design-2026-10-30.md) |
| AEH-CTL-011 | Timer: countdown/start/pause/resume/cancel | B | HA+FW | P1 | częściowo: runtime/visual/browser | HA19: domyślne Start/Pauza/Wznów bez resetu przy resume. HA22/native31: konfigurowalny czas 1–86400 s, preset 90 s, wznowienie 88 s i jawne Anuluj potwierdzone dokładnymi zdarzeniami HA oraz obrazami; formularz PL i czysty szkic sprawdzone w przeglądarce. Przywrócone 16 kart, rewizja 22, brak pomocników QA. Normalne wejście do Ustawień 54 FPS, failed=0. Lokalny countdown, wspólny detail i pełne wyniki komend pozostają planem; physical/audio/lifetime nieprzyjęte. [T-CAT] [E-CARDS] [bieżący dziennik](validation-2026-10-30.md) |
| AEH-CTL-012 | Lock: confirm/lock_only/code i stan unknown | C | HA+FW | P1 | plan | Obecne lock/unlock bez confirm; jawna polityka i keypad jeśli wymagany. [A-CARD] [T-CAT] |
| AEH-CTL-013 | Alarm: tryby, disarm, PIN i pending/triggered | C | HA+FW | P1 | plan | Istnieje prezentacja; wymagane osobne dozwolone akcje i code flow. [A-CARD] [T-CAT] [E-CARDS] |
| AEH-CTL-014 | Vacuum: akcje, pokoje/routines i mapa | B | HA+FW+integracja | P3 | częściowo: HA/runtime/visual/browser | HA65 moc ssania; HA75 sześć jawnych akcji; HA76 jeden rzeczywiście zmapowany obszar HA na kafelek,3 exact Core/MQTT commands przed feedback,25 oryginałów/browser/registry-only mapping loss/ABA/drag/cleanup246. Fizyczny robot,wiele obszarów naraz,mapy i routines osobno. [Akcje](vacuum-actions-design-2026-11-01.md),[pokój](vacuum-area-design-2026-11-01.md). [T-VACUUM] |
| AEH-CTL-015 | Lawn mower: start/dock/pause/resume | B | HA+FW+integracja | P3 | częściowo: HA/runtime/visual/browser | HA73 jawne3akcje/negotiated press,6exactMQTTcommands przedfeedback/26oryginałów/browser/heldABA-drag-outage-featureloss/cleanup226. Standardowa trasa53sourceFPS/failed0. Fizyczna kosiarka i nowsze idle/stop osobno. [Odbiór](mower-actions-design-2026-10-31.md). [E-CARDS] |
| AEH-CTL-016 | Humidifier: setpoint/mode/toggle | B | HA+FW | P3 | częściowo: HA/runtime/visual/browser | HA57 power i HA58 mode; HA60/native45: dokładna docelowa wilgotność, min/max/step/None/off-grid/ABA/range/outage,5int broker commands przedfeedback bez power/mode.21oryginałów, rzeczywisty edytor/Undo,cleanup157/8prefs i55sourceFPS/failed0. Fizyczny aktuator i lifetime pozostają. [Projekt i odbiór](humidifier-humidity-design-2026-10-31.md). [T-CAT] |
| AEH-CTL-017 | Sensor: precision/unit/duration/state mapping | C | HA+FW | P1 | częściowo: HA/runtime/visual/browser | HA25 precyzja0..6; HA35 do8 dokładnych opisów stanów. HA77/native45: podgląd duration zgodny z istniejącym native,203 shared cases/PLEN,7 dodatnich przypadków native+outage,4 browser proofs z prawdziwą precyzją HA,cleanup254/54 source FPS. Native formatter nie został dodany na nowo. Fizyczne sensory,audio,lifetime i mierniki osobno. [Duration](duration-preview-design-2026-11-01.md),[wcześniejszy odbiór](validation-2026-10-30-continuation.md). |
| AEH-CTL-018 | Historia: wykres liczbowy i timeline stanów | B | HA+FW | P3 | plan | HA agreguje bounded samples; limit retained/peak pamięci. [T-CAT] |
| AEH-CTL-019 | Mierniki ring/tape/bars | B | HA+FW | P3 | plan | Własne widgety M3 i cadence; brak porównania wydajności z obcym rendererem. [T-CAT] |
| AEH-CTL-020 | Door/window/presence: dedykowane stany i ikony | C | HA+FW | P1 | częściowo: HA/runtime/visual/browser | HA26/native31: opcjonalne lit-when-on i ikona według klasy, istniejące fonty; dziewięć scenariuszy, unknown/unavailable, zmiana poza ekranem i dwa tapy bez usług. Przywrócone 16 kart przy rewizji 34; 55 FPS, pamięć bez spadku w cyklu. Osobne ikony open/closed i fizyczny czujnik pozostają otwarte. [A-CARD] [E-CARDS] [odbiór](validation-2026-10-30-continuation.md) |
| AEH-CTL-021 | Calendar: agenda/day/week/month/booking | B | HA+FW+integracja | P3 | częściowo: HA/runtime/visual/browser | HA68 jedno CalendarEntity.event/slot12/timed-all-day/PLEN/14oryginałów/browser/cleanup193; HA70 pixel-fit290px/319glyphów i14nowychoryginałów/browser/cleanup207; dopasowane54sourceFPS/failed0. Agenda/day/week/month i booking pozostają otwarte. [Odbiór](calendar-next-design-2026-10-31.md). [T-CALENDAR] |
| AEH-CTL-022 | Person/map/zones/photos | B | HA+FW+mapy | P3 | częściowo: HA/runtime/visual/browser | HA70 pasywna osoba/home-away-zone/PLEN/exact-home accent,18oryginałów/browser/cleanup209; aktywna karta i cleanup53sourceFPS/failed0. Bez GPS/account/photo. Zdjęcia, mapa i fizyczny tracking osobno. [Odbiór](person-presence-design-2026-10-31.md). [T-MAP] |
| AEH-CTL-023 | Sun: ścieżka słońca i karta stanu | B | HA+FW | P3 | częściowo: HA/runtime/visual | HA20/native31: pięć poprawnych podpisów PL na urządzeniu, brak/błędne/niedostępne dane, data po północy, oryginalne obrazy i przywrócenie oryginalnych kart przy rewizji 18. Ustawienia 54 FPS, bez nowego bufora. PL/EN i DST hostowo; wykres ścieżki pozostaje planem. [T-CAT] [odbiór 30 października](validation-2026-10-30.md) |
| AEH-CTL-024 | Remote: activity/power/command keypad | B | HA+FW+integracja | P3 | częściowo: HA/runtime/visual/browser | HA79: jawne power,2 exact commands/18 oryginałów/cleanup259. HA81/native45: Choice aktywności1..8/32 bajty,off→Apply i on→inna aktywność,4 exact Core/MQTT commands przed feedback,25 przypadków/28 oryginałów/final browser/cleanup263;53 source FPS/failed0. Własna Core RemoteEntity bez nadajnika; fizyczny IR/RF,keypad i większe katalogi osobno. [Power](remote-power-design-2026-11-01.md), [aktywności](remote-activity-design-2026-11-01.md). [T-CAT] |
| AEH-CTL-025 | Energy: przepływy i agregacje | B | HA+FW | P3 | plan | HA liczy dane; osobny budżet animacji i punktów. [T-ENERGY] |
| AEH-CTL-026 | Lokalne sensory/akcje ESPHome z katalogiem | C | FW+profil | P3 | plan | Skompilowane callbacki są; brak użytkowego katalogu i mapowania. [A-HOME] [E-CARDS] |
| AEH-CTL-027 | Webhook/HTTP action z parametrami | C | HA+usługa | P3 | plan | Obecny Webhook to stały skrypt HA; konfiguracja wykonania po stronie HA. [A-HOME] [E-CARDS] |
| AEH-CTL-028 | Guest Wi-Fi/QR i ewentualny przełącznik sieci | B | HA+dane | P3 | plan | Oddzielić sekrety od backupu; nie wymagać zapisu HA tokenu na ESP. [E-CARDS] |
| AEH-CTL-029 | Automation: enable/disable/run | B | HA | P1 | częściowo: runtime/visual/browser | HA27/native31: domyślne enable/disable bez zatrzymywania trwającej sekwencji; jawne Run/Stop z parametrami warunków. Osiem dokładnych usług i rzeczywiste wykonanie izolowanej sekwencji, 11 obrazów, panel PL/Undo, cleanup do 16 kart/rev42. 54 FPS, pamięć bez spadku w cyklu. Pełny wynik/pending oraz fizyczne wejście/lifetime nadal otwarte. [T-CAT] [E-CARDS] [odbiór](validation-2026-10-30-continuation.md) |
| AEH-CTL-030 | Osobna encja stanu skrótu i aktywność potomków | B | HA+FW | P2 | plan | Oddzielić presentation od action target; bounded subskrypcje. [E-SUB] [E-CARDS] |
| AEH-CTL-031 | Bezstanowy trigger/zdarzenie do automatyzacji HA | C | HA+FW | P1 | częściowo: runtime/visual/browser | HA33/native35: jawne Action/event, odkrywalna encja Event, prywatny callback i aktualny kontekst. Sześć tapów/zdarzeń i zmian izolowanego helpera; drag/held/rename/hide/rebind/move bez fałszywych akcji. Stała tożsamość po zapisanym przeniesieniu15→13, browser/create/Undo, oryginały i cleanup do73. 54FPS/failed0, brak nowych buforów lub workerów. Physical/audio/lifetime otwarte. [A-HA] [E-CARDS] [odbiór](validation-2026-10-30-continuation.md) |

### Wzornictwo, dostępność i język

| ID | Funkcja | Baza | Zależności | Etap | Realizacja nowa | Warunek i dowód |
| --- | --- | --- | --- | --- | --- | --- |
| AEH-UI-001 | Zachowanie obecnej kompozycji Material 3 / Wear OS | O | projekt+FW | utrzymać | baza; zachować | Układ grup, hierarchia, typografia i bezpieczny obszar okrągłego panelu. [A-DESIGN] [A-HOME] |
| AEH-UI-002 | Material Design 3 Expressive dla nowych funkcji | C | projekt+FW | P0 | w toku | Spójne komponenty/tokeny/motion; nie deklarować ukończonego audytu Expressive. [A-DESIGN] [M3] |
| AEH-UI-003 | Role kolorów, kontrast i stany pressed/pending/error | C | HA+FW | P1 | plan | Akcent i role są; pokryć każdy nowy widget i snapshot. [A-CARD] [A-POOL] [E-APPEAR] |
| AEH-UI-004 | Lokalizacja en/pl i język edytora | C | HA+FW | P0 | testy HA/host | Firmware i stan HA już en/pl; formularz JS wymaga lokalizacji. [A-SET] [A-EDITOR] |
| AEH-UI-005 | Light/dark/manual/solar theme | B | HA+FW | P3 | plan | Jedna polityka motywu; invalidation całej zmienionej bazy. [E-APPEAR] |
| AEH-UI-006 | Szerszy dobór ikon/fontów i appearance per karta | C | HA+FW | P2 | częściowo: rzeczywisty HA/browser | Dev12 grupowo stosuje jedną z pięciu istniejących semantycznych palet; bez nowych kolorów/fontów/ikon ani zmiany autorytetu motywu. Szerszy zestaw i glyph/font budget pozostają planem. [A-CARD] [A-DESIGN] |
| AEH-UI-007 | Zegar: data, 12/24h, wiele stref i warianty | C | HA+FW | P3 | plan | Natywny zegar istnieje; warianty digital/analog/dial/flip oraz formaty/strefy wymagają osobnej konfiguracji i budżetu renderowania. [A-HOME] [E-CARDS] [T-CAT] |

### Media, obrazy, pogoda i powiadomienia

| ID | Funkcja | Baza | Zależności | Etap | Realizacja nowa | Warunek i dowód |
| --- | --- | --- | --- | --- | --- | --- |
| AEH-MED-001 | Natywny Player/Sendspin, artwork, kolejka | O | HA+FW | utrzymać | baza; zachować | Nie zastępować wypracowanego audio/display lifecycle. [A-PLAYER] [A-AUDIO] |
| AEH-MED-002 | Grupowanie głośników i volume członków | O | HA+FW | utrzymać | baza; zachować | Istnieją discovery/subskrypcje; zachować generacje i UX. [A-GROUP] |
| AEH-MED-003 | Dowolne HA media_player jako karta | C | HA+FW | P1 | częściowo | HA83 jawne mute/unmute; HA85 bounded source Choice i HA87 repeat/HA89 shuffle odebrane na native45. HA90 relativevolume/HA91soundmode/HA92Stop/HA93fixedvolume + native46 guard odebrane; własny Player, pełny suwak/seek/browse/favourites/detail osobno. [A-CARD] [T-CAT] |
| AEH-MED-004 | Biblioteka mediów, favourites i speaker picker | C | HA+integracja | P3 | plan | Picker grup jest; szersze browse API zależne od odtwarzacza. [A-GROUP] [T-CAT] |
| AEH-MED-005 | MJPEG i picker kamer HA | O | HA+FW+źródło | utrzymać | baza; zachować | Allow-list, token kamery, hardware JPEG i idle DSI lease. [A-CAMERA] |
| AEH-MED-006 | Miniatury camera/image, Fit/Fill i refresh policy | B | HA+FW | P3 | plan | Widoczność/generation/backoff; bez raw 800x800 na kartę. [E-CAMERA] [T-CAMERA] |
| AEH-MED-007 | Doorbell: zdarzenie, wake, kamera i czas powrotu | B | HA+FW+automatyzacja | P3 | plan | Oddzielne pola polityki; użyć istniejącej aplikacji Camera. [E-CAMERA] |
| AEH-MED-008 | Audio strumienia kamery | B | HA+FW+źródło | P4 | plan | Oddzielny kontrakt formatu i miksowania; zachować jednego właściciela I2S. [T-CAMERA] [A-AUDIO] |
| AEH-MED-009 | Natywna aplikacja Immich/Gallery | O | FW+Immich | utrzymać | baza; zachować | Album/person/tag/daty/orientacja/slideshow; hardware JPEG i release. [A-GALLERY] |
| AEH-MED-010 | Galeria: dodatkowe źródła i pary portretów | C | HA/host+usługa | P3 | plan | Nie dublować Immich; opcjonalne HA media/Synology/przetwarzanie. [E-IMMICH] [T-SAVER] |
| AEH-MED-011 | Pogoda HA i dziewięć skończonych scen Lottie | O | HA+FW | utrzymać | baza; zachować | Zachować retained phase, jeden cykl i bounded source. [A-HOME] [A-POOL] |
| AEH-MED-012 | Prognoza, szczegóły i wykres low/high | B | HA+FW | P3 | plan | Prognozę i jednostki normalizuje HA; bounded liczba dni. [E-CARDS] [T-CAT] |
| AEH-MED-013 | Powiadomienia: czteroelementowa kolejka i M3 sheet | O | HA+FW | utrzymać | baza; zachować | Queue oraz pause/drain overlay są atutem obecnego produktu. [A-HA] [A-POOL] |
| AEH-MED-014 | Akcje i obraz w powiadomieniu | B | HA+FW | P3 | plan | Typed action IDs; obraz ma jawny limit i lifecycle. [T-CAT] |
| AEH-MED-015 | Historia/centrum powiadomień | B | HA+FW | P3 | native49/HA95: wdrożone w zakresie tekstu i gestów | Historia na HA; tylko bounded strona na urządzeniu. [E-CARDS] [M-UI] |
| AEH-MED-016 | GIF/radar i dodatkowe formaty obrazu | B | HA/host+FW | P4 | plan | Osobne limity rozmiaru/klatek/canvas; ukryte odtwarzanie zatrzymane. [E-CAMERA] |
| AEH-MED-017 | Muzyczna wizualizacja/spectrum/ambient worlds | B | FW+opcjonalny HW | P4 | plan | Wyodrębniony ograniczony region; audio ma pierwszeństwo. [M-APPS] [M-BSP] |

### Polityka ekranu i utrzymanie produktu

| ID | Funkcja | Baza | Zależności | Etap | Realizacja nowa | Warunek i dowód |
| --- | --- | --- | --- | --- | --- | --- |
| AEH-SYS-001 | Jasność, timeout i reguły aktywnej aplikacji | O | FW | utrzymać | baza; zachować | Touch/explicit wake liczy aktywność; redraw nie resetuje timeout. [A-SET] |
| AEH-SYS-002 | Harmonogram jasności, solar i tryb nocny | B | HA+FW | P3 | plan | Off/dim/clock i czas wake w jednej polityce. [E-SLEEP] |
| AEH-SYS-003 | Obecność sterująca wake/sleep | B | HA+FW+sensor | P3 | plan | Wybrana encja; jawny priorytet i debounce. [E-SLEEP] |
| AEH-SYS-004 | Sekwencja wygaszacza: zegar/media/photos/camera | C | HA+FW | P3 | plan | Aplikacje istnieją; sekwencja/arbitraż oraz zegary Digital/Glass/Classic/Bauhaus z wyglądem, sekundami i przesuwaniem pozycji pozostają planem. [T-SAVER] [E-SLEEP] |
| AEH-SYS-005 | Artwork/gallery jako wygaszacz | C | HA+FW | P3 | plan | Wykorzystać istniejących właścicieli i zwolnienie pamięci. [A-PLAYER] [A-GALLERY] [T-SAVER] |
| AEH-SYS-006 | Lokalna blokada ekranu/PIN | B | FW | P3 | plan | Niezależne od lock.* oraz autoryzacji HA. [E-SLEEP] [E-CARDS] |
| AEH-SYS-007 | Jednostki/timezone/NTP i format danych | C | HA+FW | P3 | plan | Zegar/HA są; pełny formularz i coverage wymagają audytu. [A-SET] [E-SYSTEM] |
| AEH-SYS-008 | HTTP OTA i stable/beta | O | HA+FW+wydania | utrzymać | baza; zachować | Istnieją update entity i selektor; to nie dowód web instalatora. [A-OTA] [A-SET] |
| AEH-SYS-009 | Instalator USB/web, wersje i UX aktualizacji | C | host+HA+wydania | P4 | plan | Dashboard import/OTA są; dodać spójny proces i zgodne artefakty. [E-SYSTEM] [T-BUILD] [M-FW] |
| AEH-SYS-010 | Reset częściowy/pełny i recovery danych | C | HA+FW+host | P4 | plan | Dokumentować wpływ na sekrety, konfigurację i rollback. [E-SYSTEM] [T-BUILD] |
| AEH-SYS-011 | Aktualizacja ESP32-C6/coproc i zgodność | B | FW+HW+host | P4 | plan | Oddzielna procedura recovery i fizyczny test. [E-SYSTEM] |
| AEH-SYS-012 | Automatyczny powrót Home po idle | B | HA+FW | P3 | częściowo: rzeczywisty FW | Settings-only, domyślnie wyłączone; 53 przypadki polityki host PASS. V18: Off obserwowane 32,084 s, Idle30 powrót w obserwacji hosta 32,462 s, osobne świeże przywrócenie własnego 30→0 i przegląd obrazów. Nie dowodzi to fizycznego czasu przejścia, dotyku/inercji ani p95; [rejestr](validation-2026-10-25.md). Polityka osobna od podświetlenia. [E-SUB] [E-SLEEP] |

### Rozszerzenia i warsztat deweloperski

| ID | Funkcja | Baza | Zależności | Etap | Realizacja nowa | Warunek i dowód |
| --- | --- | --- | --- | --- | --- | --- |
| AEH-DEV-001 | Deklaratywna rejestracja stron/aplikacji i reusable widgets | O | FW | utrzymać | baza; zachować | YAML policy; C++ ma maszyny stanów, bufory i taski. [A-NAV] |
| AEH-DEV-002 | Jeden autorski katalog schematów/capabilities | B | HA+FW+narzędzia | P1 | plan | Generowane metadane i fixtures bez kopiowania obcych kontraktów. [E-CARDS] [T-CAT] |
| AEH-DEV-003 | Podgląd host/WASM z tym samym rendererem | B | host+FW adapter | P4 | plan | Natywne PPA/DSI/JPEG/audio pozostają poza dowodem preview. [T-WASM] [M-VIBE] |
| AEH-DEV-004 | Zintegrowany Workbench: logi, screenshots, input replay | C | host+FW | P4 | plan | Obecne narzędzia i scenariusze są; brak jednego produktu UI. [A-VALID] [M-IRIS] |
| AEH-DEV-005 | Katalog aplikacji/pluginów i instalowanie | B | host+HA+FW | P4 | plan | Jawne zasoby, pochodzenie, ABI i uninstall lifecycle. [T-PLUGINS] [M-APPSTORE] |
| AEH-DEV-006 | Pakiety natywne z maintenance ABI/recovery | B | host+FW | P4 | plan | Oddzielny projekt; nie dopisywać Iris ABI do małego edytora. [M-VIBE] [M-IRIS] |
| AEH-DEV-007 | Generatywne tworzenie konfiguracji/Chat Coding | B | host+model | P4 | plan | Model na serwerze; wyniki przechodzą zwykłą walidację/preview. [M-GUIDE] [M-FAQ] |
| AEH-DEV-008 | Lokalny scheduler/reguły użytkownika na urządzeniu | C | HA/FW | P4 | plan | HA automations już mogą sterować; lokalne Lua/agent nie istnieje. [M-GUIDE] [A-HA] |
| AEH-DEV-009 | Pamięć agenta, umiejętności i sesje IM | B | host/model+FW opcjonalnie | P4 | plan | Możliwy companion; koszty/storage nie mogą wejść w audio critical path. [M-GUIDE] [M-CLAW] |
| AEH-DEV-010 | MCP client/server i połączenie HA | B | host+HA+protokół | P4 | plan | Sprawdzić transport/OAuth; samo MCP nie daje gotowej integracji. [M-MCP] [HA-MCP] |
| AEH-DEV-011 | Flota, kolejka buildów i remote build | B | host+usługa | P4 | plan | Oddzielna granica sekretów/serwera; brak potrzeby add-on dla prostego panelu. [T-BUILD] |
| AEH-DEV-012 | Rozdzielone dowody config/build/flash/runtime/visual | O | proces+HW | utrzymać | baza; zachować | Publikowany checkpoint nie przyjmuje automatycznie nowych funkcji. [A-VALID] |
| AEH-DEV-013 | Budżety widgetów i admission control | C | HA+FW | P2 | plan | Obecne lifecycle/pule są; model układu musi znać peak/retained/fragmentation. [A-NAV] [T-MEM] |

### Funkcje wymagające innej konfiguracji sprzętu

| ID | Funkcja | Baza | Zależności | Etap | Realizacja nowa | Warunek i dowód |
| --- | --- | --- | --- | --- | --- | --- |
| AEH-HW-001 | Bluetooth Classic A2DP sink | HW | HW+FW | X | plan | S31 ma BR/EDR; obecny P4/C6 nie otrzyma tego samą opcją YAML. [M-BSP] |
| AEH-HW-002 | Magnetyczne łączenie i topologia wielu ekranów | HW | HW+FW | X | plan | Magnetometry/kontakt i ESP-NOW; nie zwykły multi-device dropdown. [M-BSP] |
| AEH-HW-003 | IMU/haptics/bateria/gauge i gesty orientacji | HW | HW+FW | X | plan | Potrzebne fizyczne układy oraz profil pinów/lifecycle. [M-BSP] |
| AEH-HW-004 | Hot-plug moduły: joystick/relay/ToF/thermal/LED | HW | HW+FW | X | plan | Discovery EEPROM i exclusive slot ownership, nie fikcyjne wyjścia. [M-BSP] |
| AEH-HW-005 | Fizyczna kamera, zdjęcia i edge vision | HW | HW+FW+storage | X | plan | Inny przypadek niż istniejące odbieranie kamer HA. [M-BSP] |
| AEH-HW-006 | Native Matter hub/bridge i Thread border router | HW | HW+FW+accessory | X | plan | Mosaico ma osobne firmware; HA może pozostać kontrolerem. [M-MATTER] |
| AEH-HW-007 | USB secondary display/HID/UAC | HW | HW+FW+host | X | plan | Osobne BSP example, nie funkcja fabrycznej aplikacji HA. [M-BSP] |
| AEH-HW-008 | Inne panele/rotacja i profile urządzeń | HW | HW+FW+walidacja | X | plan | Metadane profilu nie dowodzą gotowego renderera dla nowej płyty. [T-BOARDS] [M-BSP] |

## Material Design 3 Expressive i granica produktu

Nowe widoki mają rozwinąć obecny język Material 3/Wear OS w kierunku Material Design 3 Expressive: czytelna hierarchia, akcent/role zamiast arbitralnych kolorów, spójna typografia, grupy kształtów, jasne stany i ruch wspierający orientację. To intencja projektu, nie stwierdzenie pełnej zgodności obecnego firmware z całym standardem. Punktem wyjścia pozostają [lokalne reguły i źródła projektu](../design/wearos-m3-map.md) oraz [oficjalny kierunek M3 Expressive][M3].

Widżet domenowy musi wyglądać i zachowywać się jak część tego produktu. Formularz konfiguracji w HA może korzystać z natywnego języka HA; podgląd urządzenia odwzorowuje jego kompozycję. Nie zastępować okrągłego Home przypadkową prostokątną siatką tylko dlatego, że edytor obsługuje DnD. Ruch, loading i zmiana motywu muszą respektować zarejestrowanych właścicieli snapshotów/direct regions i nie generować ukrytych animacji.

## Własność i wymagane bramki

| Warstwa | Właściciel | Reguła |
| --- | --- | --- |
| Konfiguracja/encje/akcje/sekrety/backup | Integracja HA | Waliduje dokument i capabilities oraz wywołuje HA; przeglądarka nie jest źródłem zaufanego profilu |
| Kompozycja i reguły aplikacji | Product YAML/assets | Konkretny wygląd/IDs i polityka; brak dużych maszyn stanów w lambdach |
| Gesture/navigation/display/audio/bufory | Companion ESPHome C++ | Jawne leases, pause/drain/resume i lifecycle; reusable bez nazw/pinów/800×800 produktu |
| Preview i generowanie danych | Host/HA | Nie jest dowodem właściwości DSI/PPA/cache ani audio sprzętu |
| Akceptacja | Dokładna para źródeł i obraz | Osobno config, tests, full native build, flash/hash, runtime, visual i ograniczenia |

Każda zmiana runtime określa źródło danych, task, bufor, maksymalny rozmiar, punkt zwolnienia oraz reakcję na błędny/niepełny payload i brak HA. Zachować RGB888 DIRECT, trzy display-owned DSI buffers, coherent LVGL bases, trzy surowe Home slots z JPEG backing, jeden app work buffer oraz jednego właściciela fizycznego audio. Nie przenosić obcych rozwiązań bezpośredniego zapisu do framebufferów lub raw-per-page.

Dla firmware mierzyć presents/FPS, loop, total i largest free block, retained/peak memory, DSI FIFO, ciągłość audio i gesty. Przejścia testować z Camera/Player/Voice/Gallery, powiadomieniem i zmianą motywu. Nowy native control nie jest ukończony, jeśli tylko pojawia się jego ikona.

Kod ESPControl/aktualnej Tessera/GSP nie staje się automatycznie źródłem do skopiowania. Szczegóły licencji i pochodzenia są w [porównaniu](../research/project-comparison-2026-10-24.md#licencje-i-granica-adaptacji). Domyślnie projektujemy własne kontrakty i implementacje.

## Dziennik nowych wdrożeń

Pierwsze trzy małe rozszerzenia edytora mają osobny [rejestr zmian i dowodów](editor-three-features-2026-10-24.md).

| Data | ID / zakres | Źródła/commit | Kod/testy | Config/build | Flash/runtime/visual | Akceptacja i ograniczenia |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-24 | Rejestr 108 rodzin, plan profilu 16 slotów | Niniejszy dokument | Dokumentacja | Nie dotyczy | Nie wykonywano nowych testów urządzenia | Plan; wszystkie nowe funkcje wymagają własnych dowodów |
| 2026-10-24 | P0: CFG-001..009/011, częściowo CFG-010/020 i UI-002/004 | Lokalne feature/ha-dashboard-2026-10-24; source-manifest-v3..v7 i manifest paczki HA w katalogu dowodów | 112 Python, 39 JS, 41 C++/schema; przegląd mock browser | Config i pełny ESP-IDF build v3/v4/v5/v7; v7 OTA i pełny ELF zweryfikowane | V7: 12 scenariuszy/33 obrazy, 3 etapy kafelków, 5 warm resetów i czysty start końcowy; pogoda FPS bez obserwowanego spadku, internal −4 KiB w parze pomiarów | Szczegóły, zachowane niezaliczone próby i granice dowodów: [rejestr walidacji](ha-dashboard-2026-10-24.md). Brak wdrożenia w rzeczywistym HA i dowodu wykonania usług/aktuatorów; pozostałe rodziny nie są ukończone |
| 2026-10-25 | CFG-012 / W13: grupowy wygląd HA12 | Lokalny manifest appearance v1 i przyjęty package12-v2; [rejestr wdrożenia](live-ha-deployment-2026-10-24.md) | 200 Node = 181 bez zmian +19; 250 HA shim; Ruff/syntax/patch PASS; wcześniejsze 3 FAIL i metadata NameError zachowane | Bez zmiany backendu/schematu/FW | Rzeczywisty HA12, osiem oryginalnych plików/7 unikalnych hashy; observer180s explicit selected on/off/toggle:0; bez Save | Tylko ograniczona paleta szkicu; naturalny wait15.716s potwierdza DOM/fokus, nie pojedynczą odpowiedź poll; urządzenie/mobile i pozostałe 108 rodzin nie są domknięte |

| 2026-10-25 | W04 / CTL-009, locale23 | Source23 `15b34d0211ec16812f0dee22283bde0045814b8f5db29328f8073cad1da41b2b`; [walidacja](validation-2026-10-25.md) | 39 native/481 subtests,301 HA,209 Node | Pełny build i2304-unit audit23 | OTA/fullELF/60s Home1, polska pogoda i Number open/close/original PASS; wcześniejszy22 single-step z HA PASS;23 granice/−0.75/0.75 i Light z HA/original PASS | Dwa Settings31FPS/failed0 bez narastającej straty free; hold/physical/audio/lifetime otwarte. QA usunięte, układ6 zachowuje DnD; brak Git publikacji |
| 2026-10-25 | W01 / CTL-002: input_button availability | Source24 `b035cf7e75aaed4009f01d6f03f77ef79f1765d9097f2186050fb30d7c00757e`; root receipt `5f1456dd497de5413628034dfa6a7b1186cade5c85e16ffc7facb3216048ae67` | Host W01 contract/Home composition i HA PASS; bez nowych testów dla tej dokumentacji | Pełny build,2304-unit audit,1OTA/fullELF/60s/normalroute PASS | Izolowany input_button:8ACK/2raporty/2usługi HA, disabled/held ABA i oryginały PASS |128B static binding cost;3Settings31sourceFPS/failed0. Normalny inverse 7→8 i usunięcie helpera PASS; pending/error innych domen, physical/audio/lifetime otwarte |
| 2026-10-25 | W04: reset wyniku nowej sesji | Source25 `05117070864d998b12d2b43d649df1f8dfc465bd388b9452e7a1b40476859625`; final receipt `de688b0f138e8693565d099440db47299c5b62f904b45fd4e773e5c29cb98505` | Dwie instrukcje wspólnego ownera; focused host/parentnegative PASS | Pełny build/2304-unit audit/1OTA/fullELF/60s/normalroute PASS; RAM i Flash jak24 | Number6ACK/2open/2close/1provider; nowa sesja Ready bez dodatkowego polecenia; oryginały PASS | Jeden Settings31sourceFPS/failed0, work buffers0; inverse9→10/unbound/exactdelete/HAoriginal PASS. Wcześniejszy collector pozostaje failed; physical/audio/lifetime otwarte |

### Zatrzymanie prac na koniec 2026-10-25

Stan aktualny: native26 / HA17 / czysty układ12. Odbiór PL/EN/PL separatora
Number, jeden cykl Ustawień31 FPS oraz usunięcie pomocnika przeszły. HA17
przeszedł wdrożenie i rzeczywisty native/browser test zmiany i przywrócenia
palety bez utraty szkicu/fokusu i bez Save. Odrębny pomiar Ustawień po HA17
pozostaje nieuruchomiony. HA18 — dostępność button/scene/script — ma kod poza
canonical i testy hostowe; nie został wdrożony. Pełne rodziny nadal pozostają
otwarte zgodnie z ich zakresem. [Raport i kolejność wznowienia](validation-2026-10-25.md#raport-stanu-na-koniec-dnia).

### Wznowienie 2026-10-26

HA18 jest zainstalowane, native26 pozostaje tym samym zweryfikowanym firmware.
Scoped root acceptance `eff912a4ac90cb08ae15ae0f93765502b0da2032767aac3bdcea5a0ae06c2081`
obejmuje source/storage/API/browser, izolowaną Scene z rzeczywistym feedbackiem
wirtualnego Boolean, dwa oryginały, exact inverse/delete i dwa cykle Ustawień
31sourceFPS/failed0. Wolna pamięć jest stabilna, przejściowo mniejszy largest
wrócił do4096KiB. Całe okna CPU/loop nie są porównaniem benchmarku: źródłowy
audyt wykazał brak resetu przy włączeniu logów i odroczone resety podczas direct
scroll. Czysty układ14 zachowuje pozycje użytkownika. Zero commit/push.
Timer19 jest zainstalowany i ma scoped odbiór funkcjonalny oraz wizualny,
exact inverse/cancel/delete i czysty układ16. Dopasowany cykl Ustawień utrzymuje
31sourceFPS/failed0. Mikrofon przywrócono do unmuted; nie ma pomocników QA.
Całkowita pamięć/CPU nie są przyjęte jako wyjaśnione; większość różnicy pamięci
poprzedza utworzenie timera. HA20 słońce ma lokalny kod/pakiet i testy hostowe,
ale nie ma jeszcze wdrożenia ani odbioru urządzenia. Zero commit/push.
[Szczegóły i granice](validation-2026-10-26.md).

### Wznowienie 2026-10-30

Po jawnie zleconej publikacji obu repozytoriów migracja została wznowiona.
HA20/native31 ma ograniczony odbiór pasywnej karty Sun; HA21 naprawia aktualność
biblioteki encji i ma wdrożenie oraz test w przeglądarce. HA22 dodaje presety
czasu timera, odebrane z resume i cancel na urządzeniu. Przywrócono wszystkie
16 kart, rewizja wynosi 22, własne encje QA usunięto. Zwykłe wejście do Ustawień
utrzymuje 54 FPS. [Dowody i ograniczenia](validation-2026-10-30.md).

## Kandydatury TouchDeck — 2026-10-30

Lista powstała podczas pauzy; **migracja została później jawnie wznowiona**.
Poniższe kandydatury nadal są wynikami badania, a nie deklaracją implementacji
ani zmiany statusu 108 bazowych rodzin. Bieżący punkt pracy:
[resume-2026-10-30.md](resume-2026-10-30.md).
Źródła, granice i propozycja kolejności: [raport TouchDeck](../research/touchdeck-2026-10-30.md).

| Kandydat badawczy | Mechanizm | Powiązanie / warunek |
| --- | --- | --- |
|TD-01 |Warunkowe strony/kafelki, auto-przejście i powrót |Rozwija CFG-014/018; po bounded templates, bez przerywania gestów i z jawną polityką stale/unknown. |
|TD-02 |Opcjonalny companion PC: metryki, media, głośność, dozwolone skróty |Osobny host i parowanie; zacząć od odczytu. USB serial nie oznacza HID. |
|TD-03 |Współdzielone źródła HTTP JSON i kontrola świeżości |Preferować HA REST sensors/adapter w HA; CTL-027 obejmuje akcje, nie ten model odczytu. |
|TD-04 |Widok Bambu Lab/AMS |Opcjonalny pion, preferowane dane z integracji HA; wymaga drukarki do odbioru. |
|TD-05 |Dwuwymiarowe grupy stron |Po CFG-014/016 i testach arbitrażu obu osi; zachować ograniczone bufory. |

Do istniejących specyfikacji dopisać: progi warn/crit z histerezą (CTL-017/UI-003),
do czterech odczytów w kafelku i bounded wykresy (CTL-017/018/019), lokalny edytor
jako klient HA (CFG-004/015), presety motion z limitem kosztu i spokojnym
wariantem (UI-002), szybki panel (CFG-017/SYS-001) oraz polityki obecności
(SYS-002/003). Nie dublować tych rodzin i nie traktować opisów jako odbioru.

Badanie potwierdza, że TouchDeck **używa snapshotów i własnego kompozytora**;
nie stanowi argumentu za usunięciem obecnej architektury nawigacji Atmosfery.

## Definicje odsyłaczy

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
