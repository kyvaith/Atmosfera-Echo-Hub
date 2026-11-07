# Precyzyjna temperatura barwowa — HA62, odbiór ograniczony

Status: odebrane HA62/native45/163 w zakresie realnego MQTT/HA/native/visual/
browser/cleanup i krótkiego porównania wydajności.648Python(3skip)/323Node,
5dokładnych poleceń przedfeedback,22oryginały. Szczegóły w validation-2026-10-31.md. Pierwszy fragment to dokładne dostrajanie co1K; szeroki
suwak/picker oraz RGB są odrębnymi dalszymi częściami W08.

Jawna karta v3 Number/propertycolor_temp_kelvin korzysta z app6, istniejących
przycisków i Number ownera. HA wymaga rzeczywistego supported_color_modes z
color_temp, jawnych całkowitych min/max w dopuszczonym produktem1000..20000K
oraz zarejestrowanego light.turn_on. Granice nie mają wartości zastępczych.
Krok1K pochodzi z całkowitej jednostki usługi Core, nie udaje kroku sprzętu.

Odczyt to wyłącznie rzeczywiste color_temp_kelvin w on/color_modecolor_temp.
Off, inny tryb, None, brak klucza, ułamek, wartość poza zakresem lub outage dają
nieznaną wartość i zablokowane przyciski. Nie podstawiamy ostatniej temperatury,
wartości środka ani konwersji z RGB. Zmiana zakresu/capability unieważnia sesję;
zmiana stanu oraz A-B-A przechodzą przez istniejącą generację i autoryzację.

Jedyna usługa to light.turn_on(color_temp_kelvin=exactint); bez jawnych pól
brightness/rgb/effect lub osobnego power. Core może stosować swoje profile i
przejście, a integracja lampy może kwantyzować kelwiny. Dopiero zgłoszony dokładny
stan potwierdza dopasowanie; samo przyjęcie usługi tego nie dowodzi.

Nie dodajemy bufora, zadania, timera, subskrypcji ani protokołu native. Testy
wymagają realnej własnej MQTT JSON light, broker-before-feedback, on/off/innego
trybu, missing/None/fraction/range/capability/ABA/outage, PL/EN, przeglądarkowego
review/Undo, oryginalnych screenshotów i porównania wydajności. Fizyczna lampa
nie jest podłączona. Źródło Core2026.7.1 jest przypięte w poprzednim badaniu
installed-light-effects-source.json; state_attributes publikuje temperaturę
tylko w aktywnym color_temp. Oficjalny kontrakt światła:
https://www.home-assistant.io/integrations/light/.
