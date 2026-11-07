# Wznowienie po zatrzymaniu 5 listopada 2026, około 22:40 CET

**Zatrzymane na polecenie użytkownika 6 listopada2026. Czytaj najpierw
[aktualny punkt wznowienia](resume-2026-11-06-sendspin109.md).**

## Bieżący stan — uruchomiony native109, HA127 / układ399; odbiór otwarty

Aktualizacja około22:47 CET: późniejszy read-only odczyt rzeczywiście potwierdził
ELF109, układ399 i Home1, pełne230399 ramek PCM, aktywny wake przez35,77 s,
brak nowych faultów/resetów. Raport `NEW/native109-later-readonly/report.json`,
SHA `2f648ec600fe3ff318cfdfed38a01c90a0996834c91091fac4d6f3d35d899666`.
RAM wewnętrzny22835 B, PSRAM4921176→4921244 B, largest3407872 B.
To późniejsza obserwacja, nie zastąpienie niezaliczonego pierwszego testu.
Osobna kwalifikacja źródłowa startu: `NEW/native109-startup-source-reconciliation.json`,
SHA `d66eb3bc5017b06d12d5dd43ac61d8c36eca53017c770f6d22ee851ce332f07c`.
Interpretacja DSIMEM: `NEW/dsimem109-firstboot-readonly.json`, SHA
`bfe800a74d8663b88f4ad0ed57608ac40940aa626d599a12cfbd5cf2ef26bd7e`.
Brak danych wskazujących konkretną nową poprawkę; dopuszczono jedną diagnostyczną
trasę Agenda→Home na109 z osobnym admission, zachowując FAIL pierwszego bootu.
Nie oznacza to jeszcze wykonania tej trasy ani odbioru wydajności/stabilności.

Aktualizacja 6 listopada, około22:43 CET: pełny build109 i linked audit przeszły.
ELF `e679aeb10b33cae33cf7d456b88b97245bec569f9f62c3658811080dbf43b9d5`;
linked `NEW/stack109-sendspin-linked/report.json`, SHA
`53fcb9e635b9ebcf8263e1507717d08e98db7cdd1701bcede217e8446c8333a4`.
Capture receipt ma finalny status `BUILT_SENDSPIN109_NOT_FLASHED`, SHA
`3d0242c0947dc8e4cc96854fb2a93574ec3c43823b462faf6f342b0edffdfa4a`.
Jedna OTA109 zakończyła się powodzeniem; artefakt
`D:/aeh-build/native-context-v109/manifest.json`, SHA
`065a1bc65d8febd8d0bb65afbff469742fb64ef638c6163de7aa2197f2016a24`.

Pierwszy boot109 odzyskał Sendspin po dwóch rzeczywistych nieudanych startach
zadań (Protocol i Sync), bez abort/Guru/rollback. Marker mówi `running; retries=2`.
**Oryginalny test pozostaje FAIL/UNCLASSIFIED**, ponieważ runtime log filter
nie pokazał nowych markerów Worker WARN z fazą i errno. Raport
`W/panel109-firstboot/first-boot.json`, SHA
`aa672b17ef424e558f4345e4a3504793df074aae8d2a736ebf946c54c4120c89`;
zamknięty rawUART obok, SHA
`f1d8c698031906d1ae2c4eb0c9e79372f442ca9e6b5da0441113302767e61a5a`.
Nie zmieniać tego raportu/logu ani ponawiać OTA dla samego filtra. Pełny licznik
audio i35 s wake nie zostały jeszcze sprawdzone przez ten przerwany test;
następny krok to osobna kwalifikacja źródłowa widocznych E-caller/retry/running
oraz późniejszy read-only odczyt gotowości109/399.

Boot109 ma także dwa DSI underrun i jeden kompletny, ale poprzedzony fragmentem
innego logu DSIMEM1. CPU timeout raw=0x2c; MSPI raw=0x18; cache statusy=0.
Te słowa wymagają interpretacji — nie stanowią jeszcze dowodu przyczyny Guru107.
Trasa Agendy109 i trzy restarty nie zostały wykonane. Przed diagnostyczną trasą
trzeba osobno rozpatrzyć wynik pierwszego bootu i aktualny stan; nie przedstawiać
jej jako odbioru stabilności. Statystyki i nowe funkcje nadal wstrzymane.

Aktualizacja 6 listopada, około22:25 CET: trwa pełna kompilacja kandydata109.
Kanoniczne źródła i build junction wskazują już109; urządzenie nadal107.
Źródła `W/source-v109-build.json`, SHA
`6d2ed5b83095aa6938df84884455efab763282ba18beb1736b2e11b33febb883`.
Dostawa `C:/aeh-build/sendspin109-native-work/delivery-v2/manifest.json`, SHA
`6739856f128ceeb21319c94db99d69931940a78df1fc7e9d904ad77262a1f8e5`.
Obejmuje kontrolowane tworzenie zadań Sendspin, cleanup niepełnego startu
i maksymalnie cztery ponowienia po błędzie zasobów. Zachowuje diagnostykę108,
rozmiary stosów, bufory i liczbę zadań. Host/schema/codegen/P4 TU oraz osobny
przegląd źródeł przeszły; pełny linked audit i wszystkie testy sprzętowe109
są jeszcze przed nami. Nie oznaczać109 jako odebranego ani wgranego.
Capture: `NEW/native109-capture-first/receipt.json`; jego aktualny status jest
źródłem prawdy po zakończeniu procesu. Nie uruchamiać capture ponownie.
Po build: linked audit, jedna OTA ze świeżym preflight107/399, pełne audio
startowe i35 s wake oraz rzeczywisty marker Sendspin running. Następnie jedna
diagnostyczna trasa Agendy, dopiero po jej przejściu krótka partia trzech
restartów. Guru107 nadal nierozwiązany; Statistics1 pozostaje wstrzymane.

Aktualizacja 6 listopada, około21:47 CET: diagnostyczny108 przeszedł config,
pełny build i actual linked audit, lecz pierwszy rozruch po jednej OTA zakończył
się `pthread: Failed to create task` i abort. **Nie ponawiać tej samej OTA.**
Raport `W/panel108-firstboot/first-boot.json`, SHA
`fd0326b831d7e5fb47b96c6396a5d842a8f1641bb2a29bbae59fb34aae91cc81`.
ELF108 `d80f922e4e4ab9df373a733d9eb9aa10aa12ed593fafcff9f2375d393148fec1`;
źródła108 `1125153d5b07d1f652dfa3aab5c7c9541e4a9a36ecdeef25fc428a66f2dd2dbb`.
Odczyt stosu wskazuje `SsProto`/Sendspin `ProtocolTask::start`, nie mikser:
nieudane utworzenie zadania7168 B przez pthread przechodzi przez `std::thread`
do abort przy wyłączonych wyjątkach, pomijając istniejący cleanup dla `false`.
Stos protokołu już jest skonfigurowany w PSRAM; log nie rozstrzyga, czy zabrakło
samego stosu, czy wewnętrznego TCB. Diagnostyka dodała730 B statycznego SRAM.

Automatyczny rollback do107 potwierdzono dwoma odczytami i35 s pasywnego UART:
`NEW/native108-rollback-readonly/report.json`, SHA
`a4b647de2bc3ba24ed6554f8b5ec494d6385e4043a3804f183b2e52294131b21`;
plik `context.json` obok wskazuje nieudany108 jako powód tego nowego odczytu.
Home1, HA127, układ399,230399 ramek audio i wake poprawne; brak nowych faultów.
Nie wykonano trasy ani screenshotów108. Przyczyna Guru107 pozostaje otwarta.
Kanoniczne źródła i build junction mają diagnostyczny108, urządzenie nadal107.
Następny krok: naprawić obsługę niepowodzenia tworzenia zadania Sendspin i
sprawdzić cleanup/ponowny start, potem nowy kandydat109 oraz diagnostyka Agendy.
Nie łączyć z zapisanymi, nadal wstrzymanymi Statistics1.

**Przerwać rozwój nowych funkcji do wyjaśnienia Guru107.** Ostatni odebrany
checkpoint pozostaje native105 / HA126 / układ398. Bieżące urządzenie ma
native107, serwer HA127 i układ399; to stan po awarii, a nie nowy pełny odbiór.
Nie ponawiać migracji slotu12 ani zakończonych restartów tylko dlatego, że
starszy checkpoint opisuje105. Przed kolejnym zapisem odczytać aktualną
tożsamość i pełny układ. Bez Git commit/push.

Źródła107: `C:/aeh-build/native107-sources`, manifest `W/source-v107-build.json`,
SHA `08d97629719cd2884d7f5442297897e4ee87fd629ee7c29f63d7f1a2426b9686`.
ELF `f46464b6656603b3b4b263a88e27ecd0a6aaff8cd10a89147109423411492c70`;
artefakt `D:/aeh-build/native-context-v107/manifest.json`, SHA
`9de74b7c94502f9ee80002411dccbd7d8db21f2b39e801859d29192c10f152ed`.
Pierwsza kompilacja zatrzymała się na archiwizacji z ENOSPC; jej FAIL zachowano.
Kontynuacja `native107-disk1` z tymi samymi źródłami przeszła pełny build i
linked audit. `NEW/native107-disk1-continuation.json` ma SHA
`08765a1b9b0985471c0788586963038ca8baa0f269b817a0623dd15eac2850f3`.

**Zaliczone, ograniczone dowody107:** pierwszy boot po jednym OTA potwierdził
pełne230399 cyfrowych ramek i35 s wake bez Guru. Pięć kontrolowanych restartów
programowych i siedem lokalnych odtworzeń także przeszło; pięć oryginalnych
obrazów Home było kompletne. Pozostaje znany odzyskany retry4096 B stosu
miksera, więc `strict_boot_passed=false`; brak odsłuchu i testu fizycznego
odłączania zasilania. Raport restartów `NEW/mixer107-restarts-first/report.json`,
SHA `c17e8d674174e857dc91e018592120328f02672c3f3b734ac88b977cfa6eeec1`,
oraz osobny `NEW/mixer107-restarts-visual-review.json` nie dowodzą stabilności
późniejszego przebiegu Agendy.

HA127 rzeczywiście zainstalowano: `NEW/agenda-ha127-deployment-first.json`,
SHA `9315b93a04d7500122c9cbe86e166f303ae770e95ee8c75a96836ac7798f880f`.
Jedyny CAS398→399 zmienił akcję własnego slotu12 na Agendę. Sześć odczytów
PAGE pokazało sześć wydarzeń; ponowne otwarcie dało ten sam obraz pierwszego
wpisu. Nie wysłano COMMAND ani usług providera. Siedem oryginalnych JPEG
przeszło częściową ocenę układu, fontów i kontrastu; porównanie pikseli
potwierdziło wspólny nagłówek i daty. Pomijanie niezmienionych fragmentów
przez podgląd narzędzia nie było ubytkiem rzeczywistego framebuffera.
Dowód: `NEW/agenda107-originals-ui-review.json`, SHA
`e5063e1f62283e964029b79fca5ee699e657b335e469e6eab2be7d82e941687c`.
Edytor HA127 pokazał „Otwórz agendę”, zapisany układ399 i brak szkicu;
`NEW/agenda127-editor-observation.json`, SHA
`bb9d591dbd64b1e8ef9ed97bbaa038baf0e1bc397fc548f2d702247715c9eb2c`.

**Rzeczywista awaria107:** po zamknięciu App6 i powrocie na Home, przed
partią Settings, wystąpił Core1 Load access fault. Raport pozostaje FAIL:
`NEW/agenda107-device-first/report.json`, SHA
`44c1be468c3f9054a767364dd953534745ef5ff61d680732e950c8f750104a52`.
Pełny UART jest obok w `device-uart.raw`. Nie ukończono końcowego pomiaru
Settings/FPS/pamięci ani końcowej kontroli audio tej partii; nie ma odbioru
Agendy jako całości. Timeout odczytu `debug_audio_output` nie przypisuje
przyczyny audio. Dekodowanie ELF wskazało malloc/TLSF w ścieżce logowania
lwIP/diagnostyki DSI. MTVAL0x48000290 odpowiada prawidłowemu adresowi metadanych
alokatora; nie jest sam w sobie dowodem uszkodzonej sterty ani błędu cache.

Przegląd źródłowy nie znalazł konkretnego nowego OOB/lifetime w Agendzie:
tekst z ograniczonego JSON jest kopiowany do ownera i przez `lv_label_set_text`,
a kod nawigacji, kompozytora, Lottie i DSI pozostał bajtowo taki jak w105.
Końcowy ciąg close/Home/odczyt jest wspólny z105, lecz wcześniejsze PAGE,
screenshoty i historia pamięci różnią się. Nie wprowadzać pełnego kopiowania
framebufferów ani zmiany własności na podstawie artefaktu podglądu.

Odczyt po awarii `NEW/agenda107-after-fault-readonly/report.json` (SHA
`100ad27b2ce5ab48bcf94742c02b70dbf968c19af02b37fdc44e1daa55d093dd`)
potwierdził107/127/399/Home1,230399 cyfrowych ramek i wake;35 s pasywnego UART
nie zawierało nowych faultów. Bez restartu, odtwarzania, zmiany widoku,
usług ani CAS. To potwierdza odzyskany stan, nie usuwa wcześniejszego FAIL.
Cztery zewnętrzne wywołania `provision_pipecat` pozostały nieprzypisane;
nie wolno zakładać ciszy innych użytkowników/procesów.

**Plan sprzed próby108:** minimalna diagnostyka rejestrów rzeczywistego
faultu, potem potrzebna weryfikacja naprawy i niedokończony odbiór powrotu
Home/Settings. Aktualny następny krok opisano na początku pliku. Zachować zaliczone
restarty, PAGE, screenshoty i CAS jako dowody, nie powtarzać ich bez powodu.
Statistics1 zapisano i wstrzymano w `C:/aeh-build/statistics108-ui-work`;
checkpoint `checkpoint-paused-20261106.json`. Ten katalog to wcześniejsza
izolacja funkcji, nie diagnostyczny108. Wymaga późniejszej nowej bazy/numeru;
native max-storage codec ma nierozwiązany wynik FAIL i nie ma zamrożonego
gate. Nie łączyć statystyk z poprawką awarii.

Historia106 pozostaje osobna: pierwszy chime boot zakończył się Guru przy
niszczeniu shared control block miksera i automatycznym powrotem do105.
`NEW/crash106-mixer-readonly/report.json` dokumentuje ignorowany wynik
inicjalizacji pthread mutex; presja pamięci jest hipotezą źródłową, nie
przechwyconym wynikiem inicjalizacji.107 zastąpił tę sesję jednym właścicielem
ring/reader i lease, z niszczeniem w main loop po ostatnim lease; bez nowego
PCM, zadania lub pojemności ringa. Patrz [własność audio](../architecture/audio-voice.md#mixer-session-handoff).
Osobny `C:/aeh-build/mixer107-native-work/test-runner-followup-v1/manifest.json`
(SHA `8e5629aa443bf9a0b684face2034fb3cfbd314ed4577022dac4237a313163917`)
zawiera tylko skip testu bez `ESPHOME_TEST_CXX`, do następnego capture;
nie zmienia niezmiennego107 ani runtime. Rzeczywiste szczyty Color,
ograniczenia pamięci i brak strict-clean boot pozostają otwarte.

## Ostatni odebrany checkpoint — native105 / HA126 / układ398

Odebrano **native105**, HA **0.4.0.dev126**, Core2026.11.0, układ **398**,
Home1. Raport `NEW/range105-acceptance-final.json`, SHA
`eb9e23d990221b6710354976054fa9ceca9fb16cbdebedb4c584f85ae7bdb1c4`,
ma status `PASS_SCOPED_CLIMATE_RANGE_DEVICE_AND_VISUAL`. Wiąże źródła,
pełny ESP-IDF build, linked audit, jedno OTA, kwalifikowany boot, niezmienione
HA126, pięć oryginalnych screenshotów i przywrócenie układu. Nie powtarzać
zakończonych testów lub CAS na podstawie historycznych sekcji poniżej.

Źródła: `C:/aeh-build/native105-sources`; manifest
`C:/aeh-build/notification-cards-20261102/source-v105-build.json`, SHA
`9f71ba5251d1c2ecf62c8f9db68eec916bcd68cc04771998ab5ac2d32f81fcbf`.
ELF `aa92cb8edda9323ae054758215d6a87bf832c5a3070eddf1f230d9177c925f90`.
Oryginalny artifact pozostaje w `D:/aeh-build/native-context-v105`.

Range1 używa istniejącej tarczy600px. Dolny/Górny wybierają próg,
przeciągnięcie ogranicza go do drugiej granicy, puszczenie wysyła jedną
absolutną parę. Równość granic jest legalna; nie ma osobnego Zastosuj.
Dodano tylko przycisk Zakres z etykietą, używając Mode/Parameters jako
Dolny/Górny, a Zakres jako Wstecz. Kontrakt i kwalifikację jednostek opisuje
[Climate Range1](../architecture/ha-climate-range.md).

Native105 domknął błąd wyglądu104: MAIN pokazuje znaną parę21–24 °C dużym
napisem również po powrocie z Range. Jedyny plik runtime105 zmienia tekst,
korzystając z istniejących low/high, bufora72 B i skonfigurowanej czcionki.
Para musi być znana, uporządkowana, w dostępnym heat_cool i bez pojedynczej
nastawy. Długi zapis otrzymuje w hero lokalizowane „Zakres”, a dokładna para
pozostaje niżej; wartości nie są zaokrąglane, by zmieścić je na ekranie.
Nie zmieniono wire, ownera, edytowalności, pozycji kropki, fontów, geometrii,
wariantu danych, HA126 ani istniejących aplikacji.

Runtime105 `NEW/range105-device-first/report.json`, SHA
`5d17468444e8c3f273e10ae3886c0fc9c461d7d159334a6e777c3da69998b575`,
potwierdza MAIN→Range→MAIN, stary pojedynczy termostat21 °C oraz Home1,
**zero native COMMAND i zero usług providera**. Dwa CAS tylko własnego slotu16
wykonały396→397→398 i przywróciły dokładnie oryginalne karty. Nie wysyłano
usług do fizycznego termostatu Iwona Pellets. Root obejrzał pięć oryginalnych
JPEG800×800. MAIN przed i po Back jest identyczny bajtowo, bieżąca temperatura
i aktywność zachowują te same piksele. Pominięte wspólne regiony podglądu
narzędzia nie są ubytkiem obrazu urządzenia.

Jedna trasa Ustawień: **55 FPS, avg16074 µs/max18024 µs, failed0**, bez błędów
DSI/UART; wcześniejszy104 miał55 FPS/16254/19763 w swojej trasie. Końcowo
internal23231 B, PSRAM4940528 B. Nie ma wzrostu statycznego RAM/komponentu,
nowego obiektu, bufora ani zadania; flash+512 B, ramka zmienionej funkcji+16 B.
Wolny heap zależy od historii/cache, więc ten przebieg nie dowodzi braku
wycieku ani ciągłych60 FPS. **Sporadyczne szczyty kosztu Color pozostają
nierozwiązane**; poprawka105 ich nie dotyczy.

Pierwszy boot105 jest **kwalifikowany**: pełne230399/230399 ramek cyfrowego
audio i35 s gotowości wake, z odzyskaną znaną próbą alokacji4096 B stosu
miksera przed dźwiękiem. Nie jest to strict-clean boot ani odsłuch. Scenariusz
używał publicznej ścieżki diagnostycznego dotyku realnej Atmosfery i własnego
demo HA; nie potwierdza fizycznego palca, regulatora ogrzewania ani lampy.

**Dalsza praca:** diagnoza rzeczywistego Guru107 i domknięcie niedokończonego
odbioru Agendy, zgodnie z bieżącą sekcją powyżej. Nie powtarzać ukończonych
CAS394→395→396 ani396→397→398. Backlog: rzeczywiste szczyty Color, krótsze
podpisy Kamery, przyjazny czas Action, histereza i osobna kwalifikacja
konwersji jednostek. Bez Git commit/push.

## Historia — kwalifikowany Range104 / HA126 / układ396

Raport `NEW/range104-acceptance-final.json`, SHA
`7b8fafb6bb2924d2863c67a674160b3f8e0c25ef92515680c9db4da8394fd722`,
pozostaje `PASS_SCOPED_CLIMATE_RANGE_WITH_MAIN_DISPLAY_FOLLOWUP`; jego
statusu nie podniesiono wstecznie. Batch104 potwierdził trzy komendy pary
oraz jedno publiczne przywrócenie źródła podczas trzymania. Otwarcie, wybór
progu, unchanged, Back i release po zmianie źródła nie dodały polecenia.
Przywrócono oryginalne karty/396/Home1. Dziesięć oryginalnych screenshotów
potwierdziło Range, równość i anulowanie gestu, lecz MAIN miał duże `-- °C`
nad małą poprawną parą. Ten konkretny follow-up zamyka osobny odbiór105.

Config/generacja,52 sprawdzenia fontów/geometrii,12 public LVGL oraz209
powiązanych testów HA/26 komunikatów pozostają dowodami host104. P4 probe:
Range96 B w istniejącym wariancie, Snapshot728/Message960/owner1160 bez
wzrostu, komponent+16 B; linked static+184 B. Settings104:55 FPS,
avg16254 µs/max19763 µs, failed0; końcowo internal23071 B/PSRAM4941552 B.
Probe, linked i wolny heap są różnymi pomiarami. Boot był kwalifikowany przez
odzyskany retry miksera. Histereza, cross-unit i parametry producenta nie są
zakresem104/105.

Poniższe sekcje zachowują historię i ówczesne plany.

## Historia — odebrany native103 / HA125 / układ394

Odebrano **native103**, HA **0.4.0.dev125**, Core2026.11.0, układ **394**,
Home1. Finalny raport `NEW/color103-acceptance-final.json`, SHA
`7f10d9a5af0b42ee8fc455247c9eec17bcd083088dc8e1d05cc3979e63812945`.
Source `e76407eb2a3489ab5eba84f256c5d6a76a9f3ece75827f23a20186faf3d7ade3`,
ELF `586ef859f6c6f189d38fff7586ea364677ce43901d5a4016ad03b8434171b251`.
Pełny ESP-IDF build, linked audit i jedno OTA zakończone. Nie zmieniono układu
karuzeli ani mechanizmów Player/Kamera/Galeria/Asystent.

Color1 rozszerza istniejący Light Detail/App6. Dwa suwaki H/S tworzą lokalny
szkic; Anuluj nie wysyła usługi, Zastosuj wysyła jeden jawny wybór. Z trybu
temperatury bieli „Przełącz na kolor” działa także na nieruszonym seedzie.
Próbka bez edycji pokazuje RGB źródła, zmieniony szkic V255; motyw nie nadpisuje
jej koloru. Jasność pozostaje osobnym sterowaniem i jest zachowywana dokładnie
przez HA. Kontrakt: [Light Detail Color1](../architecture/ha-light-color.md).

Na własnym demo `light_2` sprawdzono **dwie komendy native i po jednej usłudze
HA dla każdej**: CT→HS oraz zmieniony H/S. Otwarcie, Anuluj, unchanged i close
nie wysłały poleceń. Trzecia usługa providera była jednym kontrolowanym
przywróceniem oryginalnej temperatury2631 K i surowej jasności180; odebranie
tego stanu podczas trzymania suwaka anulowało gest, release nie wysłał komendy.
Układ394 i inne encje zachowano. Runtime `NEW/color103-device-first/report.json`,
SHA `abdb6a8e73a5038caca2bcd9d106392ebca6f7193090fc177673bf243081bef0`.
HA deployment `NEW/color-ha125-deployment-first.json`, SHA
`e216e9e565169b74596453d5ebed294e39e8eefc5bf24ad1bbfe6b208171126a`.

Root obejrzał **osiem oryginalnych screenshotów800×800**: CT, dwa szkice,
zatwierdzenia, reopen, przywrócenie podczas dotyku i pełny Home. Obraz reopen
jest identyczny z zatwierdzonym, przywrócony z seedem; stałe wspólne regiony
potwierdzono pikselami oryginałów. Znikające wspólne fragmenty w podglądzie
narzędzia nie były ubytkiem urządzenia. Wejście pochodziło z diagnostycznej
ścieżki dotyku na realnej Atmosferze; bez nowego testu fizycznym palcem/lampą.

Jedna trasa Ustawień: **55 FPS, avg16100 µs, max18079 µs, failed0**, bez błędów
UART/DSI; wcześniejszy102 miał54 FPS/16307/20183 w swojej trasie. Osobny sampler
dwóch istniejących dragów Color: **loop avg13.544 ms, max61.873 ms,10>30 ms**,
flush avg9.796 ms/max25.912 ms. Sampler wyłączono przed screenshotem. Okno
obejmuje też API i przerwy wejścia: to nie dowód ciągłego60 FPS ani braku
przycięć. Same wartości loop avg/max są rzeczywistymi kosztami wykonania,
których przerwy wejścia nie wyjaśniają. Przegląd źródła nie znalazł pełnego
odświeżania drzewa przy każdym ruchu: `NEW/color103-draw-source-review.json`,
SHA `82866850bd8b9567ec65d554deab9406ff056017f205a866aba8bc410e4d6916`.
**Sporadyczne szczyty kosztu Color pozostają do wyjaśnienia.**

Końcowo internal23035 B, PSRAM4763156 B. Statyczny RAM310476 B (+320 względem
102); produkt dodał15 obiektów, bez nowego zadania/bufora pełnego ekranu.
Probe P4: Color16 B/draft20 B, owner+24 B, komponent+80 B łącznie z ownerem;
Snapshot728/Message960 bez wzrostu. Wolna pamięć zależy od historii/cache:
nie przypisywać całej różnicy PSRAM nowym widżetom ani nie deklarować braku
wycieków. Zachować rozróżnienie statycznego ABI i rzeczywistego liveheap.

Pierwszy boot103 jest **kwalifikowany**:230399/230399 ramek cyfrowego audio,
wake gotowe, zdrowy UART; zachowana znana odzyskana próba4096 B stosu miksera
przed dźwiękiem. Nie jest to strict-clean boot ani odsłuch. Dowody boot,
artifact, linked i oryginalne obrazy są przypięte w finalnym raporcie.

## Historia — odebrany native102 / HA124 / układ394

Aktualny odebrany stan: **native102**, HA **0.4.0.dev124**, Core2026.11.0,
układ **394**, Home1. Raport `NEW/camera124-acceptance-final.json`, SHA
`f89ed5a63fc00acd24fd90d1aa9ad2a492bc714b4a1241b2e3f6ef4ced9c9cdb`.
Firmware jest ten sam co w102/HA123: ELF
`481f6822d7d8ede3c40f63d0b9888dba12300efc6ae948a64eb989afd7e0fe0c`.
Nie było nowego build, OTA ani zmian natywnego mechanizmu Kamery.

Jeden CAS393→394 zastąpił tylko slot30 jawnym launcherem CameraPreview35 s.
Rzeczywiste zwolnienie kafelka Home otworzyło Demo camera w istniejącym App5;
bez polecenia do mockbutton, tile_event i bez jawnej usługi providera.
Standardowe zamknięcie od dołu wróciło na Home5. Zwykła aplikacja Kamera
nadal wyświetliła uprzednio wybrany Public Aquarium Stream. Obie sesje
zakończyły się idle i source_kib0; wspólna kolejka134 KiB pozostała zachowana.
Root obejrzał pięć oryginalnych screenshotów800×800, w tym końcowy Home1.

W dwóch oknach po około3 s zmierzono **13.237 FPS prezentowanych** dla Demo
i **10.932 FPS** dla Aquarium. To różne źródła, nie porównanie regresji tego
samego strumienia ani obietnica60 FPS. Końcowo internal19307 B,
PSRAM4490736 B, cyfrowe audio230399 ramek, wzmacniacz aktywny/bez wyciszenia
i wake-word gotowy. Pamięć zależy od odwiedzonych podglądów; statyczny firmware
nie zmienił się. Bez dowodu braku wycieku, fizycznego dzwonka/palca i odsłuchu.
Wcześniejszy kwalifikowany boot102 z odzyskaną próbą4096 B stosu miksera
pozostaje obowiązującym ograniczeniem.

Pierwotny raport `NEW/camera124-device-first/report.json` zachowuje **FAIL**:
po zakończeniu asercji i zapisie finalnego układu obserwator otrzymał normalne
zamknięcie WebSocket1000 zamiast oczekiwanego tekstu. Błąd kolejności sprzątania
obserwatora wyjaśnia wynik; nie zmieniono jego statusu. Odczytowa kontrola
`NEW/camera124-readonly-reconciliation/report.json`, SHA
`21325f07b96c166beb22c25821921ee1c2b02c90e1d27f380a1bfc639768df99`,
potwierdziła394/Home1, źródło, idle i audio. Nie powtarzała CAS, naciśnięcia
kafelka ani strumieni. Nie należy ponawiać zakończonej migracji394.

**Następna praca:** konkretny widok koloru światła w istniejącym Light/App6,
z własnym lokalnym szkicem i kontrolą pamięci; plan nie jest implementacją.
Nie używać stanu ani skryptów pickera akcentu do zmiany koloru lampy.
Do późniejszej partii HA/UI dopisać krótszy tytuł/podpis launchera kamery
(na gęstej stronie tekst ma wielokropek) i przyjazny czas Action, bez zmiany
formatu ISO protokołu. Bez osobnej kompilacji/restartu dla tych kosmetyków.
Bez Git commit/push.

## Historia — odebrany native102 / HA123 / układ393

Poniższy stan i ówczesny planHA124 dokumentują punkt393; aktualny stan jest
powyżej. Nie powtarzać zamkniętych testów i migracji z tej historii.

Odebrany stan to **native102**, HA **0.4.0.dev123**, Core **2026.11.0**,
układ **393**, Home1. Raport `NEW/tile-event102-acceptance-final.json`, SHA
`4175a0abbe0f8abd0177618fca6bd7137cf271f76dbd926f9dda844d06ff3cfa`,
wiąże source `3e87f5e9a309dc84d977090aa5e0f02df8565cdb6a98872ad586880037f6454d`
i ELF `481f6822d7d8ede3c40f63d0b9888dba12300efc6ae948a64eb989afd7e0fe0c`.
Slot23 „Zdarzenie HA” otwiera dedykowany panel istniejącego App6 Action2;
dodatkowy profil tile_event:1 jest negocjowany jawnie. Otwieranie i zamykanie
nie wysyła zdarzenia. Jedno świadome zwolnienie przycisku w panelu daje jedną
komendę native, aktualizację EventEntity i publiczne zdarzenie HA
`atmosfera_echo_hub_event` z tym samym kontekstem. To potwierdzenie przekazania
zdarzenia, nie ukończenia uruchomionej przez użytkownika automatyzacji.

Pierwszy użyty panel bez historii, wynik przekazania, ponowne otwarcie historii
i standardowe zamknięcie zostały sprawdzone na urządzeniu. Root obejrzał
oryginalne screenshoty pierwszego użycia, launchera, wyniku, ostatniego użycia
i końcowego pełnego Home. Dotyk podano przez diagnostyczną ścieżkę wejścia
urządzenia; brak nowego potwierdzenia fizycznego gestu i oceny każdej klatki.
Slot6 pozostaje pełnym wentylatorem, slot9 Text, slot29 Datetime. Slot30 nadal
uruchamia test dzwonka; nie został jeszcze zastąpiony launcherem kamery.

Historia nieudanych prób pozostaje zachowana:

- Pierwsza próba wgrania zatrzymała się **przed OTA** na audycie tłumaczeń:
  cała gałąź zawiera49 przypisań, lecz zwykła tabela nadal46. Zawężono stary
  pomiar do tabeli, zachowując odrębne kontrole3 nadpisań zdarzenia. Firmware
  nie zmieniono; osobna kontynuacja zakończyła audyt i OTA.
- Pierwszy test urządzenia wykonał CAS392→393 i jedno rzeczywiste zdarzenie,
  lecz nasłuchiwał niewłaściwej nazwy magistrali. Raport zachowuje **FAIL**,
  także kontrolę właściciela opartą na nieaktualnym oczekiwanym stanie event.
  Kontynuacja odczytała świeży393, źródła i zamkniętą sesję, bez ponownego CAS.
  Nowe pojedyncze naciśnięcie potwierdzono na właściwej magistrali oraz encji.
  Runtime `NEW/tile-event102-bus-continuation-first/report.json` ma SHA
  `030692268f4e257397abacaf52867109d2b21ce3c077e7748b197b118fe86a20`.
  Końcowy raport wiąże oba pierwotne FAIL; nie zmienia ich statusów.

Jedna trasa Ustawień: **54 FPS źródła, średnio16307 µs, maksimum20183 µs**,
failed0 i brak błędów UART/DSI. Po trasie internal23547 B, PSRAM4942768 B;
końcowo internal23587 B. Statyczny RAM310156 B pozostał bez zmiany względem101.
Historia cache różni się od101: nie jest to dowód odzyskania pamięci, braku
wycieków ani uniwersalnego60 FPS. Start pozostaje **kwalifikowany**: znana
odzyskana próba alokacji4096 B stosu miksera przed dźwiękiem,230399 ramek
cyfrowego audio i36.012 s obserwacji wake. Bez strict-clean boot i odsłuchu.

**Następny etap:** HA124 ma izolowaną implementację jawnego launchera kamery
Home → istniejący CameraPreview/App5. Nie został wdrożony ani odebrany na
urządzeniu. Zachowuje mechanizm Kamery, bieżący katalog dozwolonych źródeł,
uprawnienia i kontrolę tożsamości kafelka; nie używa mockbutton ani pośredniego
App6. Następnie mały widok RGB światła z osobnym budżetem pamięci. Drobny
backlog: przyjazna prezentacja czasu ostatniego użycia Action, bez zmiany
ścisłego formatu ISO w protokole; dołączyć do późniejszej partii bez osobnego
build tylko dla tej kosmetyki. Nie powtarzać odebranego102 ani CAS393.
Bez Git commit/push.

## Historia — odebrany native101 / HA122 / układ392

Poniższy stan i ówczesny plan102 dokumentują punkt101; bieżący stan znajduje
się powyżej. Dawne „bieżąca praca” nie oznacza nowego zadania do powtórzenia.

Odebrany stan to **native101**, HA **0.4.0.dev122**, Core **2026.11.0**,
układ **392**, Home1. Raport `NEW/text101-acceptance-final.json`, SHA
`8a40ae039f1bb4da05b57c170886edbbdd7cf8d8c8ccd0a98e5745274804f98b`,
wiąże source `128d11e2be0d0d821e6ccebb68407cdb1b0365897a2c34b84a9b7d50288948c1`
i ELF `43eb2f11f90610a935fa9c4c6ec76e6817b2c087881aa8f9717a3cd3e4378ce5`.
Zmiana101 współdzieli style Text; geometria, paleta i obsługa wejścia nie
zmieniły się. Nie dodano bufora, zadania ani widżetu. Szacunek usuniętego
wyrównanego payloadu heap wynosi2624 B; rzeczywisty statyczny RAM wzrósł64 B
do310156 B. Nie utożsamiać oszczędności heap z odzyskiem internal SRAM.

Na urządzeniu sprawdzono podgląd, klawiaturę, lokalną edycję, stany przycisków,
Anuluj i standardowe zamknięcie. Sześć oryginalnych JPEG: podgląd i klawiatura
są identyczne z100, a obraz po Anuluj z podglądem. Root obejrzał klawiaturę,
zmodyfikowany szkic i końcowy pełny Home. Zero komend/usług providera,
konfiguracja oraz „Stan demonstracyjny” zachowane. Runtime
`NEW/text101-device-first/report.json`, SHA
`21b3b1c79ae97a4c967c0547f300095d824112f67e2d93ae92baa4e3cf66aef3`.
Właściwy Zapisz/255/ABA/password pozostają dowodami wcześniejszego99a/HA121,
nie zostały ponownie wykonane ani przypisane testowi stylów101.

Jedna trasa Ustawień: **55 FPS źródła, średnio16148 µs, maksimum18833 µs**,
failed0/IRQ0. Po trasie internal13151 B wobec13295 B dla100 (**−144 B**),
PSRAM4880132 B. To pomiary zależne od historii cache; nie dowodzą odzyskania
wcześniejszej różnicy7392 B, braku wycieków ani uniwersalnego60 FPS.
Start101 pozostaje **kwalifikowany**: pełne230399 ramek cyfrowego audio,
35.988 s cyklu wake-word, znana odzyskana próba4096 B stosu miksera przed
dźwiękiem. Bez strict-clean boot i bez odsłuchu akustycznego.

Pierwotny build101 zachowuje FAIL po wyczerpaniu miejsca na C:. Dokończone
linkowanie użyło tego samego source i581 plików wygenerowanych; raport
`C:/aeh-build/notification-cards-20261102/compile-native101-link-resume-process.json`
ma SHA `fed5c491dee2347eed57cde62297956b26e580526e46da389abf2e392fa1ac84`.
Nie powtarzać zakończonego odbioru101 ani migracji układu392.

**Bieżąca praca:** native102/HA123 dodaje jawny panel zdarzenia kafelka przez
istniejący App6 Action2. Dostawa native102 jest zamrożona i przekazana do
kompilacji; nie ma jeszcze odbioru urządzenia ani instalacji HA123. Host
codec/owner/default-off i6 scenariuszy public LVGL przeszły, target probe nie
wykazał wzrostu struktur; nie zastępuje to pełnego build/OTA/screenshotów.
Manifest `D:/aeh-build/tile-event-native-work/delivery-v1/manifest.json`
SHA `928b35501837c9a73a8027c458da84105c32ff726d65ccca982559cb5450e92a`.
Układ pozostaje392; nie zakładać jeszcze panelu zdarzenia w slocie23.

Następny uzgodniony kierunek HA124 to jawny launcher kamery bezpośrednio
Home → istniejący CameraPreview/App5, bez pośredniego App6, mockbutton i
automatyzacji. Implementacja wyłącznie izolowana, bez zmian native Camera;
nie jest jeszcze odebrana. Zachować bramki katalogu, uprawnień i bieżącej
tożsamości kafelka. Bez Git commit/push.

## Historia — odebrany native100 / HA122 / układ392

Poniższy stan i „następny etap” dokumentują ówczesny punkt100; bieżący stan
oraz plan znajdują się powyżej.

Na urządzeniu jest **native100**, HA **0.4.0.dev122**, Core **2026.11.0**,
układ **392**, końcowo Home1. Zbiorczy odbiór `NEW/fan100-acceptance-final.json`
(SHA `1a30b91d3a75dabed734c48feb00e20a52d24513090af132a1430d1aebd185ca`)
wiąże poniższe próby i ograniczenia. Wentylator przeszedł cykl ręczny → preset →
ręczny na własnych mockach, także wariant z samymi presetami. Nieznany procent
po wybraniu presetu pozostaje „--”; powrót wybiera jawną prędkość bez zgadywania.
Trzy komendy urządzenia mają trzy odpowiadające usługi; otwarcie, powrót z
wyboru i ponowne wybranie niezmienionej prędkości nie wysyłają poleceń.
Odebrano siedem oryginalnych JPEG. Runtime `NEW/fan100-device-owned/report.json`
SHA `1254d0099fd3b15209f2b6940026e552a47173e55079bcd263f23ae94d6947c3`;
visual `NEW/fan100-visual-independent-review.json`
SHA `67d2e54bf4a5a8373f90599705c2c3c5b6d7d3cfcd181ea0deca515f9e01e5e4`.

Własny pełny mock został jawnie zainicjalizowany usługą z off/None/None do
off/0/None. Test wrócił do tego nowego punktu; nie twierdzić, że przywrócono
pierwotny null procentu. Mock preset-only wrócił do off/None i pozostaje w HA.
Slot6 zachowuje pełny wentylator; slot9 jest teraz launcherem **Tekst**.
Slot29 Data i czas oraz chronione4/7/30 i pozostały układ nie zmieniły się.

Zapis391→392 był pojedynczym potwierdzonym CAS. Helper promocji zachował FAIL,
bo oczekiwał globalnego snapshot_ready przy niewidzianych stronach; to błąd
warunku odbioru, nie wykazany błąd firmware. Nie ponawiać CAS. Osobny odbiór
`NEW/text-launcher100-visual-v2/report.json` (SHA
`2daee248afeb9880947a4b1d1b2aa88a0ad113283ad68333019ff0920768cf73`)
potwierdził gotowość slotu9 po wejściu na Home4, otwarcie Text, rzeczywiste
Edytuj/Anuluj i standardowe zamknięcie gestem do Home1. Root obejrzał oryginalny
obraz. Zero COMMAND/usług input_text, konfiguracja i „Stan demonstracyjny”
pozostały bez zmian. Pierwsza próba klikała poza Edytuj; nie jest jego dowodem.

Jedna trasa Ustawień: **55 FPS źródła, średnio16293 µs, maksimum21907 µs**,
failed0/IRQ0. Po trasie internal13295 B, PSRAM4849716 B; dane zależą od historii
cache. Nie deklarujemy uniwersalnego60FPS ani braku regresji pamięci. UART bez
nowych faultów; cyfrowe audio230399 ramek i wake-word potwierdzone. Start100
pozostaje **kwalifikowany**: odzyskana próba4096 B stosu miksera przy free839 B,
largest672 B przed dźwiękiem. Brak strict-clean boot, odsłuchu akustycznego
oraz testu fizycznego silnika wentylatora.

Następny etap **native101** ogranicza pamięć Text; kompilacja/odbiór sprzętowy
nie są jeszcze zamknięte. **HA123/native102 Tile event** są tylko izolowanymi
pracami: HA ma testy host265Python/34Node, native nie ma jeszcze pełnego builda
i odbioru. Zachować bramkę pamięci, brak automatycznej migracji kart i osobny
odbiór sprzętowy. Nie powtarzać ukończonego100/HA122, nie commitować/pushować.

## Historia — odebrany Text99a / HA121 przed native100

Na urządzeniu jest **native99a**, HA **0.4.0.dev121**, Core **2026.11.0**.
Odebrano ograniczony zakres edytora Text i oryginalne screenshoty. Końcowy
raport `NEW/text99a-ha121-acceptance-final.json`, SHA
`7f65125c7decc22d1ddb15a2295fdbe778bfa20bae292f16cd9af6651c268ceb`,
wiąże rzeczywisty source/ELF, instalację HA121, próby i kwalifikowany start.

**Stan przywrócony:** układ **391**, slot29 ponownie Data i czas, Home1;
`input_text.atmosfera_demo_tekst` ma pierwotne text/min0/max48 i wartość
„Stan demonstracyjny”. Nie powtarzać OTA, instalacji, Save/ABA/255 ani
sprzątania. Text był testowany tymczasowym launcherem i nie został na karuzeli.

Potwierdzono polskie znaki i usuwanie całego znaku, Anuluj, dokładnie jedną
komendę Zapisz i odpowiadającą usługę HA, blokadę niezmienionego zapisu,
unieważnienie trzymanego Zapisz po zmianie źródła tam i z powrotem, limit255
oraz odczyt całej treści w sześciowierszowym oknie. Tryb password wycofuje
sesję i czyści tekst; ponowne otwarcie pokazuje „Wartość ukryta” bez edycji.
Cztery zrzuty prywatności nie stanowią dowodu każdej klatki animacji.

Oryginalne raporty **FAIL pozostają FAIL**: wcześniejszy licznik UTF-8 naprawia
99a; brak Text w wejściu usługi naprawia HA121. Runner121 błędnie oczekiwał
CLOSE echo po wycofaniu przez HA. Kolejna próba sprzątania zmniejszyła max48
przed przywróceniem wartości255; Core zdążył zapisać konfigurację, ale odmówił
publikacji stanu. Oddzielna, chroniona sekwencja text/255 → pierwotna wartość
→ text/48 → CAS391 zakończyła się poprawnie. Nie ma już bieżącego splitu ani
niepewnego intentu. Final restore: `NEW/text121-restore-finish-first/report.json`,
SHAb65bd0357b2fba23b70108d95801817c1d5d0f6349053e5d0b6471ee8f610e89.

Jedna porównywalna trasa Ustawień: **55 FPS źródła, średnio16218 µs,
maksymalnie18464 µs**, zero failed/IRQ; wobec98:55/16223/18890.
Po tej trasie internal6871 B (**−7392 B**), PSRAM4871820 B (−36956 B).
To obserwacje zależne od historii cache/połączeń, odrębne od statycznego
RAM **+928 B** względem98 i nowych40 obiektów LVGL; stałe bufory Text4648 B
są w PSRAM. **Sprawdzić niższy zapas pamięci wewnętrznej przed dalszą alokacją
UI.** Odbiór nie oznacza braku regresji RAM, wycieków ani długiej stabilności.

Start pozostaje kwalifikowany: odzyskana próba4096 B stosu zadania miksera
przed dźwiękiem; pełne230399 ramek cyfrowego audio i wake-word. Brak odsłuchu
akustycznego i brak deklaracji strict-clean boot. Końcowe próbki audio/wake,
UART, sprzątanie oraz Home przeszły; token testowy odwołany.

Następny mały pakiet to istniejący wentylator native100/HA122: zgodność
SET_SPEED|PRESET_MODE i powrót z aktywnego presetu do jawnej prędkości bez
zgadywania aktualnego procentu. Dostawy izolowane gotowe; obowiązuje odbiór
sprzętowy po osobnym build/OTA. Dalszy panel zdarzenia kafelka jest tylko
planem, do czasu wyjaśnienia zapasu RAM. Bez Git commit/push.

## Historia po 13:20 CET — zakończona instalacją HA121

**Najnowszy stan: native99a / HA120 / Core2026.11.0 / układ389, Home1.**
OTA99a zakończoneexit0 (session79372 zamknięta), RAM bez wzrostu, flash-32B.
Boot kwalifikowany, pełne230399ramek audio i35.895s wake-word; nadal znana
odzyskana próba alokacji miksera, nie strictcleanboot. Artifact99a manifest
SHA8fbc52dc2630f64b86e8f09631675f8dee8d123dd36a8577655e5096bf8e1b3d.

Odbiór Text99a `NEW/text99a-device-first/report.json` zakończony **FAIL**,
session39354 zamknięta. Gotowość1, pisanie/Cancel/polskie znaki/backspace
działają; Save odrzucony przez HA schema. `entity_control_codec.decode_report`
nie zawierał `text` w structural extra_profiles. To nie błąd dotyku ani lease:
HA `text_fields` o12:17:06.305Z, native NOT_CONFIRMED po13.012s. Raport
`NEW/text99a-save-ingress-diagnosis.json`, SHA78ea02cb6ad36492f2b3f125acad00113c5405ce28a63326d98eb9a30d05e870.
Pierwsze dwa oryginalne JPEG w katalogu odbioru obejrzane przez root.

Po failure był zachowany niepewny intent i układ388. Root wykonał odrębny
read-only odczyt, następnie chronione uzgodnienie: stara sesja zamknięta,
wartość/config/timestamps niezmienione, jeden CAS tylko29→Datetime389.
`NEW/text99a-reconciliation-first/report.json` PASS, SHA
`6cb65cf207d055fec1adda4d2ae2d9cd2dafe5d4603c865bd46ea2c14dfbd5d7`.
Zero provider/config writes. Session44016 zamknięta; Home1. Nie ponawiać
Save ani dawnych runnerów/restore. Nie traktować reconciliation jako odbioruText.

HAagent przygotowuje **HA121 Text ingress hotfix**, source+real-ingress test,
bez ponownego build/OTA firmware. Przygotowany wcześniej fan121 staje się
przyszłym **HA122**; fan100 nadal izolowany i nieodebrany. Następny krok:
przejrzeć/zastosować HA121, jeden controlledrestart, osobny odbiór Text na
current389 z właściwym companion121 i zachowanym łańcuchem failed/reconciled.

## Historia przygotowania99a (zakończona; aktualny stan wyżej)

**Na urządzeniu native99 / HA120 / Core2026.11.0 / układ387, Home1.**
Ostatni pełny odbiór funkcjonalny pozostaje98/119 poniżej. Text99 nie został
odebrany: pierwszy test zakończył się `open-public48`, gotowość0, przed edycją
lub usługą. Uszkodzony UTF-8 w liczniku zawierał U+00AC, którego nie ma w
rzeczywistym Roboto20. Poprzedni test fontów dopuszczał każdy znak spozaASCII.
Poprawka99a zmienia tylko ten literał i test glifów;17 scenariuszy publicLVGL
PASS, stary presenter z nowym testem odtwarza błąd.

Root zastosował2 pliki; pełna kompilacja99a zakończonaexit0, session29911 zamknięta.
ELF99a `e5e932b12b9e4c6b398ea05af7e0cd6f8df1953aa751df3d6e2db6525ee02597`.
StatycznyRAM310092B bez zmiany względem99, flash8615202B (-32).
`NEW/native99a-capture-first/receipt.json`; log `NEW/native99a-capture-first.log`.
Source `W/source-v99a-build.json`, SHA
`1eb41a89a0f60ee5bc8af09023ce3e5e6d595310c1069c0669cb4d5c0ab6e654`.
Nie ponawiać `prepare99a.py`. Linked99a PASS, raport
`NEW/stack99a-text-counter-linked/report.json`,
SHA01ffd4a707813b552d7ac0a55801b0c7fff97d3e87108b257385174c0a8d7942.
PojedynczeOTA99a uruchomione w session79372, `NEW/flash99a-first.log`.
Nie otwierać COM5 równolegle ani nie ponawiać helpera. Potem odbiór Text
na aktualnym układzie387 i oryginalne screenshoty. HA120 już zainstalowane;
nie instalować ponownie. Fan100/HA121 są izolowane, jeszcze niezastosowane.

Dowody99: `NEW/text99-device-first/report.json` FAIL, restore385; następna
próba diagnostycznego screenshotu `NEW/text99-diagnostic-first/report.json`
także FAIL (niepełny odczyt sondy), restore387. Obie bez edycji wartości,
zmian konfiguracji i usług testowych; cleanup/faults puste. Brak screenshotów
z tych dwóch prób. Slot29 znów Datetime, slot9 zachowany. Nie ponawiać starych
runnerów383/385. Poprawiony odbiór musi jawnie powiązać aktualny99a z HA120
i przywróconym387, bez uznawania dwóch FAIL za odbiór.

HA120 deployment `NEW/text-ha120-deployment-first.json` PASS, jedenrestart,
zero layout/config/mockwrites. OTA99 session91161 zakończonaexit0.
Pierwszyboot99 kwalifikowany: znana odzyskana próba4096B miksera,
wolna pamięć wewnętrzna823B/największyblok672B w tym momencie; niżej niż98.
Pełne230399ramek startowych i wake-word potwierdzone cyfrowo. To nie jest
strictcleanboot ani dowód akustyczny. Nie ukrywać tej rezerwy pamięci.

## Ostatni pełny odbiór98 — historia, 6 listopada około 11:33 CET

**Odebrany wówczas stan: native98 / HA119 / Core2026.11.0 / układ383, Home1.**
Datetime ma pełny odbiór funkcjonalny97 i poprawiony styl98. Ostateczny dowód:
`C:/aeh-build/device-panels-20261104/datetime98-acceptance-final.json`,
SHA `12d8bb42862b21e49e0242a69d1676bdfd59f4d5ff6955e03b4243e7975b4c91`.
Sześć oryginalnych screenshotów98 obejrzanych; neutralny nieaktywny Save,
akcent poprawnego szkicu, neutralny błędny31listopada, Anuluj i pełneHome.
Wspólne obszary pomijane przez viewer sprawdzono w oryginalnych pikselach.
Style98: zeroCOMMAND/usług/layoutwrites, wszystkie3wartości helperów zachowane.
Standardowy gest zamknięcia przez API potwierdzony. TrasaSettings55FPS źródła,
avg16223us/max18890us, failed0, IRQwarnings0. PoSettings PSRAM4908776 B,
internal14263 B; raportowany zapas stosu6500 B. StatycznyRAM+0, flash+48 B.
Brak nowychfaultów/restartów w tej partii; audio/wake cyfrowo potwierdzone.
Pierwszyboot pozostaje **kwalifikowany**: znany odzyskany pre-chime mixer retry,
pełne230399ramek dźwięku startowego; nie jest to odsłuch akustyczny.
OTA/boot session21565 i odbiór session94409 zakończone exit0. Nie ponawiać.
Artifact98manifest SHA120aad4cd11242f58c53d92ea02c284bbbfa53d9c6ff333a56282a18b5ebc532.

**Historia przygotowania Text99 / HA120 (wdrożenie ukończone; patrz aktualizacja wyżej).**
HA120 zastosowany lokalnie: 17 plików z przypiętej nakładki, z zachowanymi
preimages; `NEW/text120-local-applied-first/receipt.json`,
SHA `1e73aa5f9720decdd15d2c6f91856f01498d0a39aade3a425ef336176d8e24c1`.
SerwerHA nadal119. Firmware99: zastosowano46plików z nativev2/UIv4/navv3,
konfiguracja i pełna kompilacjaPASS; session44701 zakończonaexit0.
ELF99 b76b1b04953a97d9d335280224de060db48f22efb3f939890a40724c63d430e8.
StatycznyRAM310092B (+928),flash8615234B (+48064 względem98).
Linked99PASS `NEW/stack99-text-linked/report.json`
SHAaabc9d22414f5d02b4bed449e24171fecf0f57714130c3d5a8900476a6090671.
Wgrywanie/odbiór pierwszego startu99 uruchomione w **session91161**;
log `NEW/flash99-first.log`. Nie ponawiać i nie otwierać COM5 równolegle.
GeneratedinputauditPASS572sources/242units; dependency11959hashesPASS.
Flashhelper zachowuje artifact99, wykonuje jedenOTA i kwalifikuje boot.
Capture `NEW/native99-capture-first/receipt.json`; log
`NEW/native99-capture-first.log`; immutable `W/source-v99-build.json`
SHA b9a4f607f10e89b0f814974e8d4a48907ae4a4919c9e8857ea894c70b4fc37fc.
Nie uruchamiać ponownie `prepare99.py` ani osobnego builda podczas tej sesji.
Własny helper `input_text.atmosfera_demo_tekst`: publiczny, min0/max48,
wartość `Stan demonstracyjny`; odczyt `NEW/text120-inventory-first.json`
SHA2da96a134244daeeabf1d0687e03d48f0a53e616b10b413d47e8af0a78b73d1d.
Zmiany definicji wymagają pełnego zachowanego obiektu `input_text/list`
i `input_text/update` z `input_text_id`; ten endpoint zastępuje konfigurację.
`prepare99.py` SHA d6949025cfa75febb17af41b30d425abf9a3c09c8e38c2be554fd2d16acb0a4e
i `panel_flash99_after98.py` SHA71678eea6df5bec1ac929509ef049bfa3e12bd0e0344bf725cfaad601e3b5b90
są przygotowane; prepare99 zakończony, flash99 aktualnie wykonywany.
Flashhelper sam uruchamia audit,
dependency verifier i preserve99; nie tworzyć tych wyników ponownie osobno.
Gotowe nakładki: native `NEW/text99-native-work/delivery-v2/manifest.json`
SHA104e2c5858680b537587ffe0edb6fc5aa0ff2b5b1bb063e10fa3e38b373456fa;
navigation `NEW/text99-navigation-work/delivery-v3/manifest.json`
SHA7b19ae9b39655e90c75b1ba3ef9202d01501539f935d1ae85709ab233646c116.
Native32scenariuszeowner i navigation22scenariusze PASS. Nowe subset API
ponownie waliduje widok oraz ograniczenie aktywnej aplikacji po admission.
Starsze nakładki zachowano jako historię; nie stosować ich zamiast finalnych.
UI `NEW/text99-ui-work/delivery-v4/manifest.json`
SHAea19f708755871341350bf2903f2d68c07a06e9983233bf57e3607e82159b886;
17publicLVGL/4schema/234fontfit/configtrue+false/codegenPASS.
UIv3 i nativev2 miały różne corpora pod tym samym testowym plikiem; pierwszy
dryrun odrzucił kolizję przed mutacją. UIv4 używa `text_ui_wire_corpus.json`;
wygenerowany nagłówek testów identyczny z udanym17-casebatchem.
`NEW/audit99_text_checks.txt` SHA1530196f697defe23ca6bb7102f0abcd63659ba5a270c0d4a4ff41cc8d7d6aea.
Flashhelper niezależnieprzejrzany (NEW/flash99-helper-independent-review.json).
Po zbudowaniu: linked99audit, singleOTA/boot99, offline freeze
`NEW/freeze99_preinstall120.py`, HA120 instalacja przez `NEW/deploy_ha120.py`,
potem skupiony Textacceptance i screenshoty. Nie twierdzić, że hardwareText przeszedł.
Nativeagent `/root/native97_audit`: `NEW/text99-native-work`;
UIagent `/root/ui97_finalize`: `NEW/text99-ui-work`;
HAagent `/root/ha97_acceptance`: `NEW/text120-ha-work`.
Kontrakt `NEW/input-text-wire-policy-draft.json`
SHAd70ed436b090f89d0b52cc79d3163e715310a1713bad87ea5a863ad4ed34ba4e;
nativeinterfaces SHA893cf49a… i UIproposal SHA5e02e04e… .
Trzy1021-bytebufory source/draft/RX w explicitPSRAM, minimumokoło4.6KB
przedLVGL; historyczny2-buffer3.6KBproposal jest nieaktualny.
Snapshot728/Message960, arena5120/output2049 pozostają limitami.
HA119 był osobnąnakładką i nie ma go w productsource98: HA120baseline bierze
kanonicznecustom_components zgodne z zainstalowanym68-filepackage119.
PierwszytestText: własnyhelper i tymczasowyownedslotCAS+restore; slot9 zachować.
Core11fullfan6 obsługuje presety również przezSET_SPEED, naszFanDomain wymaga
PRESET_MODE; osobnybugfix poText, bez cichego usuwania preset-onlydemo9.
Nie commitować/pushować, nie wyłączać komputera bez nowego polecenia.

## Historia wznowienia 6 listopada przed odbiorem98

**Najnowszy stan: native97 / HA119 / Core2026.11.0 / układ383, Home1.**
Pełny odbiór funkcjonalny Datetime PASS:3 nativeCOMMAND,8 usług (w tym5 testowych
z HA), wszystkie3 wartości przywrócone, gest zamykania potwierdzony przez API.
14 oryginalnych screenshotów sprawdzonych. Wersja97 wymaga jednej poprawki
wizualnej przed finalnym odbiorem: zablokowany Zapisz pozostaje jasnym akcentem.
Źródło ustawia DISABLED, ale paleta ignoruje ten stan. UI agent przygotowuje
izolowaną korektę98; bez zmian ownera, protokołu, geometrii ani HA.

Dowody `NEW/datetime97-functional-acceptance.json` SHA80342cbe… i
`NEW/datetime97-device-first/report.json`; pełna partia funkcjonalna jest
zakończona, nie powtarzać8 usług po poprawce samego stylu.
Trasy Ustawień:55/55/55 FPS,15964/16232/16169 us,failed0,0IRQ warnings w trasach.
PSRAM po każdej4901584 B, internal13939/13955/13931 B, stos6500 B również poSave.
Historia cache/połączeń ogranicza porównywanie absoluteRAM z dawną sesją96.
Nie było restartów/faultów w tej partii; audio/wake potwierdzone cyfrowo.
Oryginalne JPEG mają pełne nagłówki; viewer potrafi pominąć wspólne obszary.
Porównanie nagłówków overview/draft jest bajtowo identyczne po dekodowaniu.

HA119 zainstalowane: `NEW/datetime-ha119-deployment-core202611.json`, jeden
restart, bez migracji układu/konfiguracji. Instalator SHA df7db7a3… i runner
SHAee9fc538… (jedyna zmiana względem poprzednich helperów: dokładny Core pin
oraz zależny hash). Kwalifikacja actualCore: `NEW/datetime119-core202611-compatibility.json`
SHAe16da325… . Browser świeżo wczytany potwierdził podgląd Datetime na stronie
Narzędzia, zapis383, pusty inspector i brak niezapisanych zmian; zero browserwrites.

Kolejny krok:98 style-only build/OTA i krótki test existing slot29:
overview disabled neutral, poprawny szkic accent, Anuluj neutral, błędny31listopada
neutral+zeroCOMMAND, standardclose, screenshotHome i jedna porównywalna trasa.
Root zastosował dokładnie2pliki style98; capture/config/fullbuild PASS
(session43297 zakończona, `NEW/prepare98-first.log`). Source-after verified.
Source98 `W/source-v98-build.json`
SHAaeab070c0a47896d4b315f5bf0d9940a7420da2a0735023e8b0ca555abfa7545;
receipt `NEW/native98-capture-first/receipt.json`, SDK junction jużnative98.
Nie ponawiać prepare98. Delivery `NEW/datetime98-style-work/delivery-v1/manifest.json`
SHAa2cdf805…;8focusedLVGL PASS, niezależne preimage/diff sprawdzone.
`prepare98.py` SHA82a6606e… zachowuje99assertions97 i poprzednie helpery.
ELF98 SHA790486d4a1a8975f7d73ec6239c8b7058901c99d978559875fd0675afb31bfb9;
capture receipt SHAee5af300… statusBUILT_NATIVE98_NOT_FLASHED.
Narrow linked98 PASS `NEW/stack98-datetime-style-linked/report.json`
SHA0a32cddf…: wszystkie sprawdzane sizeof/ramki bez zmian, RAM309164 B (+0),
flash8567170 B (+48). `panel_flash98_after97.py` SHA8ae5d892… uruchomiony
raz (session21565, `NEW/flash98-first.log`), w chwili zapisu trwa OTA/boot.
Artifact98 manifest SHA120aad4c… zachowany. Nie ponawiać flashhelpera.
`audit98-datetime-style-linked.py` SHAc4190e24… wykonany. Nie uruchamiać osobno
verify98dependencies/preserve98: te jednorazowe kroki wykonuje flashhelper.
Runner `NEW/datetime98_style_acceptance.py` SHAf1a76ded… przygotowany i reviewed,
receiptc68dbb7b…; root `freeze98_acceptance.py` zamraża rzeczywiste wejścia dopiero
po flash98. ZeroHA/CASwrites w targeted98,3helpervalues/układ383 chronione.
Po odebraniu tej korekty wrócić do input_text. Rozpoznanie read-only:
`NEW/input-text-next-research.json` SHAc8849d27… (actualCore11),
`NEW/input-text-native-feasibility.json` SHA864a879c…,
`NEW/input-text-ui-proposal.md` SHA5e02e04e… . Żadnej implementacji Text jeszcze
nie rozpoczęto. Tryb password ukryty; pierwszy zakres bez pattern (absent/null),
UTF-8/PL-EN, jawny Save, bounded buffers poza dużą unię ControlMessage.

Poniżej historia wcześniejszych kroków tego samego wznowienia.

Użytkownik wznowił pracę. Read-only live check PASS w
`NEW/resume97-live-20261106-first/report.json` (SHAf60d7e0e…): native96,
HA118, pełny układ379 bez zmian, Home1, wake=true i trzy wartości helperów
identyczne jak poniżej. COM5/CH343 obecny; Win32_SerialPort może go nie pokazywać,
ale SerialPort.GetPortNames i Get-PnpDevice Ports potwierdzają port.

UI97 zamrożone w `NEW/datetime97-ui-work/delivery-v2/manifest.json`,
SHA4ceab9a3… (17 plików:8 fork+9 product). Finalne config true/false oraz
izolowane codegen PASS, poprzednie14 LVGL/4 schema/162 fontfit zachowane.
Additive checks `NEW/audit97_datetime_checks.txt` SHA1218e897…;
niezależny review SHA540a4831… potwierdza zachowanie78 starych +21 nowych assertions.

Root zastosował32 rozłączne pliki native/UI po exactpreimage guards.
`NEW/native97-capture-first/receipt.json`: pełna kompilacja PASS (exit0).
Source `W/source-v97-build.json` SHA
`b50baa5d3e7c3bf11ca3a8cfb1e2385d01fe1dc0832f7b9bf799fad2a36c037c`.
Config97 PASS, logSHAa6006d04… . SDK junction wskazuje już immutable97.
Nie uruchamiać ponownie prepare97. `W/compile-native97-process.json`
SHAe496b411…; ELF969917d4… . RAM309164 (+576 B), flash8567122 (+46400 B).
Linked audit PASS `NEW/stack97-datetime-linked/report.json` SHA2be54687…:
Save prefix4224 B i receive3936 B to wybrane ścieżki, nie całkowite granice stosu.
Artefakt `C:/aeh-build/native-context-v97/manifest.json` SHA61d55e54… zachowany.
Pierwsza rzeczywista OTA97 zakończona: qualified PASS w
`W/panel97-firstboot/first-boot.json`. Jedna próba, jeden reset, pełne230399
ramek dźwięku startowego i35,85 s rzeczywistego wake=true. Pozostaje znany
odzyskany retry miksera przed dźwiękiem; strict_boot_passed=false. Bez dowodu
odsłuchu akustycznego. Nie ponawiać OTA97.

HA119 jeszcze niezainstalowane. Pierwsza próba instalatora zatrzymała się
przed połączeniem SSH/zapisami/restartem na historycznym założeniu Core2026.7.1.
Faktycznie serwer ma Core2026.11.0 (`NEW/ha119-version-probe-first.json`).
Rekonsyliacja read-only w `NEW/ha119-core-source-20261106-first/report.json`
potwierdza dokładne65 plików HA118, układ379 i brak katalogu staging tej próby.
Źródła runtime input_datetime z serwera zapisane także w katalogu
`NEW/ha119-core-source-20261106-second`. Trwa kwalifikacja dokładnej wersji
instalatora dla aktualnego Core, bez zmiany pakietu ani firmware.

Pierwsze uruchomienie helpera zatrzymało się PRZED OTA (attempts0), ponieważ
wcześniejszy ręczny audyt utworzył jednorazowy plik wynikowy zależności.
Cały zapis zachowano w `NEW/flash97-preflight-output-collision`; zero uploadu
potwierdzono niezależnie. Niezmieniony helper ponownie sprawdził wszystkie
hashe, zachował artefakt i dopiero wtedy rozpoczął OTA. Log właściwej próby:
`NEW/flash97-after-preflight-collision.log`. Nie ponawiać jej automatycznie.

Runner odbioru gotowy: `NEW/datetime97_device_acceptance.py`,
SHA560a9a1c…; przygotowanie `NEW/datetime119-ha-work/acceptance97-prepared-v2.json`
SHA998c13b8… i review gestu865385c7… PASS. Ostatni panel zamyka standardowym
gestem od dolnej krawędzi. Wymaga finalnego preinstall97,
faktycznego deployment119 i geometry9be3aaf…; dotąd niewykonany. Oczekiwane4CAS
slot29,3 nativeCOMMAND+5 provider=8 usług, przywrócone wartości i Home1.

Świeży odczyt przed aktualizacją: `NEW/native96-before97-memory-20261106/report.json`:
PSRAM4923548,largest3080192,internal15255,stack watermark6452. Bez zmiany widoku.
Historia cache/pogoda ograniczają bezpośrednie porównanie z późniejszą sesją.

Poniżej zachowano checkpoint zatrzymania i szczegółowe instrukcje.

Użytkownik polecił: „Zapisz postęp i wyłącz komputer. Jutro kontynuujemy”.
Prace przerwane przed pełną kompilacją native97. Wznowić dopiero na polecenie.
Nie wykonywać commitów ani push bez osobnego żądania.

## Ostatni odebrany stan urządzenia

**native96 / HA118 / układ379**, Home1, własny tracker obecności `home`.
To ostatni odebrany stan z tego wieczoru; po uruchomieniu komputera najpierw
sprawdzić rzeczywistą dostępność i wersję urządzenia/HA, przed zapisami.
Device `192.168.88.82`, ostatni port USB `COM5`, HA `192.168.88.3:8123`.

Person/Sun i poprawka początkowego podglądu w edytorze HA118 są zakończone.
Nie powtarzać ich kompilacji, OTA, instalacji ani całej partii testów.
Łączne dowody: `NEW/info-context96-acceptance-final/report.json` oraz
`NEW/preview118-acceptance-final/report.json` (SHA367dd3ea…). Szczegóły,
screenshoty i ograniczenia: [poprzedni checkpoint](resume-2026-11-04-panels.md).
Boot96 jest qualified PASS: znany odzyskany retry miksera pozostaje osobnym
ograniczeniem, nie przedstawiać go jako naprawionego. Audio potwierdzono cyfrowo.

## Co jest gotowe, lecz jeszcze niewdrożone

Nowy dedykowany panel `input_datetime`: data, czas i oba; sekundy zachowane,
lokalny szkic, jawne Zapisz/Anuluj, klawiatura numeryczna i SVG w stylu M3.
Zapisz przyjmuje poprawne wpisane cyfry bez obowiązku dodatkowego ✓.
Semantyczna zmiana w HA unieważnia starszy szkic i przytrzymany gest, również ABA.
Brak konwersji lokalnej godziny na UTC, brak nowych pełnoekranowych buforów.

Kontrakt zatwierdzony do implementacji:
`NEW/input-datetime-wire-draft-v2/manifest.json`,
SHA `9e625084bc71fcc5deb420f205ce3efc832a5957d9a1d71f0807392e6b65d1f7`.
UIv2 `NEW/input-datetime-ui-review-v2.md`, SHA94d5033d… . Nie wracać do v1.

- Native owner/codec: `NEW/datetime97-native-work/delivery-v1/manifest.json`,
  SHA `a0d42f5014978b0cace10a338271d6e8f2b223625281d5d76145ecfaaadc5ecd`.
  15 plików:12 runtime +3 testy. Focused:87 valid/176 invalid,21 owner,
  10 negotiation; default-off56/207+10. Host Snapshot/Message bez wzrostu,
  owner +48 B; rzeczywisty P4 będzie zmierzony dopiero po kompilacji.
- UI/schema/produkt: `NEW/datetime97-ui-work`. Publiczny LVGL14 scenariuszy
  PASS w `public-lvgl-third.log`; final schema4 PASS w `schema-final.log`.
  Konfiguracja true/false PASS. `source-fit.json` sprawdza tekst i geometrię.
  63 obiekty (34 labels,22 buttons,4 SVG,3 roots),49 referencji,47 text IDs,
 16 nowych kluczy na język. Pole cyfry powiększono z34 do36 px bez zmiany
  obszaru dotyku. Checkpoint `NEW/datetime97-ui-work/checkpoint-stop-20261105.md`:
  manifest/patch oraz `audit97_datetime_checks.txt` jeszcze NIE utworzone.
  Fontfit162 PASS (SHA19892405…), konfiguracja true/false była przed ostatnią
  zmianą label34→36; publicLVGL i fontfit obejmują już finalne boxy.
  Root nie zastosował jeszcze tych plików.
- HA119: `NEW/datetime119-ha-work/delivery-v1/manifest.json`,
  SHA `25304204dec08e70cc38b9da117a008364d1ac47430e9187965693defe0e19c9`.
  Package68 `ha-package-v1/package.json`,
  SHA `0476e00c92625611c8a6b541bd1b3cfdbcaa2023580b424f15b9213d2270f8be`.
  18 focused +261 related +124 family regression PASS; JS500 full +1 nowy
  focused test8 actual backend fixtures. Wzajemne source review HA/native PASS.
  Root ZASTOSOWAŁ lokalnie18 plików po exactpreimage guards:
  `NEW/datetime119-local-applied-first/receipt.json`, SHAafdcf193… .
  **Kanoniczny kod HA ma119, działający HA nadal118. Nie aplikować drugi raz.**
  Edytor JS119 jest już w tej dostawie; nie aplikować osobno root JSv2.

## Przygotowane narzędzia — jeszcze nie wykonywać bez sprawdzenia wejść

- `NEW/prepare97.py`, SHAa0ce05b1…: nakłada rozłączne runtime overlays na
  dokładny immutable96, zapisuje preimages i source-v97, zmienia tylko build
  junction96→97, waliduje config i buduje. Wymaga `--overlay PATH SHA`
  dla native/UI oraz `--checks PATH SHA` od agenta UI. Każdy preimage musi
  pasować równocześnie do kanonicznego pliku i source96; dokumentację zmienioną
  od96 stosować oddzielnie, nie rozluźniać guards. HA119 wdrażane osobno.
- `NEW/panel_flash97_after96.py`,
  SHA `dbf294d76892c65610be9d5c0a3cd9c68756d2dc6167fda733a848f18ba87b77`.
  Jedna OTA z96/379, chronione source/ELF/linked audit i pełny UART/audio/wake.
  Niezależny review `panel_flash97_after96-independent-review.json` SHAd69a3d4a… .
  Finalna derivacja jest v2; wcześniejszy b441… miał tylko dwie literówki tekstu.
  Ten helper sam zachowuje artifact97 przed OTA; nie tworzyć katalogu
  `native-context-v97` wcześniej, bo celowo odrzuca istniejący artefakt/próbę.
- `NEW/audit97-datetime-linked.py`, SHA1904a6ac…: przygotowany ekstraktor,
  **nieuruchomiony**. Agent native czeka na faktyczne source/ELF97. Należy
  przejrzeć stos ścieżki Save→emit→serialize oraz receive/parse i P4 type sizes.
  Końcowy raport: `PASS_PATH_SCOPED_LINKED97_DATETIME_AUDIT`.
- `NEW/deploy_ha119.py`,
  SHA `a1949e606c5e9ef4c59a296c55bc8e63a8316384b7a25a207e89c8ad1c295c14`.
  Offline package/preimages PASS, root source review `deploy119-root-review.json`.
  Wymaga faktycznego preinstall97 manifestu. Wzór/schema w
  `NEW/datetime119-ha-work/installer119-prepared.json`. Oddziela bieżący379
  od `boot_layout_revision`; jeden restart, zero config/layout/fixture writes.
- Runner odbioru sprzętowego97 jeszcze NIE utworzony. Agent zapisał scenariusze,
  geometrię i pułapki API w
  `NEW/datetime119-ha-work/acceptance97-paused-checkpoint.md`.
  Actual native31→HA crosscheck PASS w `native97-wire-crosscheck.json`,
  SHA4ff9ba04… . Dokończyć i przejrzeć helper przed wykonaniem.

Potwierdzone podczas zatrzymania: nie istnieją `C:/aeh-build/native97-sources`,
`W/source-v97-build.json` ani receipt instalacji119. SDK junction nadal wskazuje
`C:/aeh-build/native96-sources/fork/esphome/components`. Nie było build/flash97.
Nie działał żaden kompilator, Ninja ani proces testowy. Pozostawione niezależne
Python PID20844 (proxy) i21960 (SMTP) nie są procesami tego etapu.

## Własne mocki w HA — już utworzone, nie tworzyć ponownie

Inventory `NEW/datetime97-inventory-first.json` SHA3843c9af… zapisuje cały379.
Receipt `NEW/datetime97-helper-creation-first.json` SHA78b6191e… potwierdza dwa
nowe storage helpers, bez zmiany layoutu ani istniejącego helpera:

- `input_datetime.atmosfera_demo_data_i_czas`: istniejący,2026-11-04 00:00:00.
- `input_datetime.atmosfera_demo_data`: nowy,date-only,2028-02-29.
- `input_datetime.atmosfera_demo_czas`: nowy,time-only,23:58:37.

Nie uruchamiać ponownie `datetime97_create_helpers.py`. Sprawdzić stan i registry
po restarcie HA. Slot29 nadal ukrytym redundantnym wentylatorem; żadne przypisanie
datetime nie zostało zapisane. Plan: świeży CAS tylko29→combined, tymczasowe
date/time warianty i końcowy combined. Zachować pozostałe karty, szczególnie4/7/30.

## Następny krok po wznowieniu

1. Sprawdzić dostępność i wersje HA/device, brak niezależnej zmiany layoutu379.
2. Odebrać finalny UI overlay/audit checks i przejrzeć rozłączne dostawy.
3. Jedna pełna kompilacja97, rzeczywisty linked/resource audit, jedna OTA
   z zapisem UART i dowodem audio/wake; później instalacja HA119.
4. Odbiór trzech własnych helperów przez publiczne dotyki i HA services:
   Cancel bez komendy; bezpośredni Save dokładnie1 komenda/usługa; błędny dzień/
   rok przestępny; zachowanie sekund; external ABA przy trzymanym Save.
   Przywrócić własne wartości tylko po sprawdzeniu, że nie zmienił ich ktoś inny.
5. Oryginalne screenshoty, porównanie HA, Home i jedna partia3 tras Ustawień
   względem96:55 FPS, avg16166 µs. Pilnować pamięci/DSI/audio; nie deklarować
   60 FPS wszystkich widoków ani fizycznego odsłuchu na podstawie telemetrii.
6. Uaktualnić roadmapę po faktycznym odbiorze, następnie kolejne dedykowane panele.
   Nie zmieniać mechanizmów Player/Kamera/Galeria/Asystent. Bez Git push/commit.

Ścieżki: `NEW=C:/aeh-build/device-panels-20261104`,
`W=C:/aeh-build/notification-cards-20261102`,
Python `C:/aeh-build/upstream-sync-20261022/.venv/Scripts/python.exe`.
Kanoniczne repo: `C:/Users/kyvai/atmosfera-echo-hub` i
`C:/Users/kyvai/kyvaith-esphome`. Oba na `feature/ha-dashboard-2026-10-24`,
HEAD odpowiednio `5de0e0789ab8b9cc76adc2de5195e622370e51d9` i
`62745ae0c43a233760ddaf1fed60867736832547`; dużo wcześniejszych zmian lokalnych.
Nie resetować, nie sprzątać katalogów ani nie odczytywać wielogigabajtowej historii.
