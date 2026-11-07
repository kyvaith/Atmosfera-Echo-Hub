# Stop odtwarzacza HA — W14 / MED003

Stan: ograniczony odbiór native46 / HA92 / układ294 zakończony. Play,Pause,Next i Previous były już dostępne jako akcje kart.
Rzeczywisty brak dotyczył media_stop: nie było go w dozwolonym schemacie,
mapowaniu capabilities ani w konfiguracji edytora.

Zainstalowany Core2026.7.1 rejestruje media_player.media_stop bez danych i wymaga
STOP4096. Źródła z hashami: W2/installed-media-player-source-20261101.json oraz
media-transport92-core-contract.json. HA92 dodaje to jedno jawne polecenie,
bez zmiany dotychczasowego Play/Pause ani sterowania lokalnym Player/Sendspin.

Konfiguracja wymaga znanego źródła on/off/standby/idle/playing/paused/buffering,
bitu4096 i obecnej usługi. Pozwala przygotować kafelek także dla nieaktywnego
odtwarzacza. Natomiast wykonanie jest dostępne tylko w playing/paused/buffering;
on/off/standby/idle,unknown/unavailable i utrata obsługi blokują tap na urządzeniu.
Pola dodatkowe, inny entity_id w danych i źródło nie-media_player są odrzucane.
HA wysyła entity_id bez innych danych, a Core wywołuje async_media_stop().

Opis kafelka i podglądu pokazuje obserwowany stan, nie przewidywany wynik Stop ani
zachowany tytuł utworu. Pierwszeństwo mają tłumaczenia HA; brakujące stany mają
ograniczony polski/angielski fallback. Prefiks Stan:/State: i mierzone136px
zapewniają opis w jednym wierszu. Zwykła karta MediaPlayer zachowuje swój tytuł
utworu i dotychczasową akcję domyślną. Przyjęcie usługi nie zmienia stanu źródła;
stan zmienia dopiero raport integracji danego odtwarzacza.

Własność: adapter HA posiada capability/eligibility/tłumaczenie i dispatch,
Core/provider wykonuje polecenie, native46 zwykły kontekstowy tap i istniejące
snapshoty. Edytor ma skrót M3 do szkicu/Undo; podgląd niczego nie odtwarza.
Bez nowego protokołu, sesji, widoku, bufora, tasku, timera, subskrypcji i bez
zmian w forku lub właścicielu I2S. Korzystamy z naprawionego raw deferred press
w native46.

Plan odbioru: rzeczywista własna CoreMediaPlayerEntity z STOP4096 i własnymMQTT.
Trzy dokładne Stop w playing/paused/buffering, bez zmian źródła przedfeedback;
idle/on/off/standby/unknown/outage/featureloss,heldABA,drag,off-window,PLEN,
browser/Undo/noSave,35+ zrzutów,performance i odwrócenie tylko własnych pól.
Fizyczne zatrzymanie dźwięku i GT911 są oddzielnymi bramkami.

## Odbiór


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

Receipt: W2/ha92-media-stop-scoped-acceptance.json. Własny wpis, rejestr, stany
i tematy testowe usunięto, token odwołano, cztery dokładne źródła zarchiwizowano
poza aktywnym custom_components. 39 plików canonical=frozen92=installed.
