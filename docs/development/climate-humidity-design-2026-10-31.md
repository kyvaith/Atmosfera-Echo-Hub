# Docelowa wilgotność Climate — HA64, odbiór ograniczony

Status: odebrane HA64/native45/171 w zakresie realnego MQTT/HA/native/visual/
browser/cleanup i krótkiego pomiaru wydajności.664Python(3skip)/330Node,5intcommands
przedfeedback,23oryginały. Szczegóły: validation-2026-10-31.md.

Rozszerzyć istniejący v3 Number/propertyhumidity na domenę climate przy
rzeczywistym TARGET_HUMIDITY4, zarejestrowanym climate.set_humidity i jawnych
całkowitych min_humidity/max_humidity0..100. Wspólny humidity_domain posiada
walidację opcjonalnego dodatniego całkowitego target_humidity_step; brak oznacza
całkowitą jednostkę usługi1, a jawne None/bool/ułamek są odrzucane.

Odczyt dotyczy target humidity, nie current_humidity. Każdy znany tryb HVAC,
także off/auto/heat_cool, może mieć niezależną nastawę wilgotności. Unknown,
off-grid, brak wartości lub outage nie mogą podstawiać pomiaru ani środka zakresu.
Zmiana zakresu/kroku/feature unieważnia sesję. Istniejący Number owner posiada
generację, A-B-A, autoryzację i pojedynczą usługę. Jedyna wysyłka to dokładny
int w climate.set_humidity, bez pól temperatury lub hvac_mode.

Użyć istniejących app6 i Number widgets, bez nowego bufora, taska, timera,
subskrypcji lub protokołu. Edytor musi rozróżniać facet Climate od humidifier,
mieć jawne review/Undo i podgląd rzeczywistej docelowej wartości. Polityka
powinna rozszerzyć współdzieloną walidację wilgotności bez kopiowania maszyny
stanów ani tworzenia drugiego właściciela.

Odbiór: realna własna MQTT Climate z humidity target/state/current i osobnym
trybem HVAC; feature4 bez nastawy temperatury; min/max/step, None/off-grid,
auto/off/heat_cool, target A-B-A, zmiana feature/range/outage, PL/EN. Dokładny
broker-before-feedback, brak usług HVAC/temperatury, oryginalne screenshoty,
rzeczywisty edytor oraz pomiar/cleanup. Fizyczny układ HVAC pozostaje odrębny.

Źródła: W2/installed-climate-humidity-source.json odczytany z Core2026.7.1;
climate/__init__ SHA69f7b794cf4e76ab814898eb2d6cc908d9a7315e684c4c697ce346df990eb312,
MQTTclimate SHA98420e70bba64294aa86cdbc1878dc48d33dcadb70504fbc3aadde72281ccb04.
Core wymaga TARGET_HUMIDITY4 i konwertuje usługę do int oraz sprawdza min/max.
Dokumentacja: https://www.home-assistant.io/integrations/climate/.
