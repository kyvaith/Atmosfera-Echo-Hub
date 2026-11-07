# Odtwarzanie losowe HA — W14 / MED003

Stan: ograniczony odbiór native45 / HA89 / układ283 zakończony.

Core2026.7.1 rejestruje media_player.shuffle_set z wymaganym shuffle:boolean,
bit SHUFFLE_SET32768; provider otrzymuje async_set_shuffle(shuffle:bool).
Źródła i hashe: W2/media-shuffle89-installed-contract.json; dokumentacja:
https://www.home-assistant.io/integrations/media_player/ .

HA posiada obserwowany bool, akcję, tłumaczenia i dispatch. Edytor wybiera
Losowo/Po kolei jako jawny szkic z Undo/Save. Nie tworzymy domyślnego toggle.
Na native45 używamy zwykłego kontekstu tap i generacji press_enabled, tego
samego Home/snapshotów; bez aplikacji, protokołu, bufora, tasku lub subskrypcji.
Powtórzenie osiągniętego celu, off/standby/unknown/unavailable, brak flagi lub
nieprawidłowy bool blokują polecenie. Stan po poleceniu pochodzi z feedback.
Playback,volume,mute,repeat i tytuł nie zmieniają się optymistycznie. Opis HA
z kontekstem losowania mieści się w136px przy użyciu istniejącego formattera.

Plan odbioru: realCoreMediaPlayerEntity/własneMQTT bez transportu do głośnika,
dwa dokładne boolTrue/False przedfeedback; redundant/featureloss/missing/invalid/
off/standby/outage/heldABA/drag/off-window/PLEN, actualbrowser/Undo/noSave,
800×800,sprzątanie i pomiar. Fizyczny losowy porządek muzyki oraz GT911 osobno.

## Odbiór

W2/ha89-media-shuffle-scoped-acceptance.json:39canonical=frozen89=live,
771Python(3skip)/382Node/8focused/criticalRuff/normaldiff. V1 przerwano przed
pierwszym pełnym przypadkiem: QA oczekiwał pełnego captionu HA, produkt już
poprawnie mieścił go w136px z widocznym... . Zachowano failedreport; brak
poprawki produktu/redeploy. V2 oczekiwał opisu mierzonego zgodnie z kontraktem,
następnie22oryginały800×800/contact/paired (20funkcjonalnych+2perf) przejrzano.
19scenariuszy:2exactboolTrue/False usług i pojedynczychMQTT przedfeedback;
realCore provider potwierdza typbool. Playback,volume.42,muteFalse,repeatOff,
titleTrackQA pozostały bez zmian przedfeedback. Redundant,featureloss,
missing/string/intbool,off/standby/unknown/offline,heldABA,drag,off-window,PLEN
przeszły. Actual89browser: oba przyciski,requiredBool,dwaUndo,noSave.

Final283 przywraca16kart/3kamery/8preferencji oraz chronione opcje/dane. Entry,
registry,stan,tematy usunięte, tokeny odwołane,faults[]. Niezależny SSHaudit
archiwizuje4exact własne pliki poza custom_components po wyładowaniu.
Trasa79klatek/54sourceFPS,avg16204/max23957us,failed0,segments1. PSRAM4892/
internal27/largest3264KiB,JPEG905,work/scroll/close0,fixedpools same,DSI0.
Free+6KiB vs88 odpowiadaJPEG−6; brak dowodu przyspieszenia/trwałej straty.
Native45 bez zmian; brak nowego build/flash/commit/stage/push. Fizyczny losowy
porządek muzyki,GT911,audio/lifetime pozostają osobnymi bramkami.
