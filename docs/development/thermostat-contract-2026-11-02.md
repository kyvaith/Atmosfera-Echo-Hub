# Dedykowany termostat — kontrakt następnego pakietu

Widok z większym pierścieniem i gestem działa na native71 / HA98. Odczyt kotła był pasywny, a zmianę
nastaw sprawdzono na osobnej encji MQTT. Użytkownik może wybrać akcję
**Otwórz termostat** dla kafelka z encją Climate. Widok sam wykrywa, czy
udostępnić przyciski nastawy.

Kropka śledzi zaokrągloną do kroku nastawę. Po puszczeniu panel wysyła jedną
wartość, a podpis rozróżnia podgląd od potwierdzenia HA. Na testowej encji
przeciągnięto od 21,5 do 26°C i potwierdzono, że aktualizacja nastawy z HA
w trakcie gestu anuluje lokalny wybór. Osobny zrzut pokazuje Iwona Pellets
w trybie podglądu.

Odebrano wygląd PL/EN, zakres i pierścień w kolorze akcentu, zmianę bieżącej
temperatury i aktywności, dwie potwierdzone zmiany nastawy oraz podgląd bez
uprawnień do edycji wartości spoza kontraktu liczbowego. Parametry histerezy
pozostają osobnym punktem zależnym od interfejsu providera.
[Bieżący checkpoint i dowody](resume-2026-10-31.md).

## Potwierdzony provider

Zainstalowany `custom_components/iwona_pellets/climate.py` ma SHA256
`20df78e8e630e9abd6e29ab958e2d416cd5dc68c6b4fe18f50cc01c95f6f9de0`.
`target_temperature` czyta `set-boiler-temp-pellet`. `async_set_temperature`
przekazuje `float(temp)` do API, a następnie odświeża coordinator. Samo
rzutowanie na float nie definiuje dopuszczalnego kroku urządzenia. Wcześniejszy
odczyt rzeczywistych atrybutów Climate nie zawierał `target_temp_step`.
Nie wolno wywnioskować kroku 1°C lub 0,5°C z wyglądu dotychczasowej nastawy.
Dowód odczytu: `C:/aeh-build/notification-center-20261102/thermostat-provider-contract.json`.

## Kolejność implementacji

1. Dodać profil Climate do istniejącego właściciela sesji szczegółów sterowania.
   Nie tworzyć drugiego regulatora ogrzewania ani osobnego surowego framebufferu.
   HA pozostaje właścicielem autoryzacji, capabilities, jednostki i wykonania usługi.
2. Widok M3 Expressive: duża nastawa pośrodku, temperatura bieżąca, statyczny
   pierścień zakresu, rzeczywisty stan grzania/chłodzenia i przyciski +/-.
   Pierścień odświeżać po zmianie danych, bez ciągłej animacji pełnego ekranu.
   Kolory i kontrast biorą istniejące role motywu. Teksty biorą i18n.
3. Regulację dopuścić po otrzymaniu poprawnego zakresu i dodatniego kroku z
   providera. Przy brakujących danych pokazać stan i przyczynę niedostępności
   regulacji. Ewentualny jawny override kroku musi mieć osobny kontrakt HA oraz
   walidację; nie zastępować nim brakującej informacji po cichu.
4. Zastosuj korzysta z istniejącej sesji, revision/card ID i potwierdzenia nowego
   odczytu. Samo otwarcie widoku, zmiana profilu i powrót z powiadomienia nie
   wywołują usługi. Zachować bieżącą politykę zamykania wspólnego sterowania
   przez powiadomienie, dopóki osobny kontrakt uwagi nie zostanie rozszerzony.
5. Histerezę udostępnić wyłącznie dla jawnie opisanej encji/usługi providera.
   Dla regulatora z osobnymi cold/hot tolerance są to dwa parametry, nie jeden
   wymyślony suwak. `target_temp_step` ani zakres `heat_cool` nie są histerezą.
   Obecny audyt nie wykazał takiego interfejsu u użytkownika.
6. Testy host: zakres/jednostki, brak capabilities, źródłowe potwierdzenie,
   uprawnienia i brak polecenia przy wejściu/wyjściu. Firmware, realny ekran,
   screenshoty i jedna trasa wydajności dla całego pakietu. Fizyczne grzanie
   wymaga osobnego uzgodnionego scenariusza; nie używać kotła jako fikstury QA.

Rozszerzenie musi utrzymać pojedynczy aktywny gest/sesję i istniejące
pause/drain, snapshot readiness oraz deterministyczne zwolnienie pamięci.
