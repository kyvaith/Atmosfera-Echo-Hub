# Wybór efektu światła — HA61, odbiór ograniczony

Status: HA61/native45/161 odebrane w zakresie MQTT/HA/native/visual/browser/cleanup
i krótkiego pomiaru wydajności.640Python(3skip)/319Node;23oryginały,5poleceń
przedfeedback. Fizyczna żarówka i długi test pozostają odrębne. RGB i temperatura
barwowa pozostają osobnymi punktami planu. Szczegóły: validation-2026-10-31.md.

Jawna karta v3 `choice/property: effect` dotyczy wyłącznie `light`. Wymaga
rzeczywistego EFFECT4, zarejestrowanego `light.turn_on`, pełnej listy
`effect_list`1..8 rozróżnialnych nazw po najwyżej32bajty UTF-8. Etykiety mogą
pochodzić z cache tłumaczeń atrybutów HA; wysyłana jest zawsze dokładna nazwa
z katalogu źródłowego, niezależna od tłumaczenia.

Core publikuje `effect: None`, gdy światło jest wyłączone. Jest to jawny brak
aktywnej opcji, a nie utrata łączności. Dzięki istniejącej negocjacji empty1
można wybrać efekt od takiego stanu; native45 nie ma lokalnego kandydata, dopóki
użytkownik nie wybierze opcji. Brak klucza, błędna wartość, nieznany stan zasilania
lub wyłączone światło z zachowaną niepustą nazwą nie udają aktywnego efektu.
Literalna nazwa `none` w katalogu pozostaje zwykłą opcją, odrębną od None.

Właścicielem sesji, generacji, autoryzacji i pojedynczej usługi pozostaje
ChoiceControlPolicy/EntityControlOwner. Wysyłamy tylko `light.turn_on(effect=...)`.
Jest to uruchomienie efektu i może włączyć światło, co musi jasno opisywać edytor
i okno potwierdzenia. Core może zastosować własne profile/domyślne parametry
światła; nie obiecujemy niezmienionej jasności ani kolorów po tym wywołaniu.
Potwierdzenie wymaga rzeczywiście zgłoszonego efektu w stanie `on`.

Zmiana listy, bitu funkcji, tłumaczeń lub utrata usługi unieważnia sesję.
Zmiany/utrata bieżącej opcji podlegają istniejącej generacji i blokadzie A-B-A.
Nie ma nowego zadania, timera, subskrypcji, protokołu ani bufora. Urządzenie używa
app6 i ośmiu istniejących przycisków Choice. Jasność i domyślne sterowanie światłem
zachowują osobne akcje. Opis wybranej karty pokazuje efekt, nie sam stan zasilania.

Źródła: kod zainstalowanego Core2026.7.1 w W2/installed-light-effects-source.json
oraz installed-light-effects-constants-source.json. Core `state_attributes`
zeruje widoczny efekt przy off; `filter_turn_on_params` wymaga EFFECT4;
`process_turn_on_params` może stosować profile. MQTT JSON obsługuje pole effect
i publikuje polecenie stateON/effect. Weryfikacja wymaga rzeczywistego własnego
MQTT JSON, broker-before-feedback, pustego znanego wyboru/None kontra literal,
outage/ABA/list/reorder/capabilities, PL/EN, edytora review/Undo, oryginalnych
zrzutów i pomiarów. Niepodłączona fizyczna żarówka pozostaje odrębną bramką.
