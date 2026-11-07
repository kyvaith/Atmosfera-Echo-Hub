# HA81 — aktywności pilota we wspólnym Choice

Native45/HA81/układ263: [kontrakt, dowody i ograniczenia](remote-activity-design-2026-11-01.md).
742 Python (3 skip),368 Node,7 focused i lint/diff pass;39 canonical=frozen=live.
25 ukończonych przypadków/28 oryginałów,4 exact turn_on(activity) Core/MQTT przed
feedback. V1 FAILED po14 przypadkach na błędnym oczekiwaniu testu atrybutów
unavailable; V2 potwierdził11 pozostałych i final81 browser/Confirm/Undo/noSave.
Nie przepisano starego ACK, backend80/81 identyczny. Własna Core RemoteEntity
bez IR/RF, cały entry/rejestr/stan/tematy usunięto, źródło QA zarchiwizowane poza
custom_components. Dane użytkownika zachowane;263 wynika tylko z inverses QA.
Trasa53 source FPS/avg16451/max29974 μs/failed0/segments1, wcześniejszy zakres
52–55; PSRAM4886/internal27 KiB,work0. Bez native build/flash i GitHub.
Receipt W2/ha81-remote-activity-scoped-acceptance.json.

# HA79 — jawne zasilanie pilota

Native45/HA79/układ259: [projekt i dokładne granice odbioru](remote-power-design-2026-11-01.md).
735 Python (3 skip), 365 Node, lint i diff pass; 39 canonical=frozen=live.
Dwie dokładne usługi i wiadomości MQTT przed feedback, 14 scenariuszy native,
18 oryginałów, rzeczywisty końcowy browser i Undo bez Save. Własna Core
RemoteEntity nie ma nadajnika IR/RF. Pierwszy błędny provider z int0 i jego
raport zachowano. Final79 poprawia wielkość przycisków, bez zmiany backendu78.
Cleanup/audyt/archiwizacja kodu QA zakończone, źródło testowe nie jest aktywne.
Krótka trasa54 source FPS/avg16527/max23911 μs/failed0/segments1, PSRAM4878/
internal27 KiB, work0. Dane użytkownika zachowane, bez native flash i GitHub.
Receipt W2/ha79-remote-power-scoped-acceptance.json.

# Walidacja Atmosfery — 1 listopada 2026

## HA75: jawne standardowe akcje odkurzacza

Odebrany zakres: native45 / HA75 / układ236. Bez commita lub push.
Receipt: `C:/aeh-build/feature-continuation-20261031-next/ha75-vacuum-actions-scoped-acceptance.json`.
Projekt: [polityka i granice](vacuum-actions-design-2026-11-01.md).

Wdrożono sześć jawnych akcji: start/wznowienie, pauzę, stop, powrót do bazy,
lokalizację i sprzątanie bieżącego miejsca. Edytor ma czytelne PL/EN, sześć
zawijanych opcji ze zaznaczeniem i zachowaniem scrolla inspektora przy wyborze.
Wybór zmienia wyłącznie szkic. Nowa karta nie uruchamia robota domyślnie.
Polityka ponownie sprawdza stan, rzeczywiste flagi Core i usługę w chwili
wykonania. Moc ssania z HA65 zachowuje oddzielny kontrakt.

### Źródła i instalacja

Przed zapisami potwierdzono HA73/226, wszystkie37 plików oraz chronione dane,
16kart/3kamery/8preferencji i pełną tożsamość działającego native45.
Core2026.7.1 Vacuum/MQTT nadal mają te same piny co31.10. Odczytano realne
tłumaczenia Core. Jego polski Error wymaga fallback Błąd. Standardowe
„wraca do stacji dokującej” ma179px przy Roboto16 i caption136px; HA75 używa
„Powrót do bazy”. Specyficzne translacje encji zachowują pierwszeństwo.

HA74 zachowano jako precursor instalacyjny przed tym skróceniem; nie uzyskał
odbioru wizualnego i nie uruchomiono na nim kampanii robota. HA75 zainstalowano
atomową wymianą katalogu, z kopią starej wersji poza custom_components,
sprawdzeniem hashy i rewizji, następnie jednym restartem Core. Oczekiwano na
RUNNING oraz gotową komendę layout. 38frozen75=canonical=installed.

719testów Python przeszło,3pominięte;356testów Node przeszło. Dziesięć nowych
testów host sprawdza m.in. IntFlag/bool, brak usługi, macierz aktywności,
domyślne/pasywne karty, istniejącą moc i pierwszeństwo translacji. Critical
Ruff E9/F63/F7/F82 i git diff--check przeszły. Nie twierdzimy, że wykonano
pełny stylistyczny lint całego historycznego WIP.

Nie zmieniano firmware ani źródeł forka ESPHome; brak nowego build/flash.
Nadal działa wcześniej wgrany native45, marker2026-10-31 17:54:08+0100,
pełny ELF `c74f3f2172234acbfb96dfe45f154dcbb5f89d8700384997f50ca8ed988586d5`.

### Urządzenie, HA i rzeczywisty MQTT

Kampania `vacuum-actions-v1`, owner`c611883f407441aca53d64d2cebd6504`,
używała własnej encji MQTT z rzeczywistym providerem Core i retainfalse dla
komend. Wejścia urządzenia podawano przez istniejący debug_touch_input do
natywnej ścieżki dotyku; nie jest to test fizycznego GT911 palcem.

Dokładna kolejność10usług i10odebranych wiadomości brokera:
start/pause/start/return_to_base/pause/stop/clean_spot/stop/locate/locate.
Każdą komendę odczytano z brokera przed wysłaniem feedback. Stan HA nadal
miał poprzednią wartość. Locate nie udawało zmiany aktywności nawet w error.

32scenariusze obejmują wszystkie sześć aktywności, wszystkie akcje, redundantne
dotknięcia, brak START i przywrócenie flagi, outage/unknown/error, przytrzymanie
error→paused ABA, przeciągnięcie zaczynające się w kafelku, aktualizację poza
widoczną stroną oraz PL/EN. Negatywne przypadki nie dodały komend. W czasie
przytrzymania odczytywano tylko projekcję dostępności; capture readiness
sprawdzano po release. Pełne ELF/revision/caption/press fences pozostały ścisłe.

Przejrzano33oryginalne800×800:32scenariusze i końcowy Home. Contact sheet,
piny i nagłówek Home znajdują się w `vacuum-actions-v1/contact-provenance.json`.
Oryginał `vacuum-returning-pl-compact-original.jpg` potwierdza pełny podpis,
czytelność, kolor, górne ikony i brak pozostawionej warstwy pressed. Wcześniejszy
nieznany stan sąsiednich encji tuż po restarcie Core normalnie ustąpił po ich
raporcie; nie stanowi nowego defektu renderera.

Rzeczywisty browser: wybrano Pause, potem Dock, sprawdzono obie zaznaczone
opcje i przyjazne nazwy w select, wykonano dwa Undo, Zapisz pozostał wyłączony.
Nie zapisano szkicu ani nie wykonano usług z browsera. Screenshoty pokazują
wszystkie6przycisków w wąskim responsywnym widoku. Odczyt scrollTop inspektora
wynosił0 w tym układzie, więc nie przypisujemy temu obserwacji przewijania
osobnego wysokiego panelu desktop. Jego niezerowy scroll ma test host.
ACK jest przypięty do rzeczywistego ownera tej kampanii.

### Dopasowany krótki pomiar i przywrócenie

Ta sama trasa Home1→2→Settings→2→1 na native45, bez innego aktora input:

| Metryka | Przed HA73, dzisiejszy start | Po HA75 i cleanup |
| --- | ---: | ---: |
| Źródłowe klatki / FPS | 80 /54 | 80 /54 |
| Średni / maksymalny czas | 16122 /24272us | 16475 /24036us |
| failed / segments | 0 /1 | 0 /1 |
| Wolna PSRAM | 4880KiB | 5610KiB |
| Największy blok PSRAM | 2112KiB | 2176KiB |
| Wolna pamięć wewnętrzna | 32KiB | 32KiB |
| JPEG cache | 918KiB | 906KiB |
| app_work / scroll / close | 0 /0 /0 | 0 /0 /0 |

Raw Home5625KiB, DSI5625KiB, weather1792KiB i control241KiB bez zmian.
Nie wykazano spadku sourceFPS ani ubytku pamięci w tej trasie. Średnia różni się
o353us; to krótki pomiar, bez statystycznego p95. Zysku RAM nie przypisujemy
tej funkcji: próbki różnią się fazą rozgrzania/cache. Nie jest to activeHome4
ani fizyczny panelFPS, test audio, opóźnienia palca lub długiego wycieku.
Przejrzano obie pary oryginalnych Home screenshots i pełne nagłówki.

Układ został przywrócony236 przez inverse wyłącznie własnych pól. W domu15,
Wilgotność6 i Światło7 są na swoich miejscach;16kart/3kamery/8preferencji.
Chronione data i options z normalizowaną rewizją95 mają identyczne hashe jak
przed testem. Wszystkie własne topics wyczyszczone, fixture usunięta; niezależny
odczyt SSH potwierdza brak encji/unique_id w registry i referencji w layoutach.
Token tymczasowy odwołany, faults[]. Browser odświeżono do236 i oryginalnych
kart, bez niezapisanych zmian. Brak aktywnego aktora input.

Fizyczny robot, mapy, pokoje/routines i vendor commands pozostają poza tym
odbiorem. `clean_area` istnieje w tym Core, lecz wymaga prawdziwego area_mapping.

## HA76: jedno przypisane pomieszczenie na kafelku

Odebrane native45/HA76/246; bez nowego firmware, commita lub push.
Receipt: `C:/aeh-build/feature-continuation-20261031-next/ha76-vacuum-area-scoped-acceptance.json`.
[Kontrakt](vacuum-area-design-2026-11-01.md) korzysta z rzeczywistego
cleaning_area_id i Core area_mapping. Dropdown pokazuje nazwy istniejących,
przypisanych obszarów. Nie zgadujemy segmentów, nie wybieramy pierwszego celu
i nie wysyłamy usługi z edytora. Node360/Python729(3skip),10nowych focused,
criticalRuff i zwykły git diff--check przeszły. Tymczasowy check z wyłączonym
core.autocrlf błędnie potraktował całe CRLF jako whitespace; zachowano wynik
jako błąd wywołania QA, bez masowego przepisywania źródeł. Normalny check exit0.

39frozen76=canonical=installed, po końcowym przywróceniu CoreRUNNING i layout246.
Instalacje/pomiary A/B używały wyłącznie przypiętych75/76, atomowej wymiany
katalogu i zachowania opcji. Native45 i pełny ELF pozostają jak w HA75.

### Funkcja i obraz

AreaV4 owner`2f16711a9d7d43979400565509fac66c`: rzeczywista własna MQTT Vacuum,
dwa własne obszary HA i prawdziwe options_domain/options registry API. Publiczne
vacuum/get_segments potwierdziło trzy segmenty. Trzy natywne wejścia dotyku
przez debug_touch_input wykonały dokładne clean_area. Zdarzenie call_service
zawiera surowy pojedynczy area_id; Core normalizuje go później. Broker dostał
kolejno `["17","18"]`, `["01"]`, `["18","17"]` przed wysłaniem feedback.
Ostatnia kolejność pochodzi ze zmienionego mapowania Core, nie z ESPHome.

24scenariusze obejmują featureloss/restore, utratę mapowania przy niezmienionym
paused, usunięcie rzeczywistego obszaru, held map-removal→restore ABA, drag,
aktualizację poza ekranem, busy/error/outage/unknown i PL/EN. Odmowy nie wysłały
dodatkowego ruchu. Przejrzano25oryginałów800×800 i contact/provenance; pełny
Home po cleanup oraz nagłówki pozostają kompletne. Fizyczny robot i fizyczny
GT911 nie są dowiedzione przez diagnostyczne wejście pointer.

Rzeczywisty browser V2 na identycznym frozen76: wybór Biura, jawne odświeżenie
bez utraty szkicu, Undo do Salonu, dokładny area_id z DOM i Saveoff/noSave.
`vacuum-area-v2/browser-biuro-visible.png` pokazuje selector i wszystkie akcje.
V4 jawnie referuje tę osobną próbę UI; nie kopiowano ACK pod nowego ownera.

Zachowano nieudane wcześniejsze kampanie. V1 zatrzymało błędne oczekiwanie
listy w surowym zdarzeniu call_service; broker już otrzymał prawidłowe segmenty.
V2/V3 zatrzymały się na rzeczywistym problemie providera Core2026.7.1:
get_segments ma success, a hass.states nadal nie zawiera CLEAN_AREA. V4
izoluje ten fakt, po czym fixture podaje prawdziwą zmianę aktywności i otrzymuje
opublikowaną capability. Nie zmieniono Core ani nie pominięto bramki źródła.
[Osobna obserwacja z pinami](ha-mqtt-vacuum-capability-observation-2026-11-01.md).

### Pamięć i źródłowa kadencja

Pierwsze krótkie75/76 miały zmienne52–55FPS. W pierwszym porównaniu pamięci
75end miało5610KiB, a76end4892KiB. Nie przypisano tego funkcji: już73start i
75start miały4882/4884KiB i ten sam residual12637KiB. Przeprowadzono źródłowe
A/B75→76 i dodatkową serię siedmiu oddzielnych wejść do Settings na każdej
wersji. Każda seria resetuje licznik przez zamknięcie/ponowne otwarcie app.

| Właściwy dłuższy test | Kontrola75 | Kandydat76 |
| --- | ---: | ---: |
| Źródłowe klatki | 539 | 556 |
| FPS7serii | 52/53/54/52/52/54/53 | 53/54/53/54/54/54/55 |
| Mediana FPS | 53 | 54 |
| Średni ważony render | 16853,68us | 16534,40us |
| Najwyższy czas pojedynczego render | 33034us | 26208us |
| failed / segments | wszystkie0 /1 | wszystkie0 /1 |
| Wolna PSRAM / JPEG cache | 4884 /913KiB* | 4874 /924KiB* |
| Największy blok PSRAM | 1856KiB | 1952KiB |
| Wolna wewnętrzna pamięć | 27KiB | 27KiB |
| app_work / scroll / close po wyjściu | 0 /0 /0 | 0 /0 /0 |

*Dokładne JPEG w logach: kontrola snapshot total6538KiB, rawHome5625KiB;
kandydat total6549KiB, rawHome5625KiB. Różnica11KiB skompresowanej zawartości
odpowiada różnicy wolnej pamięci z dokładnością zaokrągleń KiB. Pozostałe named
bufory DSI5625/weather1792/control241 nie zmieniły się. Należy czytać dokładne
linie memory.snapshot, nie wyliczać JPEG z całego known memory.

Nie wykazano utrzymującego się spadku w tej trasie. Wyników nie interpretujemy
jako przyspieszenia spowodowanego kodem HA; firmware i renderer są identyczne.
Różnica internal32→27 względem początku dnia występuje także na starej75,
stabilizuje się przez7serii i nie została przypisana adapterowi. Krótkie
słabsze wyniki pozostają w archiwum. To nie jest panelFPS, p95, activeHome4,
ciągłość audio ani długotrwały test leak.

Wstępna próba powtarzania benchmarku bez zamykania Settings miała kumulowane
liczniki obejmujące3s przerw:54/35/31/30/29. Ten wynik jest niewłaściwy do
oceny FPS ruchu i nie został użyty do odbioru. Poprawiony reentry7 daje siedem
niezależnych liczników poniżej100klatek. Dwa wcześniejsze koordynatory A/B
nie uruchomiły kontroli: pierwszy logował się przed startem HTTP, drugi
błędnie oczekiwał array zamiast publicznego `{providers: [...]}`. Oba przywróciły
pliki76. V3 przeszedł rzeczywisty read-only preflight, HTTP readiness, Core
RUNNING, siedem serii kontroli i końcowe dokładne przywrócenie76. Wszystkie
logi nieudanych prób zachowano. Przejrzano cztery pełne oryginały długiej pary.

### Przywrócenie i zakres

Final layout246/16kart/3kamery/8preferencji, protected95/data identyczne.
W domu15/Wilgotność6/Światło7 zachowane. Wszystkie cztery fixtures i osiem
obszarów usunięte; niezależny SSH storage audit po końcowych restartach
potwierdza brak registry/layout/area references. Tokens revoked/faults[].
Brak aktywnego input aktora, finalnie zainstalowane39plików76, źródła i opcje
potwierdzone po przywróceniu. Vendor maps/routines, wiele obszarów jedną
akcją i fizyczny robot pozostają osobno.
# HA77 — zgodny podgląd czasu i brakujący zapisany pokój

Odbiór native45/HA77/układ254: [projekt, dowody i ograniczenia](duration-preview-design-2026-11-01.md).
39 plików canonical=frozen=installed; 731 Python (3 skip), 363 Node i lint
przeszły. Siedem dodatnich przypadków duration oraz outage na urządzeniu,
cztery dowody browsera. Pokój: trzy stany native i browser refresh/wybór/Undo,
bez usług aktuatorów. 15 oryginałów i contact sheet przejrzano. Zachowano dwie
nieudane próby QA oraz osobny poprawiony test, nie przypisując im pełnego PASS.
Krótka trasa 54 source FPS, avg16409/max23799 μs, failed0/segments2;
PSRAM4878/internal27 KiB, work0, bez nowego firmware/build/flash. Oryginalny
układ/prywatne dane zachowane, cztery fixtures i dwa obszary usunięte, tokeny
odwołane. Receipt: W2/ha77-scoped-acceptance.json. Bez commit/push.



**Odbiór 01.11: native45 / HA83 / układ268.** MED003/W14: jawne Wycisz i
Przywróć dźwięk dla HA media_player, wymagany bool/bit8/świeży stan. Dwie
dokładne usługi Core/MQTT przed feedback, bez zmiany odtwarzania, utworu ani
głośności.19 przypadków/22 oryginały800×800, rzeczywisty browser/dwaUndo/noSave,
niezależny cleanup.749Python(3skip)/371Node,39 zgodnych plików. Trasa55 source
FPS/avg16575/max23453us/failed0, PSRAM4884/internal27 KiB, work0; zgodna z
poprzednim zakresem52–55. [Zakres i dowody](media-mute-design-2026-11-01.md).
Domyślne Play/Pause bez zmian; fizyczny głośnik/GT911 osobno. Bez native flash
i publikacji Git. Starsze wpisy poniżej.


Receipt: W2/ha83-media-mute-scoped-acceptance.json.


**Odbiór01.11: native45/HA85/układ272.** MED003/W14: wybór źródła dowolnego
HA media_player przez istniejący Choice/Zastosuj;1..8różnych nazw/32UTF8b,
bit2048 i aktywny stan.5exact usług Core/MQTT przedfeedback,30ukończonych
przypadków/33oryginały800×800, rzeczywisty final85browser/review/dwaUndo/noSave,
niezależny cleanup.755Python(3skip)/374Node,39zgodnych plików. Trasa54sourceFPS/
avg16805/max23134us/failed0,PSRAM4880/internal27KiB/work0,DSI0. Zgodna z
poprzednim zakresem52–55. [Projekt i dowody](media-source-design-2026-11-01.md).
Fizyczny TV/HDMI/GT911 i większe listy osobno; bez nativebuild/flash/publikacji.
MED003 pozostaje częściowy: mute i source odebrane, bogatsze media dalej plan.

Receipt: W2/ha85-media-source-scoped-acceptance.json.


**Odbiór01.11 native45/HA87/układ276.** MED003/W14: powtarzanie off/one/all
przez istniejący Choice/Apply,bit262144, rzeczywisty CoreRepeatMode.4exact
usługi/MQTT przedfeedback; playback/track/volume/mute/shuffle bez zmian.
35przypadków/39oryginałów (w tym odrzucony stary opis86 i zaakceptowane87),
final87browser/review/dwaUndo/noSave, cleanup.762Python(3skip)/378Node/39plików.
Trasa53sourceFPS/avg16906/max24447us/failed0,PSRAM4884/internal27KiB/work0,
zgodna z52–55. [Projekt i granice](media-repeat-design-2026-11-01.md).
Skrócone opisy Home wPLEN mieszczą się w136px; długie tłumaczenia dostają...
Fizyczne zapętlenie muzyki/GT911 osobno; bez nativebuild/flash/publikacji Git.

Receipt: W2/ha87-media-repeat-scoped-acceptance.json.


**Odbiór01.11 native45/HA88/układ278.** Długie nazwy źródeł mają na Home
widoczne... w budżecie136px; HAeditor dzieli dokładnie ten caption. W Choice
i usłudze zachowano pełne nazwy.8przypadków/11oryginałów,1exact nieskrócona
komenda HDMI2-Salon-Telewizor przedfeedback, final88browser/review/twoUndo/
noSave/cleanup.763Python(3skip)/379Node/39zgodnych plików. Trasa53sourceFPS/
avg16298/max30282us/failed0,PSRAM4886/internal27KiB/work0,DSI0; nadal52–55.
[Zakres](media-source-design-2026-11-01.md). Aktualna seria dodała mute/unmute,
źródła i powtarzanie dla HAmedia_player. W14/MED003 pozostaje częściowy.
Bez nowego nativebuild/flash i bez commit/stage/push. Starsze wpisy niżej.

Receipt: W2/ha88-media-caption-scoped-acceptance.json.


**Odbiór01.11 native45/HA89/układ283.** MED003/W14: jawne Losowo/Po kolei
z kafelka,shuffle_set bool/bit32768.2exact usługi Core/MQTT przedfeedback,
bez zmian playback/volume/mute/repeat/title.19przypadków/22oryginały,actual89
browser/requiredBool/dwaUndo/noSave/cleanup.771Python(3skip)/382Node/39plików.
Trasa54sourceFPS/avg16204/max23957us/failed0,PSRAM4892/internal27KiB/work0,
DSI0; nadal52–55. [Projekt i dowody](media-shuffle-design-2026-11-01.md).
W tej serii odebrano mute,source,repeat,shuffle i kompaktowe opisy. W14/MED003
nadal częściowy; fizyczne odtwarzanie muzyki osobno. Bez nativeflash/Gitpush.

Receipt: W2/ha89-media-shuffle-scoped-acceptance.json.


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

Receipt: W2/ha90-media-volume-native46-scoped-acceptance.json.


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

Receipt: W2/ha91-media-sound-scoped-acceptance.json.


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

