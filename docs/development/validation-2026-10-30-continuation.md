# Kolejne funkcje — ciągła praca od HA22

Użytkownik zlecił kontynuację do przerwania, testy na urządzeniu i screenshoty.
Wszystkie nowe źródła pozostają lokalne, bez commitów i push. Poprzedni zakres:
[Sun, biblioteka i presety timera](validation-2026-10-30.md).

## HA24: opcjonalne wyróżnianie włączonego urządzenia

Pole `state_color` jest opcjonalnym Boolean w modelu HA. Domyślnie brak pola
zachowuje wygląd starej karty. Włączenie opcji jest dostępne wyłącznie dla kart
typu entity w domenach light, switch, input_boolean i fan. Dokładne `on`
wybiera zapisaną paletę, inne stany i brak źródła wybierają surface.
Wybrana paleta w dokumencie nie zmienia się. HA nadal rozstrzyga akcje na
podstawie aktualnego stanu i uprawnień; kolor nie przewiduje wyniku dotknięcia.

Właścicielami są model/projekcja HA oraz istniejące bindingi kafelków na
urządzeniu. Użyto obecnych ról, kontrastu, akcentu urządzenia, subskrypcji i
odświeżania snapshotów. Brak nowego pola wire, taska, timera, pixmapy lub bufora.
Podgląd aktualizuje tylko istniejące style CSS, zachowując fokus, szkic i historię.
Eksport/import i odzyskanie szkicu zachowują opcję; stare dokumenty są niezmienione.

### Oddzielne wyniki i zachowane niezaliczone próby

- Pierwszy HA23 nie przeszedł testu urządzenia: `normalize_cards` usuwało nową
  metadaną, choć model ją zachowywał. Przełącznik był off, a rola pozostawała
  primary. Naprawiono adapter i dodano test entry-layout → normalization → wire.
  `state-color-v1` przywrócił wszystkie karty i usunął pomocnik; rewizja 22→24.
- `state-color-v2` zatrzymał się przed utworzeniem pomocnika i zapisem: HA po
  restarcie nie zdążył jeszcze przyjąć rewizji. Świeży odczyt API potwierdził
  następnie saved/sent/accepted=24. Nie omijano tej bramki.
- Poprawiony HA24 ma **401 testów Python OK (trzy pominięte)** i **233 Node PASS**.
  Ruff i kontrola białych znaków przeszły. Starsze dwa testy opisów formularza
  rozszerzono o nowy, celowy tekst pomocy dla światła.
- Dwa wdrożenia (HA23, następnie HA24) miały po jednym restarcie, atomową wymianę
  plików i kopię poza loaderem. Odczyt SSH HA24: 25/25 zgodnych źródeł, bez zmian
  danych wpisu. Definicje kamer i kart po kampanii są zachowane.

### Urządzenie i przeglądarka — ograniczony PASS

`state-color-v3` używał jednego własnego pomocnika input_boolean i chronionej
karty `info-20261024-15`. Dwa rzeczywiste dotknięcia przez listener LVGL dały
toggle off→on→off. Potwierdzono stany HA i zgodność kontekstów usług/stanów.
Po odejściu do Home2 operator QA włączył wyłącznie ten pomocnik. Powrót zwykłymi
gestami na Home4 pokazał primary, z wyczyszczonym pending dla slotu 15.

Oryginalne obrazy i wycinki potwierdzają ciemne surface/jasny tekst przy off oraz
pastelowy akcent/ciemny tekst przy on. Panel przeglądarkowy pokazał zapisaną,
włączoną opcję, `włączono`, tło #aee2ff i tekst #071018, z wyłączonym Zapisz.
Przeglądarka nie edytowała ani nie zapisywała konfiguracji. Zachowano osobno
obrazy podglądu i opcji. Stare połączenie automatyzacji przeglądarki odzyskano
przez reset sesji sterowania; nie zmieniano aplikacji ani źródeł, żeby to obejść.

Po kontroli przywrócono dokładne definicje wszystkich 16 kart, usunięto własny
pomocnik po potwierdzeniu odpięcia, zachowano osiem preferencji i trzy kamery.
Rewizja 24→25→26. Po zwykłych gestach wrócił kompletny Home1. Panel po reload
jest czysty, saved/sent/accepted=26. Nie wywołano usług domowych urządzeń.

Przed/po kampanii: PSRAM **4577/4577 KiB**, największy blok **3776/3776 KiB**,
internal **24/24 KiB**, snapshot **6550/6550 KiB**. raw/app_work/scroll/close=0.
Osobny pomiar rozpoczął się po zakończeniu kampanii: Home1→Home2→Ustawienia→
Home2→Home1, trim i pożyczka ciągłego bufora poprawne. **79 klatek, 54 FPS,
średnio 16331 µs, max 24166 µs, failed=0, jeden segment.** Końcowy Home przeszedł
kontrolę oryginalnych pikseli. Nie wykryto awarii ani restartu w tym zakresie.

Nie zmieniano natywnych źródeł: pozostaje zweryfikowany native31, pełny ELF
`f78afc026eb0da1d2d536560871bbf2c521134cc0858b462888eb939f5f1bd59`.
Nie wykonywano nowej kompilacji ani flashu dla zmian wyłącznie HA/edytora.
To nie jest odbiór fizycznego GT911, prawdziwego aktuatora, ciągłego audio ani
wielogodzinnego lifetime. Pełne pending/error/result pozostają osobnym punktem.

Dowody lokalne: `D:\aeh-build\feature-continuation-20261030`, w tym
`state-color-v1..v3`, `ha24-real-home`, `ha24-installed-final.json`,
`ha24-home-complete.json`, `ha23-python-fixed.log`, `ha23-node-tests.log`
oraz obie paczki i kopie wdrożeniowe. W katalogu dowodów zachowano również
niezaliczone próby; nie przepisywać ich jako PASS.

## HA25: precyzja pojedynczej karty pomiaru — ograniczony PASS

Opcjonalne `display_precision` to dokładny integer 0..6 wyłącznie dla
informacyjnych kart sensor/number/input_number. Brak pola pozostawia format
wynikający z HA. Override nie zmienia rejestru encji, źródłowej wartości, jednostki,
innych kart tej samej encji ani domeny sterowania Number. Daty, enum, timestamp,
uptime i duration zachowują dotychczasowy semantyczny formatter. Normalizer
zachowuje opcję, a wire nadal zawiera wyłącznie gotowy tekst, bez nowego pola.

Edytor ma wybór „Z Home Assistant” i 0..6. Jawny wariant liczbowy korzysta z
dziesiętnego wejścia tekstowego do Intl, halfEven, bez grupowania i z usunięciem
ujemnego zera. To nie konwersja wartości przez float. Sprawdzenie granicy 1e15
uwzględnia cyfry wejścia, także część ułamkową ponad granicą. Cache formatterów
ma co najwyżej 14 par język/precyzja, bez danych encji; nie tworzy pollera.
Bez override nadal działa istniejący formatter HA.

**407 testów Python OK (trzy pominięte), 236 Node PASS**, Ruff i kontrola białych
znaków PASS. Wspólne, jawne przykłady dla obu języków sprawdzają m.in. 2.5→2,
3.5→4, 1.245→1.24, 19.975→19.98, -0.005→0.00, notację naukową, duże dokładne
liczby i przekroczenie granicy. Test od zapisanego dokumentu przez normalizer
do projekcji chroni przed ponowną utratą metadanej. Eksport/import, zachowanie
zera, złe typy i brak wpływu na rejestr/inne karty mają oddzielne sprawdzenia.

HA25 wdrożono atomowo jednym restartem, z kopią HA24 poza loaderem; 25/25
zainstalowanych plików odpowiada źródłom. Karty i kamery nie zmieniły się
podczas instalacji. Kampania `card-precision-v1` użyła jednej własnej encji
runtime, bez usług i bez rejestracji sprzętu. Oryginalne obrazy z native31:

| Scenariusz | Podpis |
| --- | --- |
| 0 miejsc | 12 °C |
| half-even przy 2.5 | 2 °C |
| 2 miejsca | 12,35 °C |
| 6 miejsc | 12,345600 °C |
| powrót do automatycznego | 12,3456 °C |
| -0.005 przy 2 miejscach | 0,00 °C |
| unavailable | Niedostępny |
| unknown | Nieznany |

Podgląd przeglądarki pokazał zapisane 6 miejsc, następnie w szkicu poprawne
0 i 2 miejsca. Dwa Cofnij przywróciły zapisane 6 i wyłączyły Zapisz. Browser nie
zapisywał układu ani nie wykonywał usług. Zachowano obraz opcji i odczyt DOM.
W oryginalnych pikselach ikonka i tytuł przy 2/6 są identyczne; różnica ma
prostokąt tylko (51,159)–(163,177). Nie wnioskować o brakującym tytule z samego
podglądu, który potrafi pomijać powtórzone fragmenty.

Przywrócono wszystkie definicje 16 kart, trzy kamery i osiem preferencji;
usunięto encję po odpięciu i kontroli właściciela. Rewizja naturalnie wzrosła
26→32. Po normalnych gestach wrócił kompletny Home1 i czysty panel HA.
Przed/po: **PSRAM 4575/4575 KiB, największy blok 3328/3328 KiB, internal
24/24 KiB, snapshot 6551/6551 KiB**. Osobny normalny pomiar: **79 klatek,
54 FPS, średnio 16423 µs, max 26729 µs, failed=0, jeden segment**. Brak awarii
w badanym zakresie. Firmware/ELF pozostał native31; nie budowano ani nie
wgrywano nowego obrazu dla zmian wyłącznie HA/JS. Ograniczenia fizycznego
dotyku, audio i lifetime pozostają takie jak w poprzednim odbiorze.

Dowody: `card-precision-v1`, `ha25-real-home`, `ha25-installed-final.json`,
`ha25-home-complete.json`, `ha25-python-tests.log`, `ha25-node-tests.log`
pod wspólnym katalogiem z początku dokumentu. Dalszy state mapping i nowe
warianty mierników pozostają oddzielnymi funkcjami.

## HA26 — pasywne czujniki drzwi, ruchu i obecności

Opcjonalny kolor aktywnego stanu obejmuje teraz informacyjne `binary_sensor`.
`on` używa wybranej roli, pozostałe stany — surface. Opcjonalna ikona `auto`
dobiera istniejący skompilowany znak okna dla door/window/opening/garage_door
albo obecności dla motion/occupancy/presence. Inne klasy mają zwykły sensor;
ręcznie wybranej ikony nie zmieniamy. Nie są to osobne ikony otwarcia/zamknięcia.
HA nadal dostarcza tłumaczenia. Jego polski zasób klasy presence zawiera
Home/Away, więc tylko ten ogólny przypadek otrzymuje Obecność/Brak obecności.
Własne tłumaczenie konkretnej encji zachowuje pierwszeństwo. Podgląd HA stosuje
tę samą politykę bez pollera, podmiany drzewa ani nowych danych wire.

**413 Python OK (trzy pominięte), 239 Node PASS**, Ruff i diff-check PASS.
Testy obejmują zapis/normalizację/projekcję, import, ikony, błędne metadane,
legacy fallback oraz brak dispatchu informacyjnej karty. Atomowe wdrożenie HA26
zachowało konfigurację; 25/25 źródeł odpowiada lokalnym plikom.

Kampania `binary-info-v1` na niezmienionym native31 potwierdziła dziewięć
oryginalnych obrazów: drzwi zamknięte/otwarte, okno otwarte, ruch wykryty/brak,
obecność/brak, unknown i unavailable. Zmiana obecności poza widoczną stroną
była poprawna po normalnym powrocie. Dwa natywne tapy pozostawiły źródło
niezmienione; observer HA nie zobaczył usługi skierowanej do czujnika.
To diagnostyczny tor wejścia LVGL, nie dowód fizycznego kontaktu GT911.
Rzeczywisty panel pokazał auto, Obecność, pastelowe tło/ciemny tekst,
wyłączoną akcję i czysty szkic. Obrazy wszystkich dziewięciu kart oraz Home
przejrzano; oryginalne JPEG pozostają niezmienione.

Guarded inverse odtworzył wszystkie 16 kart przy rewizji **34**; własną encję
usunięto po świeżym odpięciu. Trzy kamery i osiem preferencji zachowane.
Pamięć przed/po: **PSRAM 4575/4575 KiB, największy blok 3456/3456 KiB,
internal 24/24 KiB, snapshots 6552/6552 KiB**. Oddzielna normalna trasa
Home→Ustawienia→Home: **81 klatek, 55 FPS, średnio 16308 µs, max 23723 µs,
failed=0, jeden segment**, bez zarejestrowanej awarii. Oba oryginalne Home
przeszły kontrolę wymaganych regionów. Nie jest to długotrwały test audio lub
fizycznego aktuatora. Zmiany wyłącznie HA/JS nie wymagały nowego firmware;
tego checkpointu nie kompilowano ani nie wgrywano ponownie.

Dowody: `binary-info-v1`, `binary-ha-translations.json`, `ha26-real-home`,
`ha26-installed-final.json`, `ha26-home-complete.json`, `ha26-python-final.log`,
`ha26-node-final.log`. Nie commitowano i nie wysyłano zmian.

## HA27 — automatyzacje: włączanie, wyłączanie, jawne uruchamianie

Domyślna akcja automatyzacji rozwiązuje off→turn_on, on→turn_off z
`stop_actions=false`. Nie uruchamia sekwencji akcji i nie przerywa trwającego
wykonania. Jawne trigger/turn_off mają opcjonalne, ściśle boolowskie
skip_condition/stop_actions. Puste jawne parametry zachowują istniejące domyślne
zachowanie HA; formularz wyjaśnia je po polsku i angielsku. Kolor oznacza
włączenie przyszłych wyzwoleń, podpis — następną akcję, nie potwierdzenie sukcesu.
HA ponownie sprawdza bieżący stan, usługę i kontekst/rewizję. Użyto istniejącej
negocjowanej dostępności zwykłych akcji, bez nowego wire, zadania lub bufora.

**418 testów Python OK (trzy pominięte), 241 Node PASS**, Ruff/diff-check PASS.
Dotychczasowe testy nieuczestniczącej automation zastąpiono input_select;
oddzielne testy sprawdzają jej nową politykę, dokładne usługi i Context,
parametry, brak dispatchu dla unknown/unavailable/sensor i starej rewizji.
HA27 zainstalowano atomowo z kopią HA26 poza loaderem i jednym restartem;
25/25 źródeł odpowiada lokalnej wersji.

Pierwszy harness `automation-v1` zastał 404 między zapisem definicji a jej
asynchronicznym załadowaniem. Nie zapisał układu; obie własne fixture usunięto.
Wersja v2 czeka na rzeczywisty stan encji, zachowując pierwotny negatywny dowód.
Zwykły publiczny endpoint HA przeładowuje wyłącznie utworzone ID. Przed próbą
zarchiwizowano plik automatyzacji, a kontrola wszystkich 12 istniejących ID
zapobiegła dopisaniu ID przez automatyczny mechanizm Core. Definicje tych
12 automatyzacji przed i po są identyczne; ich sekwencji nie uruchamiano.

`automation-v2` utworzył jedną własną automatyzację bez triggerów oraz własny
Boolean. Jej warunek zawsze false, akcje: Boolean on → 15 sekund → Boolean off.
Native31 wykonał dokładnie osiem oczekiwanych usług automatyzacji:
turn_on, turn_off(false), turn_on, trigger(false), trigger(true),
turn_off(false), trigger(true), turn_off(true). Stan HA potwierdził:

- włączenie/wyłączenie nie uruchamia akcji;
- trigger(false) respektuje niespełniony warunek;
- trigger(true) rozpoczyna rzeczywistą sekwencję;
- domyślne wyłączenie w trakcie pozostawia current=1, a sekwencja kończy się;
- jawne stop_actions=true kończy current=0 przed ostatnią akcją.

Jedenaście oryginalnych obrazów potwierdza Włącz/Wyłącz/Uruchom i kontrast.
Rzeczywisty panel pokazał polskie opcje i parametr Nie; trzy Cofnij odtworzyły
czysty szkic. Panel nie wykonywał usług ani Save. Dokładny inverse odtworzył
16 kart przy rewizji **42**, obie fixture usunięto po odpięciu i kontroli
definicji. Trzy kamery i osiem preferencji zachowane. Pamięć przed/po:
**PSRAM 4581/4581 KiB, największy blok 3712/3712 KiB, internal 24/24 KiB,
snapshots 6546/6546 KiB**. Osobna normalna trasa Home→Ustawienia→Home: **80 klatek, 54 FPS, średnio 16741 µs, max 23568 µs, failed=0, jeden segment**, oba oryginalne Home kompletne, brak zarejestrowanej awarii. Ograniczenia fizycznego dotyku, audio, długiego
obciążenia i pełnego pending/error/result pozostają otwarte. Firmware native31
nie zmieniono, nie kompilowano ani nie wgrywano ponownie dla adaptera HA/JS.

Dowody w `automation-v1`, `automation-v2`, `ha27-real-home`,
`ha27-installed-final.json`, `ha27-home-complete.json`, `ha27-python-tests.log`,
`ha27-node-tests.log`. Brak commitów i publikacji.

## Choice — HA31 / native35, ograniczony odbiór

Jawny Select/input_select otwiera wspólny app6 z lokalnym wyborem oraz Apply.
Cała lista musi mieć1–8 unikalnych, drukowalnych opcji do32 bajtów UTF-8;
nieobsługiwana lista i brak glyph pozostają pasywne. Nie ma nowego workera ani
osobnego pełnego bufora. Właściciel sesji, generacje, TTL, autoryzacja i kontrola
rewizji są wspólne z Light/Number. Stan unknown nie jest wymyśloną opcją.

Native33/34/35 mają pełne kompilacje, audyty wejść, OTA i odczyty tożsamości.
Finalne native35: marker `2026-10-30 19:15:40 +0100`, ELF
`e8f8191173025b570c513378c224d2abad5161a62ebcd8241d16849a46c75944`.
Artefakty i źródła: `D:/aeh-build/feature-continuation-20261030/native-context-v35`,
`source-v35-build.json`. Native35 zmienia nagłówek CLIP na DOT; kod forku jest
identyczny z przyjętym native34. Audyt potwierdza525 źródeł,203 jednostki
kompilacji forku i wygenerowany tryb DOT.

`choice-v4` potwierdził pięć rzeczywistych komend input_select, lokalny podgląd
bez komendy, noop, nieznany stan, ABA podczas trzymania, zmianę listy podczas
trzymania, odnowienie sesji,1/8/9 opcji,32 szerokie znaki i brak glyph.
`choice-v5` sprawdził docelową klatkę po revoke: trzy oryginalne JPEG są
identyczne przed zwolnieniem kontaktu, po nim i później. Cztery ciepłe cykle
Choice: PSRAM7101KiB, largest2240KiB; cztery Light:7096–7102KiB,
largest2240KiB, zero usług Light. `choice-v6` potwierdził zawijany pełny tekst
opcji i czytelny nagłówek z wielokropkiem na finalnym35.

`choice-v8` użył rzeczywistego select języka Atmosfery: PL→EN→PL, dwie komendy,
potwierdzenie encji HA, preferencji native i oryginalne obrazy obu języków.
Zmiana języka celowo zamyka app6 zgodnie z istniejącą polityką; test otwierał
go ponownie. W tej próbie nie tworzono pomocnika. Oryginalne16 kart przywrócono
przy58, trzy kamery i osiem preferencji zachowano. Browser review/Undo PASS.
Wcześniejsze nieudane oczekiwania harnessu (nav_app jako ID aplikacji,
auto-zamknięcie po revoke, natychmiastowy screenshot, pozostanie app6 po zmianie
języka) zachowano w dowodach, nie uznano ich za odebrane scenariusze.

Normalne trasy Home→Ustawienia→Home na34:54/55FPS; finalne35:79 klatek,
54FPS, średnio16842µs, max23582µs, failed0. Oba Home oraz powroty po dwóch
cyklach mediów kompletne (`native35-complete-home-final.json`). Kamera wykazała
12,9 prezentowanych FPS,85 prezentacji/86 dekodowań, brak queue/stale drop;
rzeczywiste obrazy kamery i galerii oceniono wizualnie. Cztery próbki idle po
ciepłych mediach:3806KiB PSRAM bez spadku, largest1440KiB. Ten stan ma inną
historię cache niż baseline31 i nie dowodzi wyjaśnienia całej różnicy pamięci.
Otwarte: większe listy/paginacja, fizyczny dotyk, audio pod obciążeniem i długi
test żywotności. Brak commitów i publikacji.

## Bezstanowy przycisk automatyzacji — HA33 / native35

Jawna karta Action/event nie ma encji wykonawczej ani ukrytej usługi. HA tworzy
jej odkrywalną encję Event z jednym typem press, związaną z istniejącym urządzeniem.
Właścicielem jest bridge HA; prywatny callback publikuje timestamp dopiero po
autoryzacji i ponownym sprawdzeniu klienta, tożsamości, rewizji oraz rejestru.
Publiczny bus nie jest źródłem EventEntity. Ukrycie/odpięcie usuwa aktywne
powiązanie; historia naciśnięcia nie wraca jako nowy stan po ponownym dodaniu.
Maksymalnie14 encji, bez nowego bufora, widżetu, workera i natywnego timera.

455 testów Python (3skip) i252 JS PASS. `tile-events-v2` wykonał dwa tapy,
dwa zdarzenia i dwie rzeczywiste zmiany własnego Boolean przez własną automatyzację.
Drag, rename, trzymanie podczas zmiany rewizji, hide/rebind i browser nie dodały
zdarzeń. Trigger stanu wyklucza unknown/unavailable, więc zmiana atrybutu oraz
usunięcie/przywrócenie encji nie uruchamiają akcji. Rzeczywisty panel: jawna
konwersja, tworzenie w pustym miejscu, przenoszenie w szkicu i Undo do czystego
stanu, bez Save. Polski tytuł domyślny skrócono do „Automatyzacja”.

`tile-events-v3` potwierdził cztery kolejne tapy i zmiany helpera, w tym dwa po
zapisanym przeniesieniu15→13. Entity ID i unique ID pozostały te same, raporty
zawierały aktualny slot i rewizję. Same przenoszenie i powrót nie wywołały akcji.
Oryginały przycisku w obu miejscach oceniono wizualnie. Pierwsza próba v1 miała
błędne oczekiwanie harnessu: snapshot nie może zostać gotowy, gdy nadal trzymamy
kontakt. Oczekiwanie przeniesiono po release; źródeł firmware nie zmieniano.

Po każdej próbie przywrócono16 oryginalnych kart, usunięto własną automatyzację,
Boolean oraz dokładny nowo utworzony rekord Event dopiero po odpięciu. Pozostałe
12 definicji automatyzacji są semantycznie identyczne. Osiem preferencji i trzy
kamery zachowane. Ostateczna rewizja73, HA33. Normalna trasa Ustawień:79 klatek,
54FPS, średnio16342µs, max24310µs, failed0, jeden segment; brak awarii w zapisach.
Firmware35 pozostaje tą samą zbudowaną, wgraną i odczytaną wersją; dla kodu HA/JS
nie wykonywano kolejnej kompilacji ani OTA. Fizyczny dotyk, audio pod obciążeniem
i lifetime nadal otwarte. Dowód zbiorczy:
`D:/aeh-build/feature-continuation-20261030/tile-events-acceptance.json`.

## Number urządzenia — HA34 / native35

Istniejący regulator obejmuje teraz encje `number` i pomocniki `input_number`.
Model i frontend wymagają jawnej karty control/number. Każda domena musi mieć
własną usługę set_value; brak number.set_value nie może zostać zastąpiony przez
input_number.set_value. Metadane i polecenia pozostają dokładną, ograniczoną
dziedziną dziesiętną oraz jednym właścicielem sesji. Bez zmiany firmware.

463 testy Python (3skip) i255 JS PASS, w tym właściwa domena usługi i Context,
brak/mutacja capability, metadata/value ABA, duplicate, granice i nieznany stan.
`device-number-v3` użył istniejącej, odkrytej po MAC/registry liczby Atmosfery:
odstęp pokazu zdjęć, min5/max600/step5. Dwa tapy wysłały dokładnie dwie komendy
step i dwie usługi number.set_value:30→35→30. Stan HA i bezpośredni native Number
potwierdziły wartości. Zewnętrzne40→30 podczas trzymania nie dodało komendy po
release. Oryginały30/35/30 i potwierdzeń oceniono; liczenie pikseli potwierdza
pełne tytuły, przyciski i status mimo różnicowej prezentacji obrazu w narzędziu.

Cztery ciepłe cykle otwarcia: PSRAM6359/6362/6362/6361KiB, largest3776KiB
stały. Browser: prawidłowa encja, potwierdzenie regulatora, dwa Undo do czystego
stanu, bez Save i dodatkowych komend. Oryginalny parametr30,16 kart,3 kamery
i8 preferencji odtworzono przy79; nie tworzono pomocników. Normalne Ustawienia:
78 klatek,53FPS, średnio16814µs, max23802µs, failed0, jeden segment. Oba Home
kompletne. Różnica53–55FPS mieści się w zaobserwowanych przebiegach; nie jest
deklaracją niezmienionego całkowitego CPU w dowolnym obciążeniu.

Pierwsze dwa harnessy zostały zachowane jako nieudane: intensywnie wykonywały
pełne histogramy diagnostyczne, zanim realny lifecycle otwierania/zamykania się
zakończył. Wersja3 najpierw czeka na stan aplikacji i ogranicza odpytywanie.
Bez zmiany firmware uzyskała pełny wynik. Nie mylić tego z usunięciem natywnej
regresji kodem. Physical/audio/lifetime pozostają otwarte. Zbiorczy dowód:
`D:/aeh-build/feature-continuation-20261030/device-number-acceptance.json`.

## Opisy stanów — HA35 / native35

Opcjonalne state_labels obejmuje do8 dokładnych par po32 bajty tekstu, wyłącznie
na pasywnych kartach Information. Backend sprawdza granice/drukowalność, nie
pozwala mapować unknown/unavailable. Źródło, jednostki i polityka akcji pozostają
bez zmian. Nie ma nowej subskrypcji, natywnego pola, bufora lub workera.

469Python (3skip) i262JS PASS. `state-labels-v2`: Eco→Oszczędny,
Comfort→Komfortowy, Boost bez mapowania oraz rzeczywiste helperowe wartości
unknown/unavailable z poprawnymi standardowymi komunikatami. Zmiana poza ekranem
i powrót pokazały aktualny opis. Dwa pasywne tapy nie wywołały usługi.
Rzeczywisty M3 dialog zachował wpisywany tekst i fokus, zablokował powtórzone
stany, zmienił podgląd bieżącej wartości; każde potwierdzenie było jednym Undo,
bez Save ani usług. Oryginały mapy, outage, powrotu i dialogu oceniono wizualnie.

Odtworzono16 kart przy83, usunięto własny input_select po odpięciu;3 kamery i8
preferencji zachowane. Pamięć przed/po identyczna: PSRAM3803KiB, largest2880KiB,
snapshot7368KiB. Normalne Ustawienia:80 klatek,54FPS, średnio16215µs,
max30993µs, failed0; oba Home kompletne. Pierwszy harness v1 wysłał dwa tapy
bez odstępu i dostał prawidłowe quiet_period przy drugim. Cleanup przeszedł;
v2 rozdzielił tapy400ms i przeszedł cały scenariusz. Firmware35 bez zmian,
473 Python/265 JS i nowe teksty HA36 są kolejnym, osobno odbieranym fragmentem.
Physical/audio/lifetime nadal otwarte. Dowód zbiorczy:
`D:/aeh-build/feature-continuation-20261030/state-labels-acceptance.json`.

## Tekstowe helpery — HA36 / native35, funkcjonalnie PASS; uwaga DSI otwarta

Plain input_text trafia do biblioteki i pasywnej karty Information. Tekst nie
jest tłumaczony ani wykonywany, whitespace zwija się do spacji, limit40 punktów
jest zgodny z preview. Password i nieznany mode są pomijane w katalogu i maskowane
na istniejącej karcie przed mapowaniem stanu; cached library także maskuje wartość.
473Python (3skip), focused formatter4 i265JS PASS. Własne źródło6 razy zmieniono
kontrolowanymi usługami; nowych usług zapisu tekstu w kartach nie dodano.

`text-info-v1`: zwykła notatka, mapowany tekst, unknown/unavailable,
text→password→text, pusty katalog dla password mimo aktywnej mapy, dwa pasywne
tapy bez usług i zmiana poza ekranem PASS. Oryginały zwykłej notatki i maskowania
oceniono. Rzeczywista biblioteka znalazła helper; przypisanie utworzyło Information,
jedno Undo przywróciło czysty układ bez Save. Usunięto niepasujące wskazówki
sterowania na kartach informacyjnych. Helper usunięto po odpięciu, przywrócono16
kart przy85,3 kamery i8 preferencji.30/30 plików HA zgodne. PSRAM przed/po
3807/4527KiB, largest2304/2880KiB, snapshot7364/7364KiB; wzrost free nie jest
przypisany tej funkcji bez kontrolowanego porównania.

Normalna trasa:80 klatek,54FPS, średnio16099µs, max23906µs, failed0. **Ten
przebieg ma jednak jeden DSI bridge underrun**, total1/tick3360015, tuż po
capture-resumed. DMA ring valid, recovered0/rejected0, host DPI underrun NO.
Oba Home kompletne; brak resetu. Źródła firmware są identyczne z native35.
Nie uznawać tego za naprawione ani wyjaśnione przez sam brak powtórki.

`ha36-dsi-followup-home`:81 klatek,54FPS, średnio16136µs, max23510µs, failed0,
brak nowego IRQ. `dsi-capture-v1`, bez resetu i zmiany preferencji:45s idle,
4 statyczne screenshoty,8 normalnych Home1→2→1 ze screenshotem,45s idle;
12 oryginałów, zero nowych DSI/fatal/disconnect. Funkcjonalny odbiór tekstu
jest oddzielony od niewyjaśnionej pojedynczej obserwacji DSI. Kolejny firmware
musi mieć własną bramkę diagnostyki; nie usuwać wcześniejszego nieudanego logu.

## Cover candidate native36 / HA38 — acceptance in progress

- Configuration/full ESP-IDF build PASS; frozen source manifest
  `D:/aeh-build/feature-continuation-20261030/source-v36-build.json`,
  SHA256 `3009d81068a802469a917b4152a2a0126c968ed33f5aa66eeb134a372ed68679`.
- Input audit:527 copied sources,205 ESPHome translation units,2308 compilation
  commands; three Cover widget bindings and both opt-in defines verified.
-39 native tests/383subtests PASS;492 HA Python(3skip),270 JS PASS. Cover
  includes both optional-feature combinations, real LVGL8scenarios and112tile
  routes. These are distinct from device/UI acceptance.
- One OTA PASS. Preserved native-context-v36 manifest
  `d441c5d1c77e0ef37cb36c3edaefa66a9025cb673bcde99265a734201cdf57c0`;
  ELF `fabcc582236cb4ce44b75bfc2a382b7dcdc80cfb0a75d24144db70f1272598b0`,
  marker `2026-10-30 20:40:44 +0100`. Exact live identity and8prefs PASS.
- Initial test at boot23s received touch `not_ready`, no fault. After normal
  boot completion, native36-ready-home79frames54FPS avg16716us max23657us,
  failed0/noDSI; two original Home images pass the complete-screen check.
  Pre-OTA native35 route54FPS avg16494us failed0. Cache/task history differs,
  so initial free-memory and total-CPU numbers do not establish parity.
- cover-v1 found real HA IntFlag metadata rejected as non-int, making the card
  passive before any command. HA38 fixes the adapter and adds a regression.
  Cleanup restored16cards/3cameras/8prefs, revision87, removed its MQTT entity
  and automation, and preserved all12 household automation definitions.
- Next: repeat isolated MQTT round trip, browser review/Undo, screenshots,
  warm-memory/media/performance gates. Urgent Stop during pending remains a
  required next W05 slice; do not mark CTL-005 complete or claim physical motor
  stopping from software/MQTT feedback. All changes remain local/uncommitted.

## Negotiated Cover Stop — HA39 installed, native37 build pending

HA39 adds an optional typed feature query/bind tied to the exact new channel;
v1 envelopes remain unchanged. Host evidence:515 HA Python (3 skipped),271 JS;
native priority-owner2tests/2subtests, real-LVGL1test/10subtests and codegen
2tests/5subtests PASS. These do not constitute hardware acceptance.

The first full build and broader native regression were interrupted by Windows
memory exhaustion. The partial broader test log is not PASS. Frozen source
`source-v37-build.json` has SHA256
`7236f02af25dcb7d6ed47fc18fd1b8fc2c4fb9a5fdc52fcf8614ceb388e1cfc2`.
The new native build has an explicit Ninja4 limit; C++ host compilation is kept
separate. No native37 OTA has occurred at this checkpoint.

HA39 atomic installation and one restart PASS,33/33 installed source hashes
match `ha39-source-pin.json`. Entry data/options hashes,16cards/3cameras and
revision91 are unchanged. An early startup probe saw no panel; the subsequent
fresh probe passes. On native36, generic controls remain ready and
cover_stop_version=0, so Cover correctly stays passive before the new firmware.

Pre-OTA native36 warm-media3 shows an actual Immich photo after40s and actual
camera presentation. The12s observation was still loading, not a gallery failure.
Warm Settings:80frames,54FPS,16195us average,23716us maximum,failed0.
PSRAM before/after3522/3543KiB, largest1568/1568KiB, snapshot7573/7545KiB;
this is a same-run baseline, not an across-version memory parity claim.
Native36/HA39 normal Home1→2→Settings→2→1 passes without new DSI/fatal faults,
and both Home originals pass completeness checks; the final original is also
visually reviewed. Eight preferences remain unchanged.

Basic Cover-v2/v3 software round trips, negative cases and four warm opens ran
on native36. Browser acceptance remains pending due unavailable desktop input.
The v3 browser wait outlived its HA WebSocket; fresh-connection recovery then
restored16cards/revision91, removed exactly the owned MQTT/automation fixture
and preserved all12 household automation definitions. No QA fixture remains.
Native37 campaign-v4 removes that browser wait and adds pending Close→held Stop
through position churn. Physical motor stopping, position/tilt setters, browser
acceptance, long-run audio and the earlier unexplained native35 DSI event remain
separate gates; do not mark W05 or CTL005 complete.
