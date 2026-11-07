# Głośniej / Ciszej dla HA media player — W14 / MED003

Stan: ograniczony odbiór native46 / HA90 / układ290 zakończony.

Core2026.7.1 rejestruje volume_up/down bez danych; wspiera VOLUME_SET4 lub
VOLUME_STEP1024. Domyślna implementacja Core dla VOLUME_SET liczy nowy poziom
z rzeczywistego volume_level i volume_step, ograniczając go do0..1. Domyślny
volume_step to0.1, ale vendor może implementować własne kroki. Źródła i hashe:
W2/media-volume90-relative-contract.json / media-volume90-installed-contract-
research.json; dokumentacja https://www.home-assistant.io/integrations/media_player/ .

Nie wyprowadzamy siatki absolutnego volume_set z volume_step: dotyczy on
poleceń względnych, a źródło może raportować wartości spoza takiej siatki.
Pełny suwak procentowy wymaga osobnego projektu obserwacji raw/quantization,
generacji ABA oraz potwierdzenia feedback. W tym fragmencie produkt wysyła
tylko standardowy volume_up/down. Core/provider posiada przeliczenie i krok;
HA adapter posiada dozwoloną akcję i opis, native45 zwykły tap/snapshoty.
Bez zmian NumericDomain,protokołu,bufora,tasku,subskrypcji i lokalnego audio.

Warunki: aktywny on/idle/playing/paused/buffering, bit4lub1024, skończony
numeryczny volume_level0..1 (bezbool/coercji), usługa obecna. Up na1 i Down na0
są bierne. Brak poziomu,off/standby/unknown/unavailable lub utrata obsługi
blokują akcję. Zwykła zmiana poziomu zmienia opis Home i istniejącą generację
przycisku; drobna zmiana w ramach zaokrąglenia nie zmienia zamiaru względnego.
Nie wyliczamy absolutnego celu z opisu ani przewidywanego stanu. Opis procentowy
to wyłącznie prezentacja raportowanej wartości, z136px budżetem i PL/EN.

Plan odbioru: rzeczywista własna CoreMediaPlayerEntity z VOLUME_SET4 i krokiem
0.1, dziedziczone async_volume_up/down → async_set_volume_level i własnyMQTT.
Potwierdzić dwa publiczne polecenia z samym entity_id oraz dwa poziomy Core
przedfeedback; playback/mute/repeat/shuffle/title bez zmian. Granice0/1,
None/string/bool/out-of-range,featureloss,outage,heldABA,drag,off-window,PLEN,
browser/Undo/noSave,800×800,cleanup i pomiar. Fizyczny głośnik i GT911 osobno.

## Odbiór


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

Dowody: W2/ha90-media-volume-native46-scoped-acceptance.json. Źródła HA39
canonical=frozen90=live, chronione dane/opcje(revision95) i preferencje zachowane.
Rzeczywista własna CoreMediaPlayerEntity dziedziczy oba kroki; dla.425 otrzymuje
.525, a dla.525 otrzymuje.42500000000000004. Nie zaokrąglamy komendy do siatki;
publiczne usługi mają tylko entity_id. Przedfeedback wszystkie atrybuty, w tym
rawvolume, pozostają identyczne. Granice0/1,invalid/None/string/bool/featureloss/
off/standby/unknown/offline,heldABA,drag,off-window i PLEN przeszły.
W1/W2na45 ujawniły realną lukę deferred tap; zachowano failedreports.
Po naprawie46 długie oczekiwanie po heldrelease i dalsze przypadki kończą się
dokładnie dwoma poleceniami, bez późnych dubli. Wszystkie własne wpisy/registry/
stany/tematy usunięto,4pliki niezależnie zarchiwizowano, tokeny odwołano.
