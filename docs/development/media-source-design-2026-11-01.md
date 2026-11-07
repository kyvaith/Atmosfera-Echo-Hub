# Wybór źródła HA media player — W14 / MED003

Stan: odbiór źródeł HA85, rozszerzony o kompaktowe opisy HA88 / native45 / układ278.

MediaPlayerEntity w zainstalowanym Core2026.7.1 publikuje source_list/source i
bit SELECT_SOURCE=2048. Usługa media_player.select_source wymaga source:string,
provider otrzymuje async_select_source(source). Źródła i hashe zachowano w
W2/media-source84-installed-contract.json; dokumentacja:
https://www.home-assistant.io/integrations/media_player/ .

HA posiada listę, bieżący indeks, mapowanie indeksu na dokładny string i usługę.
Używamy istniejącego Choice, wspólnej sesji i ogrodzenia poleceń. Native45
posiada listę, Apply, snapshoty i bufory. Nie dodajemy C++, pól wire, nowej
aplikacji, tasków, buforów obrazu ani subskrypcji. Otwieranie wyboru nie zmienia
źródła. Dopiero Zastosuj wysyła pojedynczy dokładny cel; brak optymistycznego
feedback i brak automatycznego Play/Power/Mute/Volume.

Dopuszczamy stany on/idle/playing/paused/buffering, bit2048 i 1..8 różnych nazw
do32 bajtów UTF8, według istniejącej walidacji Choice/fontu. Zachowujemy spacje
i kolejność źródła. Nie zgadujemy brakującego indeksu ani pierwszego wejścia.
Off/standby/unknown/unavailable nie oferują sterowania. Utrata flagi lub zmiana
listy zamyka starą sesję; zmiana stanu wycofuje nieaktualną autoryzację. Lista
większa niż8 wymaga oddzielnego stronicowania, bez cichego obcięcia.

Edytor potwierdza migrację v3 i zmienia wyłącznie szkic z Undo/Save. Karta Home
pokazuje obserwowane źródło, a inne karty media zachowują tytuł/PlayPause.
Tłumaczenia atrybutu HA są preferowane, nazwy sprzętowych wejść pozostają
oryginalne. Plan odbioru: izolowana real Core MediaPlayerEntity z własnym MQTT,
native tap/wybór/Apply, dokładne stringi przed feedback, brak innych komend,
1/8/9opcji, whitespace/UTF8, featureloss/reorder/outage/heldABA/off-window,
browser/review/Undo/noSave, oryginały800×800,cleanup i pomiar. Fizyczny TV,
przełączenie HDMI i GT911 wymagają osobnej obserwacji.

## Odbiór

W2/ha85-media-source-scoped-acceptance.json:39canonical=frozen85=installed,
755Python(3skip)/374Node/6focused/criticalRuff/normaldiff pass. Backend84=85;
85 zmienia tylko frontend (ukrywa nieobsługiwane mute) i wersje manifest/panel.
V1/84 FAILED po11ukończonych przypadkach i3dokładnych poleceniach Radio/HDMI1/
 Żółty przedfeedback. QA wymagał source_list po utracie bitu, a Core go pomija.
Zachowano raport i źródła, bez obejścia w produkcie. V2/85:19pozostałych/
powtórzonych przypadków i2komendy Radio/A7, nowy rzeczywisty browser85/review/
Confirm/dwaUndo/noSave, bez przenoszenia ACK. Razem30przypadków/5usług/MQTT.
Playback,volume.42,muteFalse,titleTrackQA nie zmieniają się przed feedback.
HeldABA, redundant,reorder,featureloss,unknownstate/current,outage,off,standby,
off-window,1/8/9opcji iPLEN przeszły.31funkcjonalnych+2pomiarowe oryginały800×800
i contact/pairedreview przejrzano; licznik pikseli potwierdza pełne nagłówki.

Final272 przywraca16kart/3kamery/8preferencji i chronione dane/opcje. Entry,
rejestr,stan,tematy usunięte; tokeny odwołane,faults[]. Niezależny SSH audit
przeniósł4exact własne pliki QA poza custom_components po wyładowaniu.
Trasa79klatek/54sourceFPS,avg16805/max23134us,failed0,segments1. FreePSRAM4880,
internal27,largest3328KiB,JPEG917,work/scroll/close0; stałe pule identyczne.
RóżnicaPSRAM−4KiB względem83 odpowiadaJPEG+5KiB; brak dowodu trwałej straty
lub przyspieszenia. DSIrecovered/rejected/invalid0. Pomiar źródła, nie panelFPS,
audio/lifetime. Native45 bez zmian; brak nowego build/flash/commit/stage/push.

## Długie opisy — HA88

W2/ha88-media-caption-scoped-acceptance.json:763Python(3skip)/379Node/7focused,
39canonical=frozen88=installed. Native Home ma136px Roboto16. Wspólny istniejący
formatter mierzy nazwę i dodaje widoczne..., zamiast niewidocznego obcinania.
CaptionyPLEN są współdzielone z edytorem i związane ze świeżym indeksem stanu.
Nie skracamy opcji ani wartości polecenia. RealCoreMediaPlayer provider z
Bluetooth Living Room Speaker / HDMI2-Salon-Telewizor / Żółty:8przypadków,
11oryginałów incl2perf; pełny target HDMI 2 - Salon - Telewizor trafił do
Core/MQTT przedfeedback. Pełne nazwy są widoczne w Choice, compact wPLEN na
Home. Final88browser/review/twoUndo/noSave potwierdza ten sam opis. Cleanup
278/16kart/3kamery/8prefs/data/protected95,ownentry/registry/state/topics
absent/tokenrevoked/faults[]; niezależny SSHarchive4exact QAfiles.
Trasa79klatek/53sourceFPS,avg16298/max30282us,failed0/segments1;52–55wcześniej.
PSRAM4886/internal27/largest2816KiB,JPEG911,work/scroll/close0,fixedpools same,
DSIrecovered/rejected/invalid0. Free+2KiB vs87 odpowiadaJPEG−2; brak dowodu
trwałej straty/przyspieszenia. Native45 bez zmian; brak nowego flash/publikacji.
