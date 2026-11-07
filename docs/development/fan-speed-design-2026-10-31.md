# Wybór biegu wentylatora — HA63, odbiór ograniczony

Status: odebrane HA63/native45/169 w zakresie realnego MQTT/HA/native/visual/
browser/cleanup i krótkiego pomiaru wydajności.657Python(3skip)/327Node,
6poleceń przedfeedback/21oryginałów. Szczegóły: validation-2026-10-31.md.

Jawny v3 Choice/propertypercentage używa istniejącej app6 i ośmiu wierszy.
Pierwszy zakres obejmuje1..7rzeczywistych biegów plus0%. Odczytujemy załadowaną
FanEntity.speed_count i wymagamy zgodnego jawnego percentage_step=100/count,
SET_SPEED1 i zarejestrowanego fan.set_percentage. Brak komponentu/liczby biegów,
zbyt duży count lub rozbieżny krok wyłącza tę funkcję, bez fikcyjnego katalogu.

Wartości wylicza publiczny helper Core ranged_value_to_percentage; weryfikujemy
rosnące całkowite0..100 oraz roundtrip przez percentage_to_ranged_value.
Zainstalowany Core2026.7.1:3biegi dają0/33/66/100,6biegów0/16/33/50/66/83/100.
Nie używamy równomiernej siatki ułamkowej ani zaokrąglenia bieżącego procentu.
Wysyłana jest dokładna całkowita wartość fan.set_percentage. Etykiety dodają %,
ale nie są źródłem wartości polecenia. Obserwujemy zgłoszone percentage niezależnie
od power/preset; None,off-list,outage lub zły typ nie stają się zerem.

Zmiana prędkości może uruchomić lub zatrzymać wentylator zależnie od integracji;
edytor i review mówią to jawnie. Nie wysyłamy osobnej usługi power/preset,
kierunku ani oscylacji. Potwierdzenie dotyczy zgłoszonego procentu, nie ruchu
silnika. Captured Choice domain/generation/authorization/service fence pozostają
właścicielami sesji. Zmiana count/kroku/capability unieważnia poprzedni katalog.

Nie dodajemy bufora, taska, timera, subskrypcji ani native protokołu. Wymagane:
realne MQTT z range1..3 i1..7, broker-before-feedback z fizycznym kodem biegu,
zero/off/preset/unknown/ABA/count/capability/outage, PL/EN, browser review/Undo,
oryginalne screenshoty i post-performance. Silnik fizyczny, paginacja większych
katalogów i ciągły speed scalar pozostają osobnymi etapami.

Źródła lokalne W2/installed-fan-speed-source.json i
installed-fan-speed-oracle.json przypinają Core fan/MQTT/percentage/scaling.
Oficjalny kontrakt: https://contributors.home-assistant.io/core/entities/fan/.

Core usuwa percentage_step w stanie unavailable; wtedy katalog traci wymagane
metadane i sesja jest unieważniana. Po powrocie należy otworzyć świeży wybór.
