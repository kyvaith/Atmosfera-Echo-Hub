# Pilot: jawne zasilanie — HA78, AEH-CTL-024

Stan: ograniczony odbiór native45 / HA79 / układ259 zakończony.

Pierwszy fragment W19 dodaje encje `remote.*` do katalogu oraz dwie jawne akcje
`remote.turn_on` i `remote.turn_off`, bez dodatkowych pól. Nowa karta jest bierna
do jawnego wyboru. Stan musi być dokładnie on/off; włączenie jest dopuszczalne
tylko z off, wyłączenie tylko z on. Rejestracja usługi jest sprawdzana ponownie
przy dotknięciu. Brak/unknown/unavailable, karta informacyjna/ukryta, domyślna
akcja, toggle i ogólne homeassistant.* nie powodują sterowania.

Core2026.7.1 rejestruje power dla podstawowego RemoteEntity bez feature bit.
Flagi LEARN_COMMAND1/DELETE_COMMAND2/ACTIVITY4 dotyczą innych funkcji, więc
brak tych flag nie blokuje zasilania. Dokładne zainstalowane źródło Remote:
SHA256 `44d44ae31e72942d93c23bd41a281752587c6435efe6da7d76a822f440a148dc`.
Źródła i hashe zachowano w W2/installed-remote-source-20261101.json.
Dokumentacja: https://www.home-assistant.io/integrations/remote/ .

HA posiada konfigurację, stan i dispatch; frontend wybiera wyłącznie szkic,
z Undo i jawnym Save. Przyciski korzystają z istniejącego stylu M3 i chronią
fokus/scroll jak wybór Vacuum. Metadane są związane z aktualnym stanem i usługą.
Native45 posiada istniejący kontekst tap/revision i generację press_enabled,
snapshoty oraz cały obraz. Nie dodajemy pól wire, buforów, tasków, timerów,
subskrypcji ani lambd YAML. Caption pochodzi ze stanu i tłumaczeń HA, nie z
optymistycznego wyniku komendy. Starzy peers zachowują dotychczasowy wire;
edytor oferuje nowe przyciski tylko przy obsłudze aktualnego kontekstu press.

Aktywności i ich katalogi, nauczone komendy, keypad oraz fizyczny IR/RF są
oddzielnymi fragmentami. Nie wymyślamy wspólnego katalogu komend różnych
integracji i nie dodajemy uczenia/usuwania komend do pierwszego fragmentu.

Plan odbioru: izolowana rzeczywista Core RemoteEntity (supported_features=0),
której wejście/wyjście przechodzi przez własne tematy MQTT. Własny tymczasowy
komponent QA jest poza kodem produktu i nie ma nadajnika IR/RF. Potwierdzić
native tap → jedną dokładną usługę → jeden broker message przed feedback;
redundant/offline/unknown/held ABA/drag/off-window, PL/EN, browser/Undo/noSave,
oryginały 800×800, cleanup i pomiar. Nie jest to test fizycznego pilota.

## Odbiór 1 listopada

W2/ha79-remote-power-scoped-acceptance.json wiąże 39 plików canonical=frozen79=
installed z testami i dowodami. 735 Python (3 skip), 365 Node końcowego79,
critical Ruff i zwykły git diff --check przeszły. Backend78 i79 jest identyczny;
79 zmienia tylko markup przycisków na istniejące większe operation-options M3
oraz wersje assetu/manifestu.

Rzeczywista własna Core RemoteEntity bez nadajnika IR/RF otrzymuje stan przez
MQTT. Dwa natywne tapy wysłały dokładne turn_on/turn_off z wyłącznym entity_id
oraz po jednej wiadomości MQTT przed feedback. 13 scenariuszy78 potwierdziło
redundant, offline, unknown, held ABA, drag, off-window i PL/EN, z 14 oryginałami.
Osobny odbiór końcowego79 potwierdził natywną kartę, większe przyciski browsera,
wybór Off/On, dwa Undo i czysty szkic bez Save/nowych usług aktuatora. Nie
przeniesiono ACK ze starej kampanii. Łącznie18 oryginałów 800×800 (2 pomiarowe)
przejrzano, nagłówki są pełne; zachowano hashe i contact sheets.

Pierwszy test nie związał układu: własny provider podał int0, a Core Remote
state_attributes wymaga RemoteEntityFeature(0). Błąd i oryginalne źródła QA
zachowano. Poprawiono wyłącznie provider, zrestartowano Core i wykonano V2.
To nie była poprawka produktu. Po końcowym teście entry/rejestr/stan/tematy
usunięto. Niezależny SSH audit potwierdził brak referencji, a cztery pliki QA
przeniósł poza custom_components, z kontrolą hashy. Tokeny odwołane, faults[].

16 kart, 3 kamery, 8 preferencji i chronione dane/opcje pozostały zachowane;
rewizja wzrosła do259 wyłącznie przez jawne bindingi i ich inverses. Po restarcie
Core część innych istniejących encji zgłaszała unknown; ich bindingów nie
zmieniano i nie deklarujemy sprawności fizycznych urządzeń na tej podstawie.

Końcowa trasa:80 klatek źródłowych/54 FPS, avg16527/max23911 μs, failed0,
segments1. PSRAM4878 KiB/internal27, largest3712; app_work/scroll/close0,
stałe pule jak przy HA77. Jest to zgodne z poprzednim zakresem, bez dowodu
panel FPS, audio lub lifetime. Fizyczny pilot/GT911, aktywności i keypad
pozostają osobnymi bramkami. Bez nowego firmware/build/flash/commit/push.
