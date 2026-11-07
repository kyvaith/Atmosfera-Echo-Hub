# Stała docelowa głośność odtwarzacza HA

Stan: ograniczony odbiór native46 / HA93 / układ298 zakończony.

To kolejny fragment W14/MED003: kafelek może ustawić skonfigurowaną głośność,
np. „Cicho” na20%. Edytor podaje poziom w procentach0..100, a publiczna usługa
`media_player.volume_set` otrzymuje dokładną wartość0..1. Zainstalowany Core
2026.7.1 wymaga VOLUME_SET4; samo VOLUME_STEP1024 nie wystarcza.
[Kontrakt publiczny HA](https://www.home-assistant.io/integrations/media_player/),
[model encji](https://contributors.home-assistant.io/core/entities/media-player/).

Kafelek i podgląd pokazują raportowaną głośność, np.42,5%, aż źródło potwierdzi
zmianę. Nie zaokrąglają jej do wymyślonej siatki ani nie zmieniają play/mute/source.
Edytor tworzy akcję z obecną wartością jako jawnym punktem startu szkicu, pozwala
wpisać własny procent i obsługuje Undo. Samo przygotowanie/zapis konfiguracji
niczego nie wysyła do odtwarzacza. Zwykły tap na urządzeniu wysyła jedno polecenie.
Gdy cel jest dokładnie równy raportowanej wartości, tap pozostaje wyłączony.

Wymagamy aktywnego on/idle/playing/paused/buffering, skończonego numerycznego
volume_level0..1, capability4 i zarejestrowanej usługi. Off/standby/unknown/
unavailable, brak odczytu lub utrata obsługi blokują wykonanie. Polecenie zawiera
tylko entity_id oraz volume_level; cel nie zależy od zaokrąglonego opisu ani
vendorowego volume_step. Istniejący kontekstowy tap pozostaje właścicielem gestu.

Ten etap nie dodaje suwaka na urządzeniu. Istniejący Number wymaga dokładnej
wartości z kanonicznej siatki i takiej samej value_text. Dowolnego odczytu0..1
nie wolno podmienić na zaokrąglony procent: utraciłoby to obserwację drobnych
zmian/ABA i przedstawiało przybliżenie jako dokładny stan. Pełny suwak wymaga
osobnego kontraktu surowej obserwacji, prezentacji przybliżenia i potwierdzenia
wyniku. NumericDomain, protokół i firmware pozostają tutaj bez zmian.

Własność: HA przechowuje docelowy poziom i waliduje dostępność; Core/provider
wykonuje polecenie i raportuje rzeczywisty stan. Native46 obsługuje istniejący
tap i snapshoty. Bez nowych buforów, tasków, timerów, subskrypcji lub ścieżkiI2S.

Odbiór obejmie rzeczywistą własną CoreMediaPlayerEntity emitującą własny MQTT,
dokładne cele0/1 i ułamkowe, brak zmian przed feedback, dopasowany cel, utratę
capability/usługi, source invalid/outage, heldABA, drag, off-window, PL/EN,
edytor procentów/Undo/noSave, screenshoty, wydajność i ochronę układu użytkownika.
Fizyczna reakcja zewnętrznego głośnika pozostaje oddzielnym dowodem.

## Odbiór


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

Receipt: W2/ha93-media-volume-target-scoped-acceptance.json. Własny wpis, rejestr,
stany i tematy testowe usunięto, token odwołano,4 dokładne źródła niezależnie
zarchiwizowano poza aktywnym custom_components. 39plików canonical=frozen93=live.
