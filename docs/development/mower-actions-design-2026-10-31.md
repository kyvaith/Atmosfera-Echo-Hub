# Jawne akcje kosiarki — HA73, odbiór ograniczony

Status: odebrany zakres native45/HA73/226. Fragment CTL015/W19.
6exact services/broker before feedback,26oryginałów/browser/cleanup; standardowa
trasa53sourceFPS/failed0. Pełne dowody: validation-2026-10-31.md.
Istniejące ogólne schematy usług nie były pełnym odbiorem funkcji kosiarki.
Dodajemy prosty wybór działania w edytorze oraz dynamiczną dostępność dotyku,
korzystając z istniejącego kontraktu press_enabled native45. Bez nowego ekranu,
bufora, timera, taska, protokołu i automatycznego startu przy dodaniu encji.

Każda karta ma jedno jawnie wybrane polecenie: start_mowing (także wznowienie),
pause albo dock, wyłącznie dla rzeczywistej usługi i flagi Core1/2/4.
Przyciski w edytorze zmieniają tylko szkic, z Undo/Redo; nie wysyłają usług.
Nowa karta domyślnie actionnone. Zapis layoutu nadal jest zwykłym flow edytora.

Produktowa polityka wykonania, sprawdzana ponownie w HA przy dotknięciu:

| Polecenie | Dozwolony zgłaszany stan |
| --- | --- |
| start_mowing | docked, paused |
| pause | mowing, returning |
| dock | mowing, paused |

Error, unknown, unavailable, nieznany stan/feature i brak usługi blokują dotyk.
Nie powtarzamy redundantnego ruchu i nie wybieramy innego polecenia w zastępstwie.
Katalog nadal opisuje możliwości konfiguracji, a eligible opisuje obecną
dostępność wykonania; można przygotować kartę Pauza gdy kosiarka jest w bazie.
Stan na kafelku pochodzi z HA, nie z wysłania komendy; tłumaczenia HA mają
pierwszeństwo, krótkie brakujące etykiety PL/EN są w projekcie.

Właścicielem stanu, features i wykonania usługi jest Core/provider. HA owns
admission/projection, istniejący controller obsługuje press/revision, a wspólna
nawigacja snapshoty. Nie dodajemy drugiej pętli oczekiwania/ponawiania ani
optymistycznie nie udajemy ruchu. Powrót do bazy nie jest potwierdzeniem postoju.

W2/installed-mower-source.json pinuje faktyczny Core2026.7.1 i MQTT. Ten Core
ma5stanów i3akcje; aktualne dokumenty opisują już idle i stop, których tutaj
nie ma. Nie dodajemy nieistniejącej usługi ani nie aktualizujemy całego HA.
Core SHA c98b35631c7d14a56899cae7818174e0cea9ca3fb8876147bf58a9e8cc865351,
MQTT SHA22a597192dc7258082629b50101a2e5a59ce647910b80ce978d8f9a7c8458ec4.
[Lawn mower](https://www.home-assistant.io/integrations/lawn_mower/),
[MQTT](https://www.home-assistant.io/integrations/lawn_mower.mqtt/).

Odbiór: host/Node/static i rzeczywista własna MQTTmower, optimisticfalse.
Start→feedback mowing, pause→paused, resume, dock→returning→docked, exactbroker
przed feedback i brak komend przy disabled/feature loss/unknown/outage/error,
gesture cancel/held change. Realny browser wybór/Undo/noSave, oryginały urządzenia,
performance i exact inverse wyłącznie własnej karty. Fizyczna kosiarka osobno.
