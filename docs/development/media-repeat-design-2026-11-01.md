# Powtarzanie mediów HA — W14 / MED003

Stan: ograniczony odbiór native45 / HA87 / układ276 zakończony.

Zainstalowany Core2026.7.1 definiuje RepeatMode off/one/all, bit REPEAT_SET262144
i usługę media_player.repeat_set z wymaganym repeat, koercja do RepeatMode.
Provider otrzymuje async_set_repeat(repeat). Źródła i hashe:
W2/media-repeat86-installed-contract.json; dokumentacja:
https://www.home-assistant.io/integrations/media_player/ .

HA posiada mapowanie, tłumaczenia, bieżący stan i dispatch. Lista off/one/all
pochodzi z publicznego kontraktu Core, a nie ze zgadywania katalogu urządzenia.
Native45 posiada dotychczasowy Choice/Apply, sesję, bufor kontrolki i snapshoty.
Nie dodajemy protokołu, aplikacji, tasków, pollingów, buforów ani subskrypcji.
Wybór lokalny jest kandydatem; dopiero Apply wysyła dokładną wartość. Stan,
odtwarzanie, utwór, głośność i shuffle nie są zmieniane optymistycznie.

Active state i bit są ponownie sprawdzane. Brak lub nieprawidłowy repeat nie
oznacza off i nie wybiera pierwszej opcji. Core StrEnum normalizujemy dopiero
po sprawdzeniu przynależności do dokładnego zbioru. Utrata obsługi/połączenia,
off/standby, zmiana stanu podczas autoryzacji unieważniają stare polecenie.
Home dodaje kontekst „Powtarzanie”, aby off nie wyglądało jak wyłączenie całego
odtwarzacza. Etykiety z HA mają pierwszeństwo przed pakietem PL/EN.

Plan odbioru: real izolowana CoreMediaPlayerEntity, własneMQTT, trzy exact
polecenia one/all/off przedfeedback, redundant/heldABA/outage/featureloss/
unknown/off-window/PLEN, prawdziwy browser/review/Undo/noSave,800×800,cleanup
i pomiar. Faktyczne zapętlenie fizycznego odtwarzacza i dotykGT911 osobno.

## Odbiór

W2/ha87-media-repeat-scoped-acceptance.json wiąże39canonical=frozen87=live,
762Python(3skip)/378Node/7focused/criticalRuff/normaldiff pass.86 zakończył23
scenariusze i3exactkomendy one/all/off z potwierdzonym provider_typeRepeatMode
przedfeedback. Brak zmian playback/volume.42/muteFalse/shuffleFalse/titleTrackQA.
Redundant,heldABA,featureloss,missing/invalid/bool repeat,off/standby/unknown/
offline/off-window/PLEN przeszły. Odbiór wizualny86 odrzucił Homecaption:
172px „Powtarzanie: wyłączono” w istniejącej etykiecie136px Roboto16. Zachowano
oryginał.87 skraca prefix do „Powt.:”, mierzy136px i stosuje widoczne... dla
długich tłumaczeń. HA/editor dzielą te same captiony; wartości usług bez zmian.
Final87:12przypadków/1kolejna exactkomenda, sześć Homecaptionów off/one/all
wPLEN oraz dwa Choice screens i rzeczywisty browser87/review/dwaUndo/noSave.
Razem35przypadków,39oryginałów (24historyczne86/13końcowe87/2pomiarowe),
przejrzane contact/pairedreview. Nie opisujemy historycznego86 jako visualPASS.

16kart/3kamery/8preferencji i chronione opcje/dane odtworzono;276. Entry,
registry,stan,tematy usunięte, tokeny odwołane,faults[]. Niezależny SSHaudit
archiwizuje4exact własne pliki poza custom_components po wyładowaniu.
Trasa79klatek/53sourceFPS,avg16906/max24447us,failed0,segments1;52–55wcześniej.
FreePSRAM4884/internal27/largest2176KiB,JPEG913,work/scroll/close0; pule stałe
identyczne. Free+4KiB odpowiadaJPEG−4KiB względem85; brak dowodu przyspieszenia
lub trwałej straty. Native45 bez zmian; brak nowego build/flash/commit/push.
