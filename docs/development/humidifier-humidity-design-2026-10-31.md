# Docelowa wilgotność — HA59

Status: odbiór zakresu HA60/native45/157.630Python(3skip)/314Node; rzeczywisty
MQTT i urządzenie:5nastaw przedfeedback,0power/mode,21oryginałów, edytor/Undo,
55sourceFPS/failed0 i dokładne przywrócenie konfiguracji. Szczegóły i granice
dowodów w [walidacji](validation-2026-10-31.md). Fizyczny aktuator niepodłączony.

Jawna karta v3 używa `control: number`, `property: humidity` dla domeny
`humidifier`. Obecna nastawa pochodzi z atrybutu `humidity`, a nie z pomiaru
`current_humidity`. Zakres wymaga rzeczywistych `min_humidity` i `max_humidity`
w granicach0..100. Wartości granic i kroku muszą być skończone i całkowite.
Raportowany `target_humidity_step` jest zachowany dokładnie. Gdy atrybut jest
nieobecny, krok1 wynika z całkowitoliczbowego kontraktu usługi Core; obecne
None, bool lub ułamek nie oznaczają kroku domyślnego. Nie zgadujemy nastawy.
Niepełny ostatni przedział pozostaje poza siatką, zgodnie z NumericDomain.

Właścicielem sesji, generacji stanu, autoryzacji, wykrywania A-B-A i jedynego
wywołania jest istniejący EntityControlOwner/Number. Polecenie to wyłącznie
`humidifier.set_humidity`, pole `humidity` z dokładną wartością int. Tryb i
zasilanie mają odrębne adaptery. Nie jest wymagany bit MODES. Nieznana nastawa,
wartość poza siatką lub nieznane zasilanie blokują kroki. Zmiana zakresu albo
kroku unieważnia sesję; potwierdzenie pochodzi z rzeczywistego stanu HA.

Urządzenie wykorzystuje istniejące app6, kontrolkę Number i jej cykl życia na
głównym zadaniu LVGL. Nie dodajemy zadania, timera, subskrypcji ani bufora obrazu.
Edytor wymaga jawnego przeglądu zmiany i zachowuje Undo, recovery oraz przenoszenie
kart. Podgląd nie wysyła usługi.

Źródłem kontraktu jest kod zainstalowanego Core2026.7.1:
`C:/aeh-build/feature-continuation-20261031-next/installed-humidifier-source.json`.
Core waliduje int0..100, sprawdza granice encji i przekazuje liczbę do providera.
Źródło ogólnego modelu encji: [Home Assistant developer documentation](https://contributors.home-assistant.io/core/entities/humidifier/).

Sprawdzone: rzeczywisty MQTT command-before-feedback, zero poleceń power/mode,
granice, None/off-grid, A-B-A podczas dotyku, zmiana zakresu/kroku, utrata dostępności,
powrót, PL/EN, oryginalne zrzuty800x800, edytor review/Undo bez Save, dokładne
przywrócenie chronionej karty i8 preferencji, FPS/pamięć/diagnostyka. Fizyczna
reakcja nawilżacza pozostaje odrębnym testem bez podłączonego aktuatora.
