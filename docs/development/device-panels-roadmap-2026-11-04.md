# Dedykowane widoki Atmosfery — stan i dalszy plan

**Stan na 7 listopada 2026: native117 / HA131.** Odebrany zakres
obejmuje także Statistics1 oraz jawny formularz skryptu z jednym wymaganym
polem Tak/Nie. Slot13 wrócił do oryginalnego widoku Info; kolejność stron12345
pozostała bez zmian. Historyczna awaria107, błędy116 i nieudane obserwacje rozruchu
pozostają zapisane. Odbiór funkcji nie oznacza strict-clean boot, odsłuchu
akustycznego ani potwierdzenia ciągłych60 FPS.

Bieżące dowody i punkt wznowienia są w [checkpointcie117](resume-2026-11-07-actionparams117.md).
Poniższa mapa opisuje odebrany zakres produktu i pozostałą pracę.

## Co jest dostępne

Kafelki otwierają dedykowany widok; polecenie urządzenia jest osobnym działaniem
w tym widoku. Kamera w slocie30 otwiera od razu istniejący CameraPreview/App5,
bez pośredniego przycisku testowego i bez automatyzacji.
Istniejące aplikacje Player, Kamera, Galeria i Asystent zachowują swoje
mechanizmy. Panel mediów HA służy do opcjonalnego sterowania zewnętrzną encją,
a rozwój lokalnego odtwarzania pozostaje w dedykowanym Playerze.

Poniższy „odebrany zakres” oznacza odbiór danej rodziny na Atmosferze, z danymi
i usługami HA oraz screenshotami. Test z mockiem nie potwierdza ruchu silnika,
pracy kotła ani odtwarzania na fizycznym urządzeniu danego producenta.

| Widok i domeny | Odebrany zakres | Nadal poza tym zakresem |
| --- | --- | --- |
| Kamera/wideodzwonek — `camera` | Jawny launcher w slocie30 otwiera istniejący CameraPreview; standardowe zamknięcie, zachowany wybór zwykłej Kamery i zwolnienie źródłowych buforów (HA124). Krótsze podpisy launchera w117/HA131. | Fizyczny dzwonek/frontowa kamera; test źródła Demo nie potwierdza instalacji przy drzwiach. |
| Wentylator — `fan` | Stan, zasilanie, rzeczywiste biegi, presety, oscylacja i kierunek, według możliwości encji. Także wariant z samymi presetami oraz powrót z aktywnego presetu do jawnej prędkości przy nieznanym procencie (100/HA122). | Większe katalogi i dodatkowe funkcje zależne od producenta. |
| Nawilżacz/osuszacz — `humidifier` | Wilgotność zmierzona i zadana, regulacja, tryb, zasilanie. | Niestandardowe tryby i dodatkowe funkcje providera. |
| Roleta/brama — `cover` | Otwórz/Zatrzymaj/Zamknij, pozycja i lamele; osobne zatrzymanie obu osi, gdy wspierane. | Odbiór z konkretnym fizycznym napędem i dodatkowe funkcje producenta. |
| Robot — `vacuum` | Stan, bateria gdy dostępna, główne akcje, moc i obsługiwane sprzątanie wybranego obszaru. | Mapa, wiele obszarów w jednym zleceniu, procedury sprzątania. |
| Kosiarka — `lawn_mower` | Stan i dostępne Koszenie/Pauza/Baza, właściwa ikona. | Mapa, strefy i rozszerzenia konkretnej integracji. |
| Minutnik — `timer` | Odliczanie, edycja czasu, Start/Pauza/Wznów/Anuluj/Restart. | Rozbudowane harmonogramy wielu minutników. |
| Pilot — `remote` | Zasilanie i wybór rzeczywistych aktywności. | Klawiatura IR/RF, uczenie poleceń i większe katalogi. |
| Zasilanie — `switch`, `input_boolean` | Wyraźny stan i jawna zmiana zasilania, bez przełączania przy otwarciu. | Funkcje specjalne urządzenia, których zwykły przełącznik nie opisuje. |
| Światło — `light` | Jasność/zasilanie, temperatura bieli i efekty; Color1 H/S z lokalnym szkicem, Anuluj/Zastosuj i jawnym przejściem CT→kolor (103/HA125). Adapter kwalifikuje HS/RGB/XY; sprzętowy batch użył własnego demo HS+CT. | RGBW/RGBWW, gamut/kalibracja i fizyczne potwierdzenie barwy. Wyjaśnienie sporadycznych szczytów kosztu Color; brak twierdzenia o60 FPS. |
| Termostat — `climate` | Duża tarcza nastawy, odczyt/aktywność i parametry HVAC. Range1: wybór Dolny/Górny i jedna dokładna para przy puszczeniu; odebrany Range104 i poprawna para w MAIN105/HA126. | Histereza, konwersja jednostek i parametry producenta bez odpowiedniego interfejsu HA. |
| Wartość — `number`, `input_number` | Wartość, jednostka i dokładny zakres; regulacja zgodna z krokiem HA. | Niestandardowe wizualizacje i edycja parametrów niewystawionych w HA. |
| Wybór — `select`, `input_select` | Aktualna opcja, wybór kandydata i osobne zatwierdzenie. | Listy większe niż obecny ograniczony katalog oraz wyszukiwanie. |
| Data i czas — `input_datetime` | Osobne tryby daty, czasu i daty z czasem; lokalny szkic, widoczne sekundy, Anuluj i jeden jawny Zapisz. Walidacja dat, lat przestępnych i zmian źródła podczas dotyku. | Wartości to lokalne daty/czasy helpera; bez wyboru DST fold i konwersji do timestamp. |
| Tekst — `input_text` | Lokalny szkic, klawiatura ASCII/PL, kursor, Anuluj i jeden jawny Zapisz; zakres HA do255 znaków, pełny odczyt przez sześciowierszowe okno, blokada nieaktualnego gestu. Password ukrywa treść i wyłącza edycję. | Pattern, pełny Unicode, wielowierszowe wartości i edycja haseł. Stały launcher Text znajduje się teraz w slocie9; slot29 pozostaje Datetime. |
| Informacja — `sensor`, `binary_sensor` | Pomiar lub stan, jednostka, klasa urządzenia i świeżość; ikona zalania. Statistics1 dla kwalifikowanych czujników pomiarowych: wykres średniej i min–max z24 zakończonych godzin (115/HA129). | Dłuższe okresy, historia stanów i rozbudowane mierniki. |
| Osoba — `person` | Dom/Poza domem/pełna nazwa strefy, czas zmiany obecności i strefa czasowa. Odbiór własnego trackera dom → poza domem → dom, zgodne dane i screenshoty. | Widok tylko do odczytu; bez mapy, zdjęć, współrzędnych i sterowania obecnością. |
| Słońce — `sun` | Stan nad/pod horyzontem, najbliższy wschód i zachód, wysokość i azymut; przyjazne daty, offset oraz strefa. Porównano z aktualnym `sun.sun`. | Graficzna ścieżka Słońca i rozbudowane wizualizacje astronomiczne. |
| Kalendarz — `calendar` | Szczegóły wydarzenia, daty, strefa i wydarzenie całodniowe; mała Agenda do16 wpisów/7 dni w HA. Ograniczona trasa114 ponownie przeszła; historyczny Guru107 pozostaje niewyjaśniony. | Wybór dni, tworzenie i edycja wydarzeń. |
| Alarm — `alarm_control_panel` | Dedykowany widok stanu. | Uzbrajanie, rozbrajanie, PIN i potwierdzanie operacji. |
| Zamek — `lock` | Stan i jawne Zamknij, z potwierdzaniem wyniku. | Odblokowanie, otwarcie i PIN. |
| Media HA — `media_player` | Dedykowany widok muzyki/TV, obsługiwany transport i zasilanie, głośność, wyciszenie, losowość, źródło, tryb dźwięku i powtarzanie. | Seek, przeglądanie biblioteki/ulubionych, większe katalogi; lokalny Player jest osobną aplikacją. |
| Działania — `button`, `input_button`, `scene`, `script`, `automation`, zdarzenie kafelka | Rozpoznawalny widok rodzaju działania, stan i ostatnie użycie. Skrypt: Uruchom/Zatrzymaj; automatyzacja: Uruchom/Włącz/Wyłącz z jawną polityką zatrzymania. Bezstanowe zdarzenie w slocie23 ma osobny widok i jawne Wyślij, odebrane w102/HA123. W117/HA131 przyjazny czas ostatniego użycia i jawny formularz jednego wymaganego Boolean, z UNSET lub rzeczywistym domyślnym Boolean. | Pozostałe typy parametrów, pola opcjonalne, wiele pól oraz działania przekazujące ekran innej aplikacji. |

W automatyzacjach komunikat „Polecenie przekazane do HA” potwierdza przyjęcie
zlecenia, nie ukończenie całej automatyzacji. Kafelki przycisku, sceny i
`input_button` otwierające panel mają podpis „Otwórz”; data ostatniego użycia
pozostaje w szczegółach. To jest już zakres 95/HA 116, nie przyszły etap.

## Odbiór formularza Params1 i drobnych poprawek 117 / HA131

Nowy wybór w edytorze jest jawny i wymaga uzgodnionego Params1. Obsługuje
**dokładnie jedno wymagane pole Boolean**. Bez zadeklarowanej wartości domyślnej
początkowym stanem jest UNSET i Uruchom jest zablokowane; false nie jest
niejawnym domyślnym wyborem. Prawdziwy domyślny Boolean z metadanych HA jest
respektowany. Otwieranie, lokalny wybór, anulowanie i ponowne otwarcie nie
wywołują usługi. Stare karty Action2 nie są automatycznie migrowane.

Na urządzeniu potwierdzono cztery komendy: jawne False, True, domyślne False
oraz Zatrzymaj. Każda ma własny zapis tożsamości i wynik; Run potwierdza
przekazanie usługi, a efekt własnego helpera i zakończenie skryptu są osobnymi
obserwacjami. Stop zachował format bez parametrów. Obejrzano osiem
oryginalnych screenshotów, w tym końcowy Home; slot13 przywrócono przez CAS
przy rewizji408. Odbiór dotyczy własnych rzeczywistych skryptów Core i wejścia
diagnostycznego Atmosfery, nie dowolnych skryptów domowych ani fizycznego palca.

Domknięto także przyjazną prezentację ostatniego użycia w Action i krótsze
podpisy launchera Kamery. Pełne sekundy, ułamek i offset czasu pozostają na
przewodzie, a silnik streamingu Kamery jest bez zmian. Porównywalna partia117
zachowała medianę Home 37,5 FPS i Settings 54 FPS, bez zdarzeń DSI ani hard fault.
To pomiary kompozytora w określonym scenariuszu, nie dowód stałych60 FPS.
Pierwszy boot117 zachowuje FAIL/UNCLASSIFIED_SENDSPIN_BOOT_WINDOW; późniejsza
obserwacja bieżącego stanu nie zmienia go w strict-clean boot.

Dowody: `C:/aeh-build/blue-flash-20261107/actionparams117-device-first/report.json`
oraz `interaction117-first/report.json`. Szczegóły i ograniczenia:
[odbiór Params1](acceptance-action-parameters-2026-11-07.md).

## Awaria107 podczas odbioru Agendy — praca diagnostyczna

Historyczny boot106 zakończył się Guru w niszczeniu sesji miksera i
automatycznym powrotem do105. Poprawka107 używa unikalnej własności
ring/reader i krótkich lease; main loop zwalnia reader przed ringiem po
ostatnim lease, bez nowego zadania/PCM. Host/P4, pełny build i linked107
przeszły. Pierwszy boot oraz pięć restartów107 potwierdziły cyfrowy dźwięk
i wake, a pięć oryginalnych obrazów Home było poprawne. Znany odzyskany
retry4096 B pozostaje; nie ma strict-clean ani odsłuchu. Pierwotny ENOSPC
build107 pozostaje FAIL, oddzielna kontynuacja z tymi samymi źródłami PASS.
Patrz [własność audio](../architecture/audio-voice.md#mixer-session-handoff).

HA127 jest zainstalowane; jedyny CAS398→399 migrował własny slot12. Agenda
przechowuje do16 wydarzeń z7 dni tylko w HA, a urządzenie pokazuje jeden
wpis w Calendar/App6 i dodaje cztery obiekty Poprzednie/Następne. Sześć PAGE
było tylko odczytami, bez COMMAND/usług providera. Siedem oryginalnych JPEG
oraz edytor127 przeszły ocenę częściową; wspólne piksele nagłówka/dat są
obecne w oryginałach, mimo pomijania ich przez podgląd narzędzia.

`NEW/agenda107-device-first/report.json` pozostaje **FAIL**: powrót App6→Home
zakończył się Core1 Load access fault przed pomiarem Settings. Dekodowanie
wskazuje TLSF malloc w ścieżce lwIP/logowania diagnostyki DSI, bez dowodu
przyczyny. Nie przypisywać winy audio na podstawie oczekującego odczytu
diagnostycznego ani zakładać uszkodzenia sterty z samego MTVAL. Późniejszy
35-sekundowy odczyt bez mutacji potwierdził107/127/399/Home1, cyfrowy dźwięk
i wake bez nowych faultów; nie zamienia wcześniejszego FAIL w PASS.

Dokładne piny i punkt wznowienia są w [checkpointcie](resume-2026-11-05-datetime.md).
Ówczesny plan diagnostyki108 został zastąpiony badaniem regresji wyświetlacza
i poprawką114. Statistics1 przeniesiono na nową bazę i odebrano w115/HA129.
Nie powtarzać zakończonego CAS ani historycznych prób bez nowej przyczyny.
[Kontrakt Agendy](../architecture/ha-agenda-panels.md) pozostaje bez zmiany.

## Odbiór Range104 i poprawki MAIN105 / HA126

Istniejąca tarcza600px i Mode/Parameters obsługują Dolny/Górny; dodano tylko
launcher Zakres z etykietą. Przeciągnięcie ogranicza wybrany próg do drugiego,
równość jest legalna, release wysyła jedną absolutną parę. Nie ma ukrytej
zmiany HVAC/zasilania ani osobnego Zastosuj. Adapter wymaga dokładnego kroku,
jednostki i pary; edycja dotyczy heat_cool. Kontrakt:
[Climate Range1](../architecture/ha-climate-range.md).

Raport `NEW/range105-acceptance-final.json`, SHA
`eb9e23d990221b6710354976054fa9ceca9fb16cbdebedb4c584f85ae7bdb1c4`,
wiąże105/HA126/398/Home1, build/linked/OTA, kwalifikowany boot i pięć
oryginalnych screenshotów. MAIN pokazuje parę21–24 °C, identyczną po Back;
zachowano bieżącą temperaturę/aktywność, stary scalar21 °C i pełny Home.
Zbyt długi zapis otrzymuje w hero „Zakres” i pełną dokładną parę niżej.
Nie zmieniono fontów, wejścia, ownera, wire ani konfiguracji HA. Batch105
wysłał zero native COMMAND/usług i przywrócił karty dwoma CAS slotu16.

Poprzedni raport104 zachowuje jawny follow-up MAIN. W104 potwierdzono trzy
komendy pary, jedno publiczne przywrócenie podczas trzymania, release bez
dodatkowej komendy i dziesięć oryginalnych obrazów. Nie powtarzano usług
tego scenariusza dla prezentacyjnej poprawki105. Odbiór dotyczy własnego
demo i diagnostycznego dotyku urządzenia, nie fizycznego kotła/palca.

Settings105:55 FPS, avg16074 µs/max18024 µs, failed0, bez DSI/UART faults;
104 miał55 FPS/16254/19763. Końcowo internal23231 B/PSRAM4940528 B.
Zmiana105 nie zwiększa statycznego RAM ani liczby obiektów/buforów/zadań;
flash+512 B, ramka zmienionej funkcji+16 B. Nie są to dowody ciągłych60 FPS,
braku wycieku lub przypisania całej różnicy heap konkretnej zmianie.
Boot105 potwierdził230399 cyfrowych ramek i35 s wake, zachowując znany
odzyskany retry4096 B stosu miksera; brak strict-clean i odsłuchu.

Histereza, konwersja jednostek i fizyczny regulator pozostają osobnymi
zakresami. W historycznym checkpointcie105 Agenda była przygotowana do
wdrożenia; jej bieżący częściowy wynik107/HA127 i awarię opisano powyżej.
Nadal nie obejmuje tworzenia/edycji wydarzeń ani automatycznej migracji kalendarza.

## Odbiór Color103 / HA125

Raport `C:/aeh-build/device-panels-20261104/color103-acceptance-final.json`
(SHA `7f10d9a5af0b42ee8fc455247c9eec17bcd083088dc8e1d05cc3979e63812945`)
wiąże build/OTA/boot, HA125, układ394/Home1 i osiem oryginalnych screenshotów.
Dwie jawne komendy dały dwie usługi zmiany H/S; jeden osobny kontrolowany
restore przywrócił CT2631 K i brightness180. Otwieranie/Anuluj/unchanged oraz
release po zmianie źródła nie dały dodatkowych poleceń. To odbiór własnego
demo i diagnostycznego dotyku Atmosfery, nie fizycznej lampy lub ogrzewania.

Ustawienia:55 FPS, avg16100 µs/max18079 µs, failed0, brak błędów UART/DSI.
Sampler Color: loop avg13.544 ms/max61.873 ms i10 pętli>30 ms to rzeczywiste
koszty wykonania. Całe okno obejmuje API i przerwy dotyku, więc nie potwierdza
ciągłego60 FPS; przerwy nie wyjaśniają kosztu pętli. Szczyty pozostają
konkretną pracą wydajnościową. Końcowo internal23035 B/PSRAM4763156 B,
statyczny RAM+320 B. Dodano15 widżetów bez nowego taska/fullscreenbufora.
Historia cache nie pozwala przypisać całej różnicy PSRAM tej zmianie ani
wykazać braku wycieku. Kwalifikowany boot zachował znany odzyskany retry4096 B
stosu miksera; audio cyfrowe/wake potwierdzone, brak odsłuchu i strict-clean.

## Odbiór launchera Kamery HA124

Raport `C:/aeh-build/device-panels-20261104/camera124-acceptance-final.json`
(SHA `f89ed5a63fc00acd24fd90d1aa9ad2a492bc714b4a1241b2e3f6ef4ced9c9cdb`)
wiąże394/Home1, HA124, ten sam firmware102 i pięć oryginalnych screenshotów.
Slot30 zmienił się jednym CAS393→394. Otwarcie Demo camera odbywa się przez
istniejący App5, bez testowego przycisku/zdarzenia. Standardowe zamknięcie
wraca na Home5; zwykła Kamera zachowuje Public Aquarium Stream. W obu sesjach
source_kib spadło do0, bez zwalniania wspólnej kolejki134 KiB.

Okna około3 s:13.237 FPS prezentowanych Demo i10.932 Aquarium; różne źródła,
bez twierdzenia o regresji tego samego strumienia lub60 FPS. Końcowo
internal19307 B/PSRAM4490736 B; cyfrowe audio i wake gotowe. Brak fizycznego
testu dzwonka/palca i odsłuchu. Statyczny firmware bez zmian; ograniczenia
pamięci zależnej od cache oraz znany kwalifikowany boot102 pozostają.

Pierwotny raport ma zachowany FAIL wyłącznie po zakończeniu prób, podczas
zamykania obserwatora WebSocket1000. Osobny odczyt potwierdził394/Home1,
normalne źródło/idle/audio, bez powtórzenia CAS lub strumieni. To wyjaśnienie
i kontynuacja dowodów, nie nadpisanie pierwotnego wyniku.

## Odbiór zdarzenia kafelka102 / HA123

Raport `C:/aeh-build/device-panels-20261104/tile-event102-acceptance-final.json`
(SHA `4175a0abbe0f8abd0177618fca6bd7137cf271f76dbd926f9dda844d06ff3cfa`)
wiąże finalny393/Home1, source/ELF, wdrożenie HA123 i oryginalne screenshoty.
Otwarcie i zamknięcie nie wykonuje polecenia. Jeden jawny przycisk odpowiada
jednej komendzie native, jednej aktualizacji EventEntity i publicznemu
`atmosfera_echo_hub_event` z tym samym kontekstem. Sprawdzono także pierwszy
stan bez historii i ponowne otwarcie ostatniego użycia. To przyjęcie zdarzenia,
nie dowód ukończenia automatyzacji. Wykorzystano istniejący App6 Action2;
nie dodano widżetów, zadań ani buforów obrazu.

Pierwotny audyt przed OTA miał FAIL przez liczenie49 przypisań zamiast46
elementów zwykłej tabeli. Poprawiono zakres kontroli, zachowując osobne3
nadpisania; osobna kontynuacja wgrała ten sam firmware. Pierwszy test miał
FAIL przez błędną nazwę nasłuchiwanego zdarzenia i nieaktualne oczekiwanie
stanu event. Potwierdzony CAS392→393 nie był powtarzany; osobna kontynuacja
z nowym naciśnięciem potwierdziła właściwą magistralę. Oba FAIL są zachowane.

Jedna trasa Ustawień:54 FPS, avg16307 µs/max20183 µs, failed0 i brak błędów
UART/DSI. Po trasie internal23547 B/PSRAM4942768 B, końcowo internal23587 B.
Statyczny RAM310156 B bez zmiany; różna historia cache nie pozwala wnioskować
o odzysku pamięci, braku wycieków czy uniwersalnym60 FPS. Start kwalifikowany
z odzyskaną próbą4096 B stosu miksera:230399 ramek audio,36.012 s wake;
bez odsłuchu i strict-clean boot. Screenshoty potwierdzają wygląd, a wejście
diagnostyczne obsługę dotyku urządzenia; brak nowej próby fizycznym palcem.

## Odbiór pamięci i stylów Text101

Raport `C:/aeh-build/device-panels-20261104/text101-acceptance-final.json`
(SHA `8a40ae039f1bb4da05b57c170886edbbdd7cf8d8c8ccd0a98e5745274804f98b`)
potwierdza podgląd, klawiaturę, lokalny szkic, Anuluj, zamknięcie i Home.
Sześć oryginalnych screenshotów; podgląd/klawiatura identyczne z100, Anuluj
identyczne z podglądem. Zero poleceń providera i zmian układu/źródła.

Jedna trasa Ustawień:55 FPS źródła, avg16148 µs/max18833 µs, failed0/IRQ0;
po trasie internal13151 B (−144 B wobec100), PSRAM4880132 B. Współdzielone
style usuwają szacowane2624 B wyrównanego payloadu heap; statyczny RAM+64 B.
Nie ma nowych obiektów/buforów/zadań. Nie wykazano odzyskania wcześniejszej
różnicy7392 B internal ani braku wycieków; historia cache ogranicza porównanie.
Start kwalifikowany:230399 ramek cyfrowego audio i35.988 s wake, z zachowaną
znaną odzyskaną próbą4096 B stosu miksera. Brak odsłuchu i strict-clean boot.
Pierwotny FAIL kompilacji po zapełnieniu C: zachowano; zakończono linkowanie
tego samego źródła. Pełne funkcjonalne Save/255/ABA/privacy pozostają odbiorem
99a/HA121;101 nie powtarzał usług ani zmian źródła.

## Odbiór wentylatora100 / HA122 i launchera Text392

Zbiorczy raport `C:/aeh-build/device-panels-20261104/fan100-acceptance-final.json`
(SHA `1a30b91d3a75dabed734c48feb00e20a52d24513090af132a1430d1aebd185ca`)
wiąże aktualny392/Home1, firmware, companion i poniższe ograniczone próby.

Własny pełny wentylator obsługuje presety również przy SET_SPEED bez osobnego
bitu PRESET_MODE, zgodnie z Core. Po presecie „auto” pokazuje nieznany procent,
a świadomy wybór33% przywraca tryb ręczny. Wariant preset-only nie pokazuje
nieobsługiwanych regulatorów. Trzy komendy mają trzy odpowiadające usługi HA,
a otwarcie i niezmieniony wybór nie wysyłają polecenia. Obejrzano siedem JPEG.
Mock pełny zainicjalizowano jawnie do off/0/None i do tego punktu wrócił test;
pierwotnego null procentu nie przywrócono. Nie testowano fizycznego silnika.

Jedna trasa Ustawień dała55 FPS źródła, avg16293 µs/max21907 µs, failed0/IRQ0.
Po trasie internal13295 B i PSRAM4849716 B; to obserwacja zależna od cache,
nie dowód braku regresji ani uniwersalnego60FPS. Cyfrowe audio/wake i UART
przeszły. Boot kwalifikowany zachowuje znany odzyskany błąd alokacji4096 B
stosu miksera przed dźwiękiem; brak odsłuchu akustycznego/strict-clean boot.
Dowody `C:/aeh-build/device-panels-20261104/fan100-device-owned/report.json`
(SHA `1254d0099fd3b15209f2b6940026e552a47173e55079bcd263f23ae94d6947c3`)
i `fan100-visual-independent-review.json` (SHA
`67d2e54bf4a5a8373f90599705c2c3c5b6d7d3cfcd181ea0deca515f9e01e5e4`).

Po jednym CAS391→392 slot9 otwiera Text, a pełny fan6 nadal ma presety.
Mock preset-only pozostaje w HA. Pierwszy helper promocji zakończył się FAIL
po potwierdzonym zapisie, bo oczekiwał gotowości snapshotów wszystkich stron.
Właściwy test oczekuje gotowości konkretnego slotu po wejściu na jego stronę;
nie wymaga ponownego zapisu układu. `text-launcher100-visual-v2/report.json`
(SHA `2daee248afeb9880947a4b1d1b2aa88a0ad113283ad68333019ff0920768cf73`)
potwierdza rzeczywiste Edytuj/Anuluj i gest zamknięcia; root obejrzał oryginalne
obrazy. Zero komend/usług input_text, konfiguracja i wartość bez zmian.
Pierwsza próba dotykała poza Edytuj, więc jej zapis nie potwierdzał edycji.

## Odbiór Text99a i HA121

Zapis z urządzenia wywołał dokładnie jedną usługę HA; anulowanie i niezmieniony
szkic nie wysyłają polecenia. Sprawdzono polskie znaki/backspace, zmianę źródła
tam i z powrotem przy trzymanym Zapisz, granicę255 znaków i wszystkie dziewięć
wierszy przez sześciowierszowy podgląd. Ukrycie wartości wycofało sesję;
ponowne otwarcie pokazuje tylko „Wartość ukryta”. Są oryginalne screenshoty,
nie ma ciągłego nagrania każdej klatki. Końcowy restore przywrócił helper
text/48 i „Stan demonstracyjny” oraz układ391/Home1.

Jedna wspólna trasa Ustawień:55 FPS źródła, średnio16218 µs, maksimum18464 µs,
zero failed/IRQ. Wobec98 zachowana kadencja, lecz po trasie internal6871 B
wobec14263 B (**−7392 B**); PSRAM4871820 B wobec4908776 B. Statyczny RAM+928 B,
40 nowych obiektów LVGL, stałe bufory Text4648 B w PSRAM. Heap zależy od historii
cache/połączeń. Niższy zapas internal wymaga sprawdzenia przed dalszą alokacją
UI; nie deklarujemy braku regresji pamięci ani długiej stabilności.
Start kwalifikowany z odzyskaną próbą alokacji miksera; cyfrowe audio/wake
potwierdzone, bez odsłuchu akustycznego. Pierwotne FAIL opisują naprawiony
licznik, wejście usługi HA i błędy kolejności testu; nie zostały nadpisane.
Dowód: `C:/aeh-build/device-panels-20261104/text99a-ha121-acceptance-final.json`
(SHA `7f65125c7decc22d1ddb15a2295fdbe778bfa20bae292f16cd9af6651c268ceb`).

## Odbiór Datetime97/98 i HA119

Układ383 ma działający launcher Datetime w slocie29. Testy obejmują trzy
rzeczywiste helpery HA: datę, czas oraz datę z czasem. Trzy komendy urządzenia
i pięć kontrolowanych zmian przez HA potwierdziły zapis, anulowanie, zmianę
źródła przy trzymanym Zapisz oraz blokowanie błędnych dat. Wszystkie wartości
helperów przywrócono. Obejrzano14 oryginalnych screenshotów97 i sześć98;
świeży podgląd w przeglądarceHA119 także pokazuje Datetime.

Poprawka98 zmienia wyłącznie paletę kontrolek: nieaktywny Zapisz ma neutralny
kolor, a poprawny szkic kolor akcentu. Jedna porównywalna trasa Ustawień:
**55FPS źródła, średnio16223µs, maksymalnie18890µs, zero nieudanych prezentacji**.
Po trasie wolnaPSRAM4908776 B, internal14263 B, raportowany zapas stosu6500 B.
StatycznyRAM bez wzrostu; flash+48 B względem97. Historia cache i połączeń
ogranicza porównania bezwzględnych wartości pamięci.

Pierwszy start98 przeszedł jako kwalifikowany: znana próba alokacji zadania
miksera odzyskała się przed dźwiękiem. Potwierdzono pełne230399ramek cyfrowego
dźwięku i działanie wake-word; nie wykonano odsłuchu akustycznego. Gesty były
wstrzykiwane przezAPI urządzenia, nie wykonywane fizycznym palcem.
Dowód: `C:/aeh-build/device-panels-20261104/datetime98-acceptance-final.json`
(SHA `12d8bb42862b21e49e0242a69d1676bdfd59f4d5ff6955e03b4243e7975b4c91`).

## Wcześniejszy odbiór pakietu96 i poprawki edytora118

Układ 379 zawiera Osobę w slocie 18 i Słońce w slocie 23. Zmiana objęła tylko te
dwa wcześniej ukryte miejsca; pozostałe karty, kolejność stron oraz sloty 4/7/30
zachowano. Własny provider obecności wrócił do stanu dom. Nie tworzono nowych
encji ani syntetycznych znaczników czasu.

Odbiór obejmuje Person/Sun, powrót przez istniejący Kalendarz i Zamek,
Home 1/Home 5 oraz 12 oryginalnych screenshotów. Daty i wartości nowych widoków
są zgodne z zapisanymi obserwacjami HA; działają wykrywanie hasła głosowego
oraz cyfrowa ścieżka audio. Dowody dotyczą urządzenia, UART i obrazu ekranu;
nie obejmują odsłuchu akustycznego ani testu palcem fizycznego panelu dotykowego.

Trzy porównywalne trasy Ustawień: **55/55/55 FPS źródła**, średnio
**16191/16183/16124 µs**, brak nieudanych prezentacji i 0 zliczonych ostrzeżeń IRQ
w tej partii. Po drugiej i trzeciej trasie wolna PSRAM wynosiła 4 807 948 B;
pamięć wewnętrzna około 20,1 KB, raportowany zapas stosu 6452 B. Są to wyniki
konkretnego obciążenia i historii widoków, nie obietnica 60 FPS wyświetlacza
ani dowód braku wszelkich przyszłych regresji pamięci.

**HA 118 zamyka błąd pierwszego podglądu.** Metadane widocznych kafelków są
pobierane niezależnie od filtrowanego katalogu. Po odświeżeniu przeglądarki
i otwarciu strony Narzędzia, bez wybierania kart, pojawiły się podpisy
„Obecność w domu” i „Słońce poniżej horyzontu”. Inspector pozostał pusty,
a układ 379 zapisany. Testy JS: 490/490, w tym 10 nowych regresji.
Instalacja wymagała jednego restartu HA; nie zmieniła firmware, układu ani
konfiguracji mocków. Dwa dodatkowe screenshoty Home 5/Home 1 potwierdzają
obraz urządzenia po instalacji; nie są powtórzeniem pomiarów wydajności.
Dowód zamknięcia: `preview118-acceptance-final/report.json` w katalogu poniżej.

Dowody: `info-context96-device-fourth/report.json`
(SHA `f5e5e1aa4039123a6c950a1617d2e976e5047c9b6f773ba8e7f1cedabc9ee7d2`)
i `visual96-context-review/review.json`
(SHA `042889b05d722f21c6a5c454e71b9b894a5837341997097609d4099c00b99558`)
w katalogu `C:/aeh-build/device-panels-20261104`. Historyczne szczegóły prób
narzędzia testowego pozostają w checkpointach.

## Co pozostało

Aktualizacja 7 listopada: firmware115/HA129 ma odebrany widok **Statystyki
godzinowe** dla czujników pomiarowych:24 zakończone godziny UTC, średnia i min–max,
jawny wybór w edytorze, otwieranie/zamykanie na urządzeniu oraz oryginalne
screenshoty. Szczegóły i ograniczenia pomiarów są w
[raporcie Statistics](statistics-2026-11-07.md). Zasadniczą różnicę wolnej pamięci
względem114 wyjaśniła zmiana animacji pogody; mediana Home37,5 FPS i Settings54 FPS
pozostały takie same. Większe pojedyncze opóźnienia pozostają zapisane.

Edytor `input_text` i jego stały launcher są odebrane w opisanym zakresie.
Wentylator100/HA122 zamknął różnicę SET_SPEED|PRESET_MODE i powrót z presetu do
trybu ręcznego. Pakiet stylów101 ma już odbiór urządzenia; niski budżet pamięci
pozostaje ograniczeniem przed dodawaniem nowych obiektów. Odbiór paneli nie
zamyka całego rejestru researchu.

Kolejność kolejnych małych pakietów:

1. **Zachować otwartą diagnostykę historyczną Guru107.** Nowsze testy Agendy114
   i Statistics115 nie odtworzyły awarii, ale nie wyjaśniają jej przyczyny.
   Nie zmieniać historycznych FAIL na PASS. Regresja niebieskich mignięć ma
   osobną poprawkę114 i pomiary w [raporcie wyświetlacza](blue-flash-2026-11-07.md).
   Przy nowej awarii zachować pełny log i przerwać bodźce testowe.
2. **Największe braki istniejących widoków.** Statistics1 jest odebrane w
   opisanym wyżej zakresie; dłuższe okresy i historia stanów są osobnym etapem.
   Przyjazny czas Action i krótsze podpisy launchera Kamery są zamknięte
   w117/HA131. Histereza tylko przy realnym interfejsie providera. Osobno wyjaśnić rzeczywiste szczyty
   kosztu Color; jego odbiór funkcjonalny nie zamyka wydajności.
3. **Operacje wymagające dodatkowej polityki:** odblokowanie/PIN zamka,
   sterowanie alarmem i klawiatura pilota. Params1 zamyka tylko jedno wymagane
   pole Boolean; pozostałe typy, pola opcjonalne i wiele pól wymagają osobnego
   kontraktu i odbioru. Stan nieznany nie może oznaczać zgody na działanie.
4. **Dalsze pozycje researchu:** mapy i procedury robotów, energia, większe
   katalogi, wykresy, prognoza pogody, typowane akcje powiadomień, szablony
   dodatkowych stron i polityka wygaszania. Pozostają w głównym rejestrze
   funkcji; odbiór paneli nie zamyka całego researchu trzech projektów.

Nowe widoki mają zachować Material Design 3, oficjalne SVG i obecne fonty,
jednego właściciela aplikacji oraz współdzielone bufory. Nie dodajemy osobnego
pełnoekranowego bufora ani zadania dla każdej domeny. Otwieranie informacji
nie wywołuje usług; konfiguracja HA nadal wymaga jawnego wyboru i zapisu.

## Zasady dalszych rozszerzeń

- Zachować jednego właściciela sesji i aplikacji App6 oraz współdzielony bufor.
  Kod produktu określa układ i politykę; mechanizmy wykonawcze należą do forku.
- Otwarcie panelu nie wykonuje usługi. HA sprawdza pełną tożsamość sesji,
  uprawnienia, możliwości i generację stanu przed przyjęciem polecenia.
- Zmiana stanu lub możliwości unieważnia nieaktualny gest. Odpowiedź usługi
  oznacza jej przyjęcie; potwierdzenie wartości pochodzi z aktualnego źródła HA.
- Nieznany stan nie oznacza zera, wyłączenia ani pierwszej opcji katalogu.
  Nowe opcje protokołu mają pozostać domyślnie wyłączone i negocjowane.
- Każdy pakiet obejmuje testy kontraktu, a przy zmianie firmware pełny build,
  wgranie, właściwe scenariusze urządzenia i oryginalne screenshoty.
  Wydajność porównywać partiami przy tym samym obciążeniu.
- Nie zmieniać mechanizmów istniejących aplikacji przy okazji dodawania panelu.
  Launcher kamery ma używać istniejącego Home → CameraPreview i jego cyklu życia.
