# Wznowienie paneli — aktualizacja 5 listopada2026

**Zatrzymanie na polecenie użytkownika wieczorem5 listopada:** zacząć od
[najnowszego checkpointu datetime](resume-2026-11-05-datetime.md).
Native97/HA119 przygotowane, bez buildu/OTA97/instalacji119. Kanoniczny kod HA119
zastosowany lokalnie, działający HA118. Poniższy zapis zachowuje wcześniejsze dowody.

## Bieżący stan: native96 / HA118 / układ379

Person/Sun przeszły odbiór firmware, źródłaHA i12 oryginalnych screenshotów.
Łączny raport: `NEW/info-context96-acceptance-final/report.json`,
SHA07d8ada8… . Poprawka wyłącznie edytora HA118 została zainstalowana i odebrana.
Nowe karty spoza pierwszych200 encji biblioteki pobierają metadane bez klikania.
Po cold reload → Narzędzia: „Obecność w domu” i „Słońce poniżej horyzontu”,
inspector pusty, Zapisz disabled, układ379. Testy JS490/490 (10 nowych).
Deployment `NEW/preview-ha118-deployment-first.json` SHA7936a56e…,
jeden restart, zero config/layout/fixture writes. Pakiet65 SHA39ce03f7…;
delivery4 SHA9443d172…; lokalny apply08ba42fe…; preinstall30bb88c0…
w `NEW/native96-preinstall-ha118-first/manifest.json` oddziela historyczny boot376
od live379. Nie ponawiać instalacji ani flashowania96.
`NEW/preview118-device-smoke-first/report.json` SHAa93dd739… zawiera dwa
oryginalne screenshoty Home5/Home1, obejrzane poprawnie; wake=true, TX661423.
PSRAM4022528/internal16571 w tej krótkiej obserwacji ma inną historię cache
i pogodę niż wcześniejszy benchmark, nie jest równoważnym porównaniem.
Łączny successor: `NEW/preview118-acceptance-final/report.json`.

Dwa nowe launchery: slot18 Osoba,slot23 Słońce. Pozostałe karty/kolejność stron
zachowane. Odbiór obejmował własny tracker home→not_home→home (dokładnie2MQTT
publikacje), rzeczywiste `sun.sun`, readonly Calendar/Lock, Home5/Home1 i3
porównywalne przewijania Ustawień. Końcowy stan mocka home, wszystkie sesje API/
UART zakończone, chwilowe tokeny cofnięte. Nie wykonywano komend urządzeń z paneli
informacyjnych. Żadnych commitów ani push.

Runtime report `NEW/info-context96-device-fourth/report.json`, SHA f5e5e1aa…;
visual `NEW/visual96-context-review/review.json`, SHA042889b0… . Domniemane braki
statycznych nagłówków w kolejnych podglądach obrazów były artefaktem narzędzia:
identyczneJPEG i losslessROI/pixel equality potwierdziły pełne piksele. Nie
zmieniano z tego powodu firmware.3×55FPS, avg16191/16183/16124us (średnia16166,
+0,62% wobec95), failed0, IRQ0 w tej krótkiej serii. Historyczne ograniczenia
DSI nadal obowiązują; nie deklarować uniwersalnych60FPS.

PSRAM po2/3próbie stabilne4807948B, internal około20143B, minimalny wolny stos6452B.
`NEW/info-context96-memory-read/report.json` pokazuje raw/app_work/scroll/close/
lowres=0 po powrocieHome; snapshot7041KiB=5625tiles+1416JPEG. Późniejsze heap95/96
nie są identycznym obciążeniem (m.in.Asystent). Poprawne przybliżone porównanie
boot: `NEW/native96-boot-memory-comparison-corrected-v2.json`, SHAeecc8acc…;
poI2S −11792BPSRAM/−192Binternal. Boot95 miał układ365,96 miał376 (jedyna różnica
kart to slot15.action); nie powtarzać błędnego założenia identycznego376 z raportuv1.

Jedna pełna kompilacja96 i jedna OTA zakończone PASS. Source
`W/source-v96-build.json` SHAa3ad20dc…; artifact
`C:/aeh-build/native-context-v96/manifest.json` SHAd1933574…; ELF
`d31a29618986ca4f8cf3ee6dc74118020017ec52e32e177872deaee3061a4dd8`.
RAM308588B (+200),flash8520722B (+23232). Linked scoped audit
`NEW/stack96-info-context-linked/report.json` SHA56455882… . Snapshot/Message/
owner P4 bez wzrostu. Capture `NEW/native96-capture-first/receipt.json` i
`NEW/prepare96.py` SHA254d00da… zachowane. Aktualny SDKjunction wskazuje
`C:/aeh-build/native96-sources/fork/esphome/components`.

Boot `W/panel96-firstboot/first-boot.json` SHAdf046b01…: qualifiedPASS, pełne230399
klatek audio i36s wake, zdrowy zamkniętyUART. Strict=false: znany odzyskany retry
miksera przed sygnałem nie jest naprawiony tym pakietem. Audio potwierdzone cyfrowo,
nie akustycznie. Preinstall96 `NEW/native96-preinstall-first/manifest.json`
SHA1edbca24… . HA117 zainstalowane po jednym restarcie, bez zmian konfiguracji:
`NEW/context-ha117-deployment-first.json` SHA221066c9… .

Piny dostaw: product11 c4213b0b…,native18 4d5a3c1a…,HA19 2ab75dae…;
HA11765-filepackage768631dd… w `NEW/info116-ha-work/ha-package-v1` (nazwa116
historyczna). HA jest osobnym pakietem: immutable firmware96 zawiera historyczne
HA115, których nie należy porównywać do instalowanej65-fileHA117.
Audit96 font-only successor `W/audit_native96_inputs_font_fix.py` SHA62792ed2…,
derivation8ccce442… zastępuje błędne oczekiwanie fontref oryginalnegoaudit96;
nie zmienia firmware. Do kolejnego capture użyć poprawionegoauditu jako template.

Historia harnessów zachowana: first0writes — projekcja4pól discovery nie zawierała
`default_entity_id`; second otworzył Person, potem read() bez offset, przywrócił
układ378 i nie publikowałMQTT; third0writes — zastano idleAsystent zamiastHome.
Root odczytał stabilnyTX/wake i zwyczajnie zamknął idleview doHome
(`NEW/info-context96-preflight-home/report.json`). Fourth wykonał pełny odbiór
na niezmienionym v3helperze SHAda47c106… i manifestca19f26b…; jedenCAS378→379.
Nie powtarzać OTA, instalacji117 ani zakończonej partii sprzętowej bez nowego powodu.

Następne: wdrożyć dedykowany input_datetime (data/czas/
oba, zachowane sekundy, lokalny draft, jawne Zapisz/Anuluj, jeden absolutnyrequest).
Propozycja `NEW/input-datetime-after96-proposal-v1.json` SHA738ec9d4… i UX
`NEW/input-datetime-ui-review-v1.md` SHA28a16c7d… . Native review potwierdził możliwy
optional datetime:1 bit64 i typedCOMMAND w istniejącej unii (bezpotwierdzonego
jeszcze sizeof97). Kontrakt v2 jest już zamrożony, implementacja trwa w izolacji.
Nie ruszać mechanizmów Player/Kamera/Galeria/Asystent.

### W toku — datetime97 / HA119, jeszcze niewdrożone

Kontrakt `NEW/input-datetime-wire-draft-v2/manifest.json` SHA9e625084…,
HA review fb16b9d2…, UIv2 94d5033d… . Trzy tryby, sześć nullable integer pól,
zero UTC/epoch/fold konwersji, Gregorian bez clamp. Zapisz z otwartą klawiaturą
przyjmuje poprawne cyfry i cały szkic atomowo; dodatkowe✓ jest opcjonalne.
Zmiana pola przyjmuje poprawny wpis lokalnie, błędny pozostaje widoczny.
Metadata tego samego pokolenia zachowuje szkic; wyższa semantic generation/ABA
anuluje szkic i przytrzymany gest. Potwierdzenie zapisu wymaga nowszej obserwacji
całego targetu. Root zatwierdził implementację, nie trzeba pytać ponownie.

Izolacje: native agent `NEW/datetime97-native-work` (owner/types/codec/
protocol/gates/extra_component handshake); UI agent `NEW/datetime97-ui-work`
(component.h/.cpp, datetime_component.cpp, entity_control.py, produkt/i18n/SVG);
HA agent `NEW/datetime119-ha-work` (backend, meta, package). Root zastosował
lokalnie18 plikówHA119 po exactpreimage guards; receipt
`NEW/datetime119-local-applied-first/receipt.json` SHAafdcf193… . Live nadalHA118.
Pozostałe implementacje jeszcze w izolacji, bez buildu/OTA97/instalacji119.

Root: izolowany JS119 `NEW/datetime119-editor-work/delivery-v2/manifest.json`
SHAa5e419f2… (v1edeb7b58… zachowany). Full500PASS obejmuje10 nowych testów;
potem dodatkowy1 focused test8 actual backend fixtures d41331e5… PASS.
Runtime JS nie zmienił się po pełnym500, doszedł tylko test actualfixture.
AgentHA zakończył independent review PASS i dołączył oba pliki do paczki119.
HA119 delivery18 `NEW/datetime119-ha-work/delivery-v1/manifest.json`
SHA25304204…; package68 `ha-package-v1/package.json` SHA0476e00c…;
18 focused +261 related +124 family regression PASS. Wzajemne source review
native/HA PASS. Native97 delivery15 `NEW/datetime97-native-work/delivery-v1/manifest.json`
SHAa0d42f50…: 12 runtime +3 tests; 87 valid/176 invalid,21 owner,10 negotiation;
default-off56/207+10. Host Snapshot/Message bez wzrostu, owner+48B;
to jeszcze nie pomiar P4. UI publicLVGL w toku.
Root przygotował `NEW/prepare97.py` SHAa0ce05b1… i niewykonany
`NEW/panel_flash97_after96.py` SHAdbf294d7…; nie ma jeszcze capture/build97.

Read-only inventory `NEW/datetime97-inventory-first.json` SHA3843c9af…:
istniejący storage helper `input_datetime.atmosfera_demo_data_i_czas`,
wartość2026-11-04 00:00:00; brak exact references w wskazanym zakresieYAML.
Public Core API utworzyło potem dokładnie dwa własne mocki:
`input_datetime.atmosfera_demo_data` data2028-02-29 i
`input_datetime.atmosfera_demo_czas` czas23:58:37.
Receipt `NEW/datetime97-helper-creation-first.json` SHA78b6191e…:
2creates/0updates/0deletes/0services/0layoutwrites; istniejący helper i379
niezmienione, ephemeral token revoked. Nie tworzyć ich ponownie.
Slot29 nadal ukryty fan/oscylacja. Zmienić dopiero po nowym firmware/HA,
z fresh compare-and-save i zachowaniem pozostałych kart4/7/30.

Build97 nieprzygotowany. Użyć corrected audit96 fontfix; historyczne
capacity==1024 zastąpić dokładnym generated count i budżetem<=1056.
Obecny SDK junction nadal native96; żadnej kompilacji ani przełączenia97.

NEW=`C:/aeh-build/device-panels-20261104`; W=`C:/aeh-build/notification-cards-20261102`.
Poniżej zachowana chronologiczna historia poprzednich etapów; powyższy stan ma
pierwszeństwo.

## Praca w toku — Action95 / HA115, 5 listopada

**Bieżący runtime: native95 / HA116 / układ376.** HA116 to zakończona poprawka
podpisu launchera. Jedna instalacja/restart HA, bez zapisu konfiguracji/układu
i bez ponownej OTA. Oryginał `NEW/caption116-device-first/home-caption-original.jpg`
pokazuje czytelne „Otwórz”; rzeczywisty podgląd HA po reloadzie pokazuje to samo.
Testy5Python/3JS przeszły również z kanonicznych plików. Receipt
`NEW/caption-ha116-deployment-first.json` ma PASS, review
`NEW/caption116-device-first/visual-review.json` potwierdza oba widoki.
Kanoniczne6 plików HA116 zastosowano z kopiami poprzednich wersji; nic naGitHub.

Recovery i uzupełnienie95
zakończone: mock switch ON, automatyzacja/skrypty OFF/current0; oryginalny układ
przywrócono jako375. Następnie jeden CAS zmienił wyłącznie slot15.action na
dedykowany panel akcji, urządzenie potwierdziło376. Odbiór paneli obejmuje11
przyjętych poleceń, rzeczywiście dostarczone powiadomienie,19 przejrzanych
oryginalnych screenshotów i3 pomiary55FPS/15984,16041,16176us, failed0.
Nasłuch działał, zamknięty UART bez awarii; brak IRQ w tej krótkiej próbie nie
usuwa wcześniejszego ograniczenia DSI. Pierwotny FAIL narzędzia pozostaje jawny.

**Zamknięty błąd podpisu Home:** dodatkowy końcowy screenshot376
`NEW/action95-final-home/home-action-launcher-original.jpg` ujawnił ucięty
surowy timestamp pod Powiadomieniem. Podgląd HA formatuje go inaczej. Trwa
przygotowanie małej poprawki HA116 (bez zmiany/flashowania native95).
Późniejsza instalacja i odbiór opisane na początku zamykają tę rozbieżność.

Dowody: `NEW/action95-combined-runtime/report.json` SHA4625fcc5…,
`NEW/visual95-action-combined-review/review.json` SHAdbe23226…,
`NEW/action95-recovery-first/receipt.json` SHA9dad1f31…,
`NEW/action95-completion-first/report.json` SHAf5e90773…,
`NEW/action95-migration-second/receipt.json` SHAec30c6fd… . Pierwsza próba
migracji zatrzymała się przed zapisem (0save/0validate), bo snapshot slot15 był
leniwy poza bieżącą stroną. Zwykłe przejście naHome4 przygotowało slot;
druga próba wykonała jedyny zapis375→376. Bez powtórzenia Press/Trigger.
Przegląd rzeczywistego edytora HA115 Action/Media zakończony bez edycji/zapisu.

**Następny pakiet w izolacji:** Person/Sun, native96/HA117; jawny opcjonalny
`info_context:1` obok zachowanego Info1, read-only, wspólny owner/bufory.
Projekt `NEW/person-sun-info-design-v1.md`; runtime inventory
`NEW/info-context-live-inventory-v1.json` SHA28a41b2d… . Rzeczywiste sun.sun
nie ma registry (walidować przez runtime state/source); istnieją demonstracyjne
person.atmosfera_demo_osoba i device_tracker.atmosfera_demo_presence.
Przed sterowaniem mock trackerem potwierdzić lokalną deklarację/creationproof.
Nie zmieniono jeszcze kanonicznych źródeł tego pakietu ani urządzenia.

Poniższe akapity zachowują wcześniejszy przebieg. Jedna OTA95
i kwalifikowany pierwszy start zakończone PASS (sesja29028 zamknięta).
Artefakt95 SHA bcca9431e2d4784e2814cdc6d350aa4dfe0fb409fc960e1acc1f92542e073c40;
pełne230399 klatek audio, ponad35s detekcji, zdrowy zamknięty UART. Strict=false:
ten sam znany odzyskany retry4096B przed sygnałem (free2495/largest2432).
Preinstall `NEW/native95-preinstall-first/manifest.json` SHA
01316696b7150006663c9388f406cd00a3d1ccd9ceee6da6fe4344ca087d3ffd wiąże
oryginalny boot, nie dodatkowy wrapperPASS.

HA115 zainstalowane po jednym restarcie, `NEW/action-ha115-deployment-first.json`
PASS; sesja43951 zamknięta.64runtime, zero zmian konfiguracji/układu i brak nowych
fixtures. Helper `NEW/deploy_ha115.py` SHAe4d15c2e3f5603aa1832ab26ad2cc462e062b5bdad92a54fe0adb17f58f470ad.

**Partia sprzętowa Action95 zakończyła się błędem narzędzia — sesja79118 zamknięta.**
Wszystkie kontrole przed powiadomieniem przeszły, w tym Trigger z wynikiem7
oraz obie polityki wyłączenia automatyzacji. Press powiadomienia i wywołanie
notify zaobserwowano; oryginalny `final-home` pokazuje dostarczony toast.
Narzędzie pominęło wymagane `phase` w void `debug_snapshot_app_state` (linia417),
więc zatrzymało się lokalnie przed wysłaniem tej diagnostyki. Nie powtarzać Press.
Pierwotny report zachowuje FAIL. Układ374 nadal ma tymczasowy panel wslot15,
mock switch jest OFF zamiast początkowego ON; automatyzacja OFF/current0.
Trwa przygotowanie minimalnego recovery i uzupełnienia trzech pomiarów Settings.
Nie wykonywać nowej kompilacji/OTA ani ponawiać całej partii z tego powodu.
Helper `NEW/action115_device_acceptance.py`
SHA109028a3af1979990ff58c034f7c68418e19a6f3e158c21e71faa1ab712838a1,
manifest `NEW/action95-acceptance-frozen/manifest.json` SHA
860abd3ec025ffc47b331d10c52106354a13b894c0ab20288e2ec6b3750391cd.
Log `NEW/action95-device-first.log`, wyniki i screenshoty `NEW/action95-device-first/`.
14 oryginalnych screenshotów przeszło częściowe review bez wizualnego blokera;
to nie oznacza pełnego PASS ani przywrócenia układu. Następnie uzupełnienie
pomiaru, osobna migracja tylko slot15 oraz rzeczywista przeglądarka HA.
Pierwotne FAIL94/95, recovery i ograniczenia DSI pozostają jawne.

Poniżej przebieg przygotowania95 oraz wcześniejszych prób.

Najświeższa czynność: root zastosował30 rozłącznych zmian95/HA115 po review
runtime i preimages; pełny config/build w sesji18984 zakończony exit0. Helper
`NEW/prepare95.py` SHAa6e8b167c80f6c10a1e54b1ee22c564d95045f9cfae2758e008aa43d99308c97,
log `NEW/prepare95-first.log`, receipt `NEW/native95-capture-first/receipt.json`.
Source95 `W/source-v95-build.json` SHA
b4089dd6b0332a4fab544ecf03419a5e1d7916cbcaa5c3481b0419c71fb34897.
ELF95 d500e5b3717d0762f2d86a1cd8019d51cf8406ad80c4830b7284c2b45e2153b9.
DIRAM308388B bez zmiany, flash8497490B (+544 wobec94). Capture receipt
SHA c8a99308e8d19824c5eef5808900da541c1ed73e9a02fb6f2cacf2aa7b1652c5.
Scoped linked review95 PASS: `NEW/stack95-action-linked/report.json`,
SHA80761622600b9f242892b8e2c8f9f69e62fd01cee663f311c504b971f5128a03.
Prefiksy3968/4240B bez zmiany; osobna gałąź wyniku +32B, brak pełnego bound.
Trwa jedna OTA95 w sesji29028 (`NEW/flash95-first.log`). Nie uruchamiać
równoległego UART/API ani powtórnej OTA. Kanoniczne źródła są95/115; HA nadal114,
układ365. Sprawdzić wynik `W/panel95-firstboot/first-boot.json` przed dalszymi
operacjami. Nie rozpoczynać drugiej kompilacji. Odbiór95, HA115,
screenshoty i pomiar pozostają do wykonania. Nic nie commitowano/wypchnięto.

Recovery wykonane: `NEW/action94-recovery-second/receipt.json`,
SHA6ad75598f88e6aa493ab2702755fdc37b4ea6da4b41c38977928515a2d27de1e.
Aktualny układ365 przywraca oryginalny slot15; mock automatyzacji OFF/current0,
mock switch ponownie ON. Zero powtórzeń Trigger, jeden CAS układu. Screenshot
`NEW/action94-recovery-second/recovered-home-original.jpg` obejrzany; audio i
nasłuch nadal gotowe. Pierwszy recovery zatrzymał się przed jakimkolwiek zapisem,
bo po200ms nie dotarł cały wieloliniowy raport diagnostyczny. V2 czeka na
kompletny raport do3s zamiast osłabiać warunek wycofania właściciela.

95/HA115 są już zastosowane lokalnie i skompilowane, ale nie wgrane. Action:2 dodaje terminal
service_dispatched7 tylko dla Trigger, przy niezmienionych payloadach
action_version1. Native95 ma zachować obsługę HA114/Action1; HA115 wymaga
Action2 i nie wysyła7 do native94. Produkt95 zawiera też tekst gotowości,
nazwę „Przycisk” i wyśrodkowanie podpisów bez zmiany hitboxów. Nie mylić
izolowanych delivery z firmware rzeczywiście działającym na urządzeniu.

HA114 jest zainstalowane po jednym restarcie. Pierwotny postcheck instalatora
zachował FAIL (`KeyError: panel_extra_profiles`); późniejszy odczyt bez ponownej
instalacji potwierdził pakiet, profile i mocki:
`NEW/action-ha114-deployment-reconciled-first.json`, SHAb7729a3b… .
Nie ponawiać instalacji114. Runtime114 ma stary URL assetu113; poprawka wersji
URL jest zaplanowana razem z poprawką HA115, nie jako osobny restart.

Partia Action94 zakończyła się FAIL (sesja71807 zamknięta), dowody:
`NEW/action94-device-first/report.json` i zamknięty zdrowy UART. Przycisk,
scena, natychmiastowy skrypt, blokada wymaganych parametrów, Run/Stop skryptu,
Enable i Trigger z niespełnionym warunkiem przeszły. Trigger z pominięciem
warunku uruchomił30s automatyzację, lecz wspólne blocking=True czekało na cały
bieg; po5s HA wysłało not_confirmed/service_timeout. To rzeczywisty błąd
semantyki, nie powód zwiększania limitu testu. Przygotowywana poprawka:
wyłącznie Action/automation.trigger użyje nieblokującego przyjęcia przez HA
i osobnego, uczciwego terminalnego wyniku service_dispatched; pozostałe
operacje zachowują dotychczasowy kontrakt.

Cleanup zachował nierozstrzygnięty intent: ostatni zapisany układ364 nadal
ma tymczasową automatyzację wslot15, mock switch pozostawiony OFF zamiast
początkowego ON. Potrzebny świeży odczyt i jeden kontrolowany restore; nie
powtarzać triggera ani całej partii bez rozwiązania tego stanu. Realne4/7 i
dzwonek30 nie były sterowane. Nie wykonano jeszcze pomiaru Settings94 ani
stałej migracji15. Dziesięć screenshotów ma częściowy przegląd; poprawki
etykiety gotowości, nazwy przycisku i pionowego centrowania podpisów są w
przygotowaniu. Nie oznaczać94 jako odebranego.

DSI:138 linii to69 par bieżącej/retained diagnostyki, nie138 zdarzeń.
Licznik invalid/recovery wzrósł6→12; brak liniiIRQ nie oznacza czystej
transmisji. Nie powiązano tych zdarzeń z błędem potwierdzenia HA.

Poniżej zachowano przebieg kompilacji i instalacji94.

Stan przed instalacją114: native94 / HA113 / układ357 (sesja17873 zakończona).
Nowy pakiet został zastosowany lokalnie:
23 pliki forka, 13 produktu i 47 integracji/testów HA. Receipt:
`NEW/action94-applied-first/receipt.json` ma status
`APPLIED_ACTION94_SOURCE_ONLY_NOT_BUILT_OR_DEPLOYED`.
Finalny manifest native to `NEW/action114-native-work/native-delivery-v2/manifest.json`,
SHA e881f2aaabf822618c31992c9f6db0f5e58c299e4783a68975a368037cacd493.
Nie wracać do wcześniejszych overlayów v1. Naprawiono wyłącznie niezamierzone
kodowanie komentarzy IDE; pozostałe 22 postobrazy i wyniki testów pozostają te same.

Capture94, config i pełny build przeszły; sesja56226 zakończona exit0. Source:
`W/source-v94-build.json`, SHA
1363dea59ad963d6726d789f746d7393c3898b9acc24b5117064d3729cc2e515.
ELF a8492bc2720f4a7e89af35277a837f266e9e579fc0a7146286485a097de35cf3;
DIRAM308388B (+264), flash8496946B (+32544). Capture receipt97b514d0… .
Ekstrakcja linked94 zakończona exit0 w sesji50901. Przegląd zakończony PASS;
`NEW/stack94-action-linked/report.json` SHAc90891e6… . Prefiks Action4240B,
odbiór3968B; brak uniwersalnego bound stosu.
Junction SDK wskazuje native94. Nie uruchamiać drugiej kompilacji.
Jedna OTA i kwalifikowany boot przeszły; sesja7212 zakończona exit0. Artefakt94
SHA0a2ebd123fe26e94c2b79a463d428f5ff9c3089f5bedf179b12523b609478c42.
Oryginalny boot `W/panel94-firstboot/first-boot.json` SHAb8886dc4… :
230399/230399 klatek, nasłuch35,931s, zdrowy zamknięty UART. Strict=false:
znany odzyskany retry4096B (free2523/largest2304) przed sygnałem startowym.
Nie powtarzać OTA. Następnie staged HA114 z dwoma dodatkowymi plikami fixture i jednym
restartem. Helper instalacji `NEW/deploy_ha114_staged_v4.py` ma SHA
8762156f0a7a05da2a881711776365a2c4a054809efddecef9fa49bd82b128a0.
Uruchomiony raz w sesji17873; log `NEW/deploy-ha114-first.log`. Preinstall manifest
`NEW/native94-preinstall-first/manifest.json` SHA46c0eb30… wiąże rzeczywisty boot,
source i artefakt; zachowuje qualified/strict=false. Nie ponawiać instalacji/restartu
bez odczytania końcowego receiptu `NEW/action-ha114-deployment-first.json`.
Pierwsza migracja tylko slot15, slot30/dzwonek pozostaje bez zmian. Odbiór Action,
screenshoty, wspólny pomiar i rzeczywista przeglądarka HA pozostają do wykonania.
Bez commit/push i bez wyłączenia komputera.

## Najnowszy stan — native93b / HA113 / układ357, Media odebrane w opisanym zakresie

Obowiązuje `NEW/accepted93b-checkpoint-v2.json`, SHA
c2127a2b44992f66af2bb63d7d343787a8b9aa0081e21ab5ab713973b15068de.
Media4 grupy/21 screenshotów, Light/Climate2 screenshoty i3 Home przeszły.
Settings55/55/55FPS, średnio15,989/16,105/16,283ms, failed0; baseline54/54/54.
To krótki pomiar źródła z1 segmentem snapshotu zamiast2, bez deklaracji stałych60FPS.
Ostrzeżenia DSI pozostają:3 IRQ underrun w poprzedniej serii,4 w obecnej.
`NEW/performance93b-dsi-comparison.json` rozdziela je od failed0 renderera;
nie deklarować bezbłędnej transmisji obrazu ani przypisywać małej różnicy poprawce.
Pamięć próbek2–3: PSRAM4906932B, internal25167–25219B, bez monotonicznej utraty.
Większy zapas RAM niż92c nie jest dowodem optymalizacji: inne rozgrzanie audio/cache.
Wszystkie poniższe sesje zakończone. Teraz przygotowanie Action94/HA114 w izolacji.

Native93b jest wgrany. Jedyna zmiana runtime wobec93a to lokalne wyrównanie
niewidocznego recolor przycisku Volume Back w stanach enabled/disabled.
Publiczny test LVGL odtworzył9 opóźnionych flushes w każdym kierunku w93a;
poprawka daje0/0, również dla niestandardowego koloru. Strażnik Scalar i DSI
pozostają bez zmian. Manifest3 plików:
`NEW/media-back93b-adjunct/manifest.json`, SHA
74461872481074bc099508a694de770a79237257f1cba7177b94c485938087be.

Capture/config/build zakończone raz, sesja48594 exit0. Source93b SHA
b6d02431e661d5dfc530779b56b6d0bf06a8016793201355d58c5d64ae0e9692;
ELFbe55567c7227baa4d4ef5211f206cd99639d6cdc3bcff699db1eac3447a4ed21.
RAM308124B bez zmiany, flash8464402B(+80). Scoped linked review
`NEW/stack93b-volume-base-linked/report.json` SHA
3547d2c79a970d90ca7a63d940f3502af6304d84650bc621411ee84539bef1bb:
setup frame80B bez zmiany; nie jest to uniwersalny bound stosu.

Jedna OTA i kwalifikowany pierwszy start zakończone w sesji89104 exit0.
`W/panel93b-firstboot/first-boot.json` SHA
89090bd53c8c69d5f9ce20034ac64effb78a607aadbd92272cf9e9e298872d29.
Pełne230399 klatek, nasłuch35,886s, zamknięty zdrowy UART. Strict=false:
ten sam znany odzyskany retry4096B przed sygnałem startowym, bez nowej awarii.
Artefakt93b SHA
cc922e9fba7b9ab214d79f985f7510e811ffb4d9ce53e2b53a229314e44ca7e3.

Partia Media harnessv5 zakończona PASS w sesji9114 exit0. Log
`NEW/media93b-device-first.log`; wynik `NEW/media93b-device-first/report.json`
SHA6c24414c15c8f8cfa3561ddd5092acf0db5b094f5210836a111ae1b0ed9b4c4d.
Wszystkie4 grupy, brak cleanup failures, zdrowy UART bez awarii. Wszystkie21
oryginalnych screenshotów przeszły review `NEW/visual93b-media-review/review.json`
SHA9535172429f3036b99176986685caa69a273defd96264176aeb20fe326bbfe79.
Nie uruchamiać równoległego UART/API testu ani ponownej OTA. Manifest odbioru
`NEW/media93b-acceptance-frozen/manifest.json` SHA
aae4015fe1b6d75d2455c1d9f1dd1d4e236f9733752bdd649f2d4aa958f650da.
Smokev2 zachowuje FAIL w `NEW/smoke93b-shared-views-first/report.json`, lecz
pełny ten sam log dowodzi poprawnej gotowości Light. Harness przerywał odbiór
przed osobną linią Detail, którą następnie wymagał. Nie ma podstaw do poprawki
firmware. Helperv3 SHAa2e2d05d5c6648d1838cf2d95f660a3066553be3d3006eaf603556dae7c6c3a6
kompletuje oba fragmenty;8 offline przypadków, w tym rzeczywista próbka14, PASS.
Sesja56269 zakończona0: smokev3 do `NEW/smoke93b-shared-views-v3` PASS,
następnie3 krótkie porównania do `NEW/scroll93b-repeat-first` PASS w zakresie
opisanym powyżej. Wizualny review5 dodatkowych oryginałów
`NEW/visual93b-shared-scroll-review/review.json` SHA
f26c1613f06c3681b1b158922a274060f9f5981426d8ffebdee5031c3379e1ef.
Pierwsza sesja87176 zakończona1; nie uruchomiła pomiaru Settings.
Action114 nadal wyłącznie izolowany; nic nie wdrożono.
Bez commit/push. Poniżej zachowana historia93/93a i wcześniejszych prób.

## Historia native93a — blokada regulatora Media

Ta sekcja zastępuje poniższe historyczne informacje o trwającej OTA i HA112.
Jedna OTA93 zakończona; `W/panel93-firstboot/first-boot.json` potwierdza
kwalifikowany start, pełne230399 klatek audio i działający nasłuch. Zachowany
`strict_boot_passed:false` dotyczy rozpoznanego, odzyskanego retry miksera przed
sygnałem startowym; nie jest to odsłuch ani test fizycznego zaniku zasilania.
ELF334812afb68b55c6e153b71c6cadf3e6c89173e9d79312448a62808d6461deee.

HA113 zainstalowany jednokrotnie, pakiet61 plików, jeden restart HA. Migracja
356→357 zmieniła tylko akcje slotów24/25 na panel/media. Zapis został potwierdzony,
ale natychmiastowy postcheck pliku nie przeszedł: oryginalny receipt
`NEW/media113-migration-first/receipt.json` pozostaje FAIL. Osobna późniejsza
kontrola `NEW/media113-runtime-after-migration/deployment-acceptance.json`
potwierdza źródła, całą konfigurację i utrwalony układ357. Opóźniony zapis pliku
jest wyjaśnieniem prawdopodobnym, nie bezpośrednio zarejestrowanym. Nie ponawiać
migracji, instalacji ani OTA.

Pierwsza partia sprzętowa Media: `NEW/media93-device-first/report.json` FAIL
przy drugim ruchu głośności42→100 (`Command/service/source feedback deadline`).
Play/pause obu mocków i ustawienie42% przeszły; dla następnego gestu brak COMMAND
i usługi HA w zapisanym obserwatorze. Zachowano8 oryginalnych screenshotów oraz
zdrowy UART bez błędów/resetów. Cleanup wycofał właściciela widoku, lecz przerwał
się na oczekiwaniu tego niewysłanego polecenia; brak końcowego screenshotu Home.
Po tej próbie mock muzyki pozostał na42%; osobne odzyskanie poniżej przywróciło
go bez ponawiania niedostarczonego polecenia i bez zmiany układu.

**Aktualizacja:** recovery wykonany jednokrotnie: `NEW/media93-first-recovery/report.json`
PASS, dokładny poprzedni stan42% przywrócono do100% jedną usługą własnego mocka.
Źródła HA/układ357 zachowane, Home/nasłuch/UART poprawne. Osobny review Home
`NEW/visual93-recovery-review/review.json` potwierdza13 widocznych i3 ukryte sloty.
Kontrast SVG rzeczywiście wymaga poprawki. Native93a ma tylko3 pliki forka:
renderer i2 testy, manifest `NEW/media-style93a-adjunct/manifest.json` SHA
865f71cc209e09ad09859cf159e5b7b60235a821e22f4588ec2974df5ee8fc06.
Root zastosował je lokalnie; `NEW/media93a-applied-first/receipt.json`.
Capture/config/build93a zakończony raz w sesji70132 exit0;
`NEW/native93a-capture-first.log`. Helper SHAfd1b294d0f44fdfe55832c49349015f50d981cdeeeed78b2eb1c155d15577b36.
Źródła93a SHA139283b30700064c368f6f4badb1b0ee9196287370cab790c87df32f2e504c35.
ELF33b02a958a9c28fe3fede5dc511ccb292d6ad74e0d77ed4504845cbbf6e6bd26.
StaticRAM308124B bez zmiany, flash8464322B(+208). Scoped9-function linked review
PASS: `NEW/stack93a-contrast-linked/report.json`, SHA
5fd879802611001102dea9e636935e1ca200f1df109374a3bc671dec2a625a56;
tylko colorlambda +16B stosu, nie uniwersalny bound.
Jedna OTA93a i kwalifikowany pierwszy start PASS, sesja44054 zakończona exit0.
Helper `panel_flash93a_after93.py` SHA
f160bf7ae8206f38e17a12d50cf14af21fda0d8fd02757b46fc4805d7617a6e4;
`W/panel93a-firstboot/first-boot.json` SHAc9a2dbbc0b7615650f38c54dbc73808fefa569a42a54b16af3c72d46d8c17991.
Pełne230399 klatek, nasłuch przez35,949s, jeden start, ten sam kwalifikowany
odzyskany retry miksera przed sygnałem. Strict=false pozostaje jawny.
Artefakt `C:/aeh-build/native-context-v93a/manifest.json` SHA
2183222047c13b2a36622acc0dbd19709e1206cb2b9ad33049da7670a3115f1e.
Nowy harnessv5 SHA3a0f855a85c6d75ad53f3a180e18790fa3f36dfa0b1e7ddb820a00772a6ab79e
rozdziela próbkowanie dotyku i sprawdza postęp renderera. Partia sprzętowa
w sesji13382 zakończona; `NEW/media93a-device-first/report.json` zachowuje FAIL.
Tym razem61% preview i polecenie42→100 zostały rzeczywiście wysłane/wykonane.
Po potwierdzeniu100% Scalar odrzuca completion req16: completed_base161,
current_base162, accepted=false; view_ready/scalar_ready pozostają0. Nie zmieniać
strażnika generacji, zanim źródło późnego native redraw nie zostanie odtworzone.
Podejrzenie: stan disabled nowego Back w widoku Volume i przejście stylu motywu;
diagnoza/reprodukcja hostowa w toku. Cleanup PASS, mocki dokładnie przywrócone,
Home poprawny, UART zdrowy bez resetów/błędów. Nie powtarzać partii w ciemno.
Osobny review9 obrazów `NEW/visual93a-first-partial-review/review.json` SHA
4d9fbd59b80727a9222e77f2b1cbf51f9b2b4f8c33e09e15b816c7628ef779e2
potwierdza naprawiony kontrast ikon i rzeczywisty61% preview; nie potwierdza100%.
Manifest `NEW/media93a-acceptance-frozen/manifest.json` SHA
5e64ada5d83008004f8bbe5d68448d1ece7d5e329c0b664407c34bccb6846427.
Light/Climate i3 pomiary Settings nadal czekają na poprawkę i udaną partię Media.

Manifest nieudanej partii93: `NEW/media93-acceptance-frozen/manifest.json`, SHA
2e9238897ffdba543ba31ebe127fb922a7648fe32580e63dfcdb3edfe1ef8267.
Harnessv4 SHAbe5c9aba7ba8ceaca39198b57fcebe27b4368884334ea53b9cb443d508ec55d7.
Kontrole Light/Climate i trzy porównawcze pomiary przewijania93 jeszcze niewykonane.
Browser potwierdził wybór nowego panelu Media; znaleziono mylące opisy legacy
skrótów pod tym wyborem. Izolowana poprawka JS/testów jest gotowa, ale jeszcze
niezastosowana: `NEW/media113-editor-hint-hotfix-work/manifest.json`.
Action:1 jest implementowany wyłącznie w izolowanych `action114-native-work`,
`action114-ha-work/product` oraz `action-product-work`. HA/UI/native uzgodniły
18 referencji/45 tekstów; native zatrzymano w `PAUSED-93A-DIAGNOSIS.json` podczas
diagnozy blokady. HA/backend i UI mają hostowe testy, lecz nic nie wdrożono.
Slot30 pozostaje bez zmian. Bez commit/push.

## Bieżący checkpoint — 92c przyjęty w opisanym zakresie, Media93 następny

**Live92c / poprawionyHA112 / układ356.** Najnowszy odbiór ma pierwszeństwo
przed historycznymi wpisami: `NEW/accepted92c-checkpoint.json`, SHA
1c29604aa030c420a0b2246d2a8224f562d88f7b82161c175d7b431451c31175.
Pełny build, scoped link, kwalifikacja pierwszego startu,3 restarty,5 mute/unmute,
audio po każdym restarcie,4 panele i9 screenshotów przeszły. Nasłuch rzeczywiście
działa. Każdy boot230399 klatek dźwięku, dodatkowy sygnał118430; nie jest to odsłuch.
Pierwotny FAIL92c pozostaje: szeroki filtr rozpoznał jednorazowy odzyskany retry
miksera obecny także91/92a. Osobny `firstboot92c-qualified-v2.json` obejmuje ten
konkretny przypadek i35,7s dalszej obserwacji tego samego bootu, bez ponownej OTA.

Pierwszy pomiar przewijania49FPS został zachowany. Trzy dalsze krótkie pomiary:
54/54/54FPS, średnio16,314/16,442/16,396ms, failed0, przy działającej detekcji.
Są to2 segmenty fizycznego snapshotu zamiast1 w pierwszym pomiarze; przyczyna
wolniejszego pierwszego pomiaru nie została przypisana. Nie deklarować stałych60FPS
ani idealnej równoważności z92a, gdzie nasłuch nie działał. Kolejne porównania
odnoszą się do tego rzeczywistego obciążenia. Cykle2–5 stabilne pamięciowo;
pierwszy uruchamia dodatkowo istniejący fetchAFE4096B. Końcowe powtórzenie:
internal15099B, PSRAM5075496B. Nie wykonywać kolejnych testów bez nowego powodu.

Podgląd narzędzia potrafił pominąć obiekty z poprawnego screenshotu. Review używa
zachowanych JPEG i bezstratnych PNG o identycznym hashu zdekodowanych pikseli.
Wyniki: `NEW/visual92c-restart-review/review.json` oraz
`NEW/visual92c-ui-review/review.json`. Nie naprawiać firmware na podstawie samego
niepełnego podglądu bez sprawdzenia oryginalnych pikseli.

**Teraz integrować Media jako native93 / HA113, bez commit/push.** Izolowane
manifesty: native23 pliki `NEW/media113-native-work/renderer-delivery-v2/manifest.json`
SHA60b5032c51ab04f93f67aa6597a310df46845678ee150ee60d964b6973f2ff3f;
product27 `NEW/media113-product-work/checkpoint-after92c-v2/manifest.json`
SHA68a6349193944b1997c0e95c091d209dcb943b8b9841a72fede51d1aa3f4b3b6.
HA19 zmian / pakiet61 plików: `NEW/media113-final-moisture-work`;
package SHA5f8421a199932135e443eb9b07b8029807fc3ea850a5f050e2ccd7846d03f7c1.
Niezależny interface review SHA0bc5ee4da7a320c825eed92023e60f4c35d2b38894488fd7241a58dd96ff7769.
Media zastosowano lokalnie:69 plików, `NEW/media93-applied-first/receipt.json`,
status APPLIED_MEDIA93_SOURCE_ONLY_NOT_BUILT_OR_DEPLOYED. Pełny capture/config/build93
PASS: sesja16218 zakończona exit0, `NEW/native93-capture-first.log`,
helper `prepare93_after92c.py`, output `NEW/native93-capture-first`.
Receipt SHA07a0b5fb7977842d8c58b8cd77d554e2e96e5a6beaf7bf420d6b64b7c029d2a3;
source SHAeefddd03f2246ed86a671ebb8496c8eb868ef2eb390811d2e8847d8afcbb3e61;
ELF334812afb68b55c6e153b71c6cadf3e6c89173e9d79312448a62808d6461deee.
Marker2026-11-05 13:57:28+0100, config0x7ebb9f82; RAM308124B(+952),
flash8464114B(+75012). Scoped linked review PASS: `NEW/stack93-linked-runtime/report.json`
SHA9ef7f21388c07c84622aa82dbd029e566e0a59931c18d76b4d75f67f185842d0.
Pierwsza i jedyna OTA93 uruchomiona: sesja98119, `NEW/flash93-first.log`;
helper `panel_flash93_after92c.py` SHA3d0b947f9f1725671822de2bfaf0722651d0bdd5eb861f330dbd691dd2ac19ae.
Jawny wyjątek tylko dla wcześniej zakwalifikowanego jednego odzyskanego retry4096
miksera przed chime. Pozostałe błędy, powtórny reset i niedziałający nasłuch odrzucają start.
Artefakt `C:/aeh-build/native-context-v93/manifest.json` SHA
f56fbd7aa4a882abaaca16fb5a0d97f609da174c3bf7ae1e7b57ce8a3bcc3aab.
Sprawdzać `W/panel93-firstboot/first-boot.json`; nie ponawiać OTA automatycznie.
Nie ponawiać apply/capture bez sprawdzenia istniejących receipt/logów. Urządzenie
nadal92c do potwierdzenia nowego startu, zdalny HA nadal112; nie wykonano instalacji113. Zachować14 zmian
MWW/i18n z92b/c i dokładną poprawkę podpisów112 przed migracją do113.
Aktualny harness Media: `media113_device_acceptance_v4.py`, SHA
be5c9aba7ba8ceaca39198b57fcebe27b4368884334ea53b9cb443d508ec55d7.
V4 zachowuje scenariusze v3 i dodaje obowiązkowy niepusty zapis UART oraz kontrolę
zakończenia/błędów readera. Niewykonane dalsze helpery: `verify_media113_runtime.py`,
`media93_shared_views_smoke_v2.py` i `measure93_scroll_repeat_v2.py`.

## Aktualizacja 92c — pełny build PASS, pierwsza OTA w toku, 2026-11-05

Live pozostaje92a / poprawionyHA112 / układ356. Nie powtarzać nieudanego
pierwszego startu92b: jego dowody i automatyczny rollback pozostają zachowane.
Poprawka92c przeszła13 testów, porównanie wszystkich822 tłumaczeń i kompilację
rzeczywistych jednostek P4. Obiekt i18n ma32 zamiast9892B, tabela9864B trafia
do sekcji tylko do odczytu. Niezależny przegląd nie znalazł blokerów.

Dokładnie7 plików zastosowano lokalnie: `NEW/i18n92c-applied-first/receipt.json`.
Manifest `NEW/i18n92c-work/delivery-v1/manifest.json` SHA
57c6d4a5e69972ddc37b5d89210d91154285b5aa4b83f59368b77b72d1cdf561;
review `NEW/i18n92c-work/independent-review-v1.json` SHA
4de7e7589ea82fb4d973e0dea9153d0089a209e59b604a0ecf14eb106598c429.
Capture/config/build zakończony w sesji94072 exit0, `NEW/capture92c-first.log`;
nie uruchamiać drugi raz. Bazą źródeł jest nieudany sprzętowo92b z zachowaną
rezerwacją MWW, a oczekiwanym poprzednikiem na urządzeniu jest92a.
Źródła92c SHA96fd382a811a1acbbe9e206e3423bae150fbb42367e65e18a7af1b819c1ccc27;
ELF e35b5ab1e065901337a37c2b7a38e1964fbc9c8fe1d109dbd76a6a57580dbdb1.
Marker2026-11-05 12:55:24+0100, config0xa6c2faf9, flash8389102B,
staticRAM307172B. Redukcja obiektu9860B, całej sekcji9856B po wyrównaniu.
Finalny scoped link review PASS: `NEW/stack92c-linked-runtime/report.json`
SHA90a2d31a7719ad834b5f818f4626d7287cead944bffc57cf384d127ee388aec4.
Setup1904+16B, sprawdzone108 wcześniejszych funkcji bez wzrostu stosu.
Pierwsza i jedyna OTA zakończona, sesja55184 exit1, `NEW/flash92c-first.log`.
Upload PASS; oryginalny `W/panel92c-firstboot/first-boot.json` zachowuje FAIL:
zbyt szeroki filtr zatrzymał obserwację na nowym wpisie StaticTask4096,
pochodzącym z jednorazowego retry miksera. Taki sam odzyskany retry i późniejszy
udany chime występowały w91/92a. Dokładne porównanie właściciela i sekwencji:
`NEW/wake92c-known-mixer-retry-classification.json`, SHA
57078bd04878eec6018395bd061cd9dcac25fcbfe475383fcb23d4125123000f.
Nie nadpisywać FAIL i nie ponawiać OTA. Dodatkowa obserwacja tego samego bootu
PASS: `NEW/firstboot92c-continued-first/report.json`, SHA
e8b22d1f3ebf24df82dfab1de6652ef3ea2a9a6ed67de5ff132185b84fc01123.
35 próbek/35,7s rzeczywistej detekcji bez błędów i resetów; uptime214493→250928ms
przy przerwie152960ms dowodzi ciągłości bootu. Home13:15 screenshot przejrzany
przez root, kompletny obraz. Całościowy odbiór wymaga osobnej ścisłej kwalifikacji
znanego retry, trzech restartów, pięciu mute/unmute i pomiaru UI.
Media113 przygotowywane wyłącznie w izolacji; nie wdrażać przed odbiorem92c.

## Aktualny stan — 2026-11-05, diagnostyka wake-word po odbiorze Info/Lock

**Ten wpis ma pierwszeństwo przed historycznymi wpisami poniżej.** Live nadal
native92a / HA112 z poprawką podpisów / układ356. Info/Lock:17 oraz Choice:4
oryginalne screenshoty przeszły przegląd. Jednak92a NIE jest przyjęty jako
wersja bez regresji: UART wykazuje powtarzające się Error flag micro_wake_word,
których wcześniejszy ogólny filtr panic/reset nie obejmował. Sam poprawny I2S
i komunikat "Idle wake-word ready" nie potwierdzały uruchomienia detekcji.
Dotychczasowe is_running() obejmuje także stan STARTING.

`NEW/wake92a-static-investigation/report.json`: kod MWW/StaticTask/audio policy
jest identyczny91→92a; stałe obiekty wzrosły o1776B. Na92a największy wolny
blok INTERNAL jest mniejszy od wymaganych8192B stosu. Zachmurzenie91 i słoneczna
pogoda92a różnią obciążenie blendera, więc nie przypisywać całej zmiany pamięci
samym nowym panelom. `NEW/memory92a-wake-investigation/report.json` po ustaleniu:
PSRAM5145212B, największy3211264B, internal17995B. Baseline92a zakończony:
81 klatek,55 source FPS, avg15919us/max17949us, bez nieudanych prezentacji;
nie jest to pełne porównanie wydajności, bo MWW nie działało prawidłowo.

Priorytet: izolowany kandydat `NEW/wake92b-work`. Domyślnie wyłączona rezerwacja
tego samego stosu INTERNAL8192B i TCB356B przed budową LVGL; żadnej zmiany modelu,
DSP, routingu audio ani przenoszenia stosu do PSRAM. Wczesna rezerwacja nie
uruchamia zadania. is_detecting() oddziela rzeczywistą gotowość od STARTING.
Wymagane: review, konfiguracja, pełny build, pierwsze OTA/boot oraz kilka
restartów z detekcją/audio i reprezentatywne screenshoty/performance.
Kandydat został przejrzany i zastosowany lokalnie jako dokładnie7 plików:
`NEW/wake92b-applied-first/receipt.json`. Manifest poprawki
a2a7cc5e9c31c5b713e292c3bd88794a8704ad19802d283fb8018cd3b2c0aa6c;
niezależny review `NEW/wake92b-work/independent-source-review-v1.json` PASS.
Pełny capture/config/build92b zakończony PASS, sesja66096 exit0;
`NEW/native92b-build.log`. Źródła92b SHA
ad6a92b81b3c06a627035dfdf31c5c023a9ed299d8be0cee5d897e83fa638abb.
Nie powtarzać apply/capture. ELF92b SHA
b25993a04037f8258251dc797a2b235c01937554d4a4ba88e1dc1ef794ff6d10;
flash8410110B, staticdelta0; setup1904+16B. Scoped linked review PASS:
`NEW/stack92b-linked-runtime/report.json`, SHA
f088316ada05ff34a652983a79f9bc84722e4ef671229802098cfcded11865c6.
Artifact `C:/aeh-build/native-context-v92b/manifest.json`, SHA
650ba225ccd58a87c1533da0f429e2fa804229ba656e6e9ce8d28bac784cd683.
Jedna OTA92b została przesłana poprawnie, ale PIERWSZY BOOT FAILED:
`W/panel92b-firstboot/first-boot.json`, sesja5052 exit1. Po13.9s wystąpiło
`pthread: Failed to create task!`, `abort()` przy PC0x40415235 i dodatkowy reset.
Pełny UART zachowany. Nie ponawiać OTA ani nie traktować build/audytu jako
odbioru sprzętowego. Native agent dekoduje właściciela pthread; osobny przegląd
sprawdza strategię przydziału internal/PSRAM. Root zbiera read-only dalszy UART
i aktualną tożsamość po resecie w `NEW/after92b-abort-observation` (sesja59502,
exit0). Sześć odczytów potwierdziło automatyczny rollback do92a/układ356,
tx230399 i amplifier=true; MWW Error nadal występuje. Oryginalny screenshot
odzyskanego Home: `NEW/rollback92a-display/home-original.jpg`, osobny visual
review PASS dla samego obrazu; nie jest to odbiór92b.

Dokładny abort to SendspinHub::loop → SendspinClient::start →
PlayerRole::Impl::start → SyncTask::start → std::thread → exception-disabled
abort. SsSync żąda6192B INTERNAL stosu oraz356B TCB; log nie rozróżnia,
która z tych alokacji nie powiodła się. Raport:
`NEW/wake92b-firstboot-abort-analysis/report.json`.
Media nadal wstrzymane. Przygotowywany92c zachowa poprawkę rezerwacji MWW,
lecz odzyska RAM z niezmiennej tablicy i18n: obecnie822×12=9864B metadanych
w BSS, cały obiekt9892B. Jawna default-off opcja ESP32 `use_flash_table`
generuje statyczną tabelę flash; domyślny add_translation pozostaje zgodny,
w nowym trybie ręczne dopisywanie jest jawnie odrzucone. Product opt-in.
Oczekiwany odzysk9860B wymaga P4 build i sprzętu; nie zmieniać Sendspin,
globalnego allocatora ani stosów/DSP. Nativeagent realizuje izolowany
kandydat, UIagent niezależny review. Nowe harnessy92c są przygotowywane osobno;
92b firstboot FAIL pozostaje trwałym dowodem, nie nadpisywać go późniejszymPASS.
Nowy build bazuje na
immutable92a plus7 plików; jawny drift dokumentów i dokładnie2 plików poprawki
podpisów HA112 nie jest częścią firmware. Artifact92a pozostaje zachowany.

Poprawka podpisów HA112 została zastosowana lokalnie i zdalnie BEZ restartu HA
i bez zmiany układu. Pakiet58 plików: `NEW/extra112-editor-caption-hotfix-work/
checked-package-v1/package.json`, SHA
caa161645505418fbd4bd5aa8f25f87ae14c3fe2aa7109bf3845a8357bb62e5e.
Rzeczywiście serwowany JS ma SHA2fb4466a8056f8b810a5e018f89270432df15de17cf894393398fc4783a42abb:
`NEW/ha112-caption-served-first.json`. Pełny reload przeglądarki potwierdził
"Zamek zablokowano" i datę Agendy, saved356 bez draftu;
`NEW/ha112-editor-caption-fixed.jpg`. Poprzednie screenshoty/paczki zachowane.

Media113 wstrzymane do rozwiązania MWW. Izolowany produkt:
`NEW/media113-product-work/paused-checkpoint-v1/manifest.json`, konfiguracja
admitted=true/false PASS; brak pełnego build/OTA. Nowa paczka HA113 oparta na
rzeczywistym poprawionym112: `NEW/media113-work/ha113-checked-package-v3/package.json`,
SHA1932b70c2311f04ae55932004db7f876a4f58b8b1b24630d3b89daae59fe313d.
Nie używać starej paczki113 z niepoprawionymi preimages112. Brak commit/push.

## Historyczny etap — 2026-11-05, po odbiorze Info/Lock

**Live: native92a / HA112 / układ356.** Jedna OTA i pierwszy start PASS,
230399 I2S frames, bez panic/rollback; odzyskane ostrzeżenia miksera/prealokacji
jak w poprzednich wersjach. Nie jest to potwierdzenie odsłuchu.
HA112 zainstalowany z jednym restartem i zachowaniem options/data. Pierwszy
odczyt zaraz po restarcie był zbyt wczesny i nie znalazł jeszcze websocket API;
log FAIL zachowano. Późniejszy odczyt potwierdził ready oraz profile info/lock.
Jedna migracja355→356 zmieniła wyłącznie pięć zaplanowanych kart i nazwę czujnika.

`NEW/extra92a-device-first/report.json` PASS:17 screenshotów,802474B UART
bez fault/reset, zero poleceń z Info, anulowanie nieaktualnego gestu Lock,
dokładnie jeden lock.lock z pasującym kontekstem i potwierdzeniem stanu mocka.
Źródła przywrócone, cleanup[]. Wszystkie17 oryginałów visual PASS:
`NEW/visual92a-extra-review/review.json`.
`NEW/choice92a-visual-first/report.json` PASS4,168979B UART bez awarii/restartu;
przegląd koloru across renewal/reopen jest kończony. Matched baseline92a działa
w sesji91535, `NEW/baseline92a.log`; nie uruchamiać go drugi raz.

**Pozostała wykryta regresja wyłącznie edytora HA112:** nowy early return
preview omija zwykłe podpisy: Lock pokazuje raw locked, Calendar nie ma daty,
pomijane są też state_labels i formatowanie liczb. Na urządzeniu dane/kolory
są prawidłowe. Agent HA przygotowuje izolowaną poprawkę JS i testy, osobną
paczę hotfix112 oraz przeniesienie do113v3. Nic z tego jeszcze nie zastosowano.
Nie nadpisywać oryginalnych paczek112/113v2. Browser verification zakończony
bez niezapisanych zmian; screenshot `NEW/ha112-editor-observed.jpg`.

Media113: owner18 scenariuszy PASS i niezależny review PASS;
ABI Snapshot728/Message960 bez wzrostu, owner+24B. Renderer/schema/product
pozostają w przygotowaniu; brak kompilacji pełnej/OTA Media. Action/Automation
ma tylko projekt: `NEW/action-automation-after113-design.md`. Slot30 pozostaje
bez migracji do czasu poprawnego handoff do istniejącej Kamery; nie zamieniać
bezpośredniego preview na zajęty panel/history-only.

## Bieżący punkt pracy — 2026-11-05, po kompilacji92

Poniższy skrót ma pierwszeństwo przed zachowanym dziennikiem etapów.
Urządzenie: zaakceptowany native91, zdalny HA111, układ355. Nie wykonano
OTA92, wdrożenia HA112 ani migracji układu. Lokalne źródła zawierają92v2,
produkt92, HA112 i poprawkę bazowej palety Choice/Detail. Bez commit/push.

Pełny build92 PASS (`NEW/native92-capture-20261105/receipt.json`),
source SHA243139aee1cd0a810de24c533e8d64eb55cf4c13fb85959889a0916371a0b78d,
ELF SHA72e9f0cf9b3830f4db2ce2f2b6ef7ae524ed76a469d69bf92bd987d6b048c773.
Static DIRAM317028B, flash8409198B. Linked audit
`NEW/stack92-linked-runtime/report.json` PASS: setup1904+16B, siedem
przejrzanych pełnych ścieżek CLOSE ma konserwatywny minimalny zapas5824B
po takim samym704B marginesie jak91. Nie jest to dowód wszystkich ścieżek
ani test sprzętowy. Kopia ELF i immutable92 pozostają zachowane.

**Przed OTA znaleziono analogiczny problem palety w nowym przycisku Lock:**
Extra pobiera bieżący styl ukrytych referencyjnych przycisków Scalar, które
mogą zachować stan DISABLED/PRESSED. Agent UI potwierdził kolejność lifecycle;
przygotowuje w izolacji minimalną poprawkę i rzeczywisty test public-LVGL.
Nie nadpisywać source92 ani jego wyników. Agent native przygotowuje osobne
helpery92a oparte na92 z dokładnie tym adjunctem, bez ich wykonywania.
Po przeglądzie: zastosować tylko adjunct, capture/config/fullbuild92a,
audyt finalnego ELF, pojedyncza OTA z pierwszym UART, następnie HA112,
migracja355→356 i testy urządzenia/screenshoty. Helpery HA przyjmują wersję
92a; Choice probe wymaga osobnej adaptacji wersji/proweniencji.

Media113 pozostaje izolowane. HA/editor v2:303 powiązane testy Python i447
edytora PASS, niezależny review PASS. Native codec43 poprawne round trips i35
odrzuconych ramek, owner/renderer nadal w pracy. Nie traktować jako wdrożone.

**92a w toku:** adjunct został przejrzany i zastosowany, tylko2 linie runtime
oraz2 pliki testów (`NEW/extra-style92a-applied-20261105/receipt.json`).
Manifest adjunctu9a8f1baf9a8c3de7cdfdcbc119d214a23edf0d9e7853c98215effa5849d5b6a7;
finalny public-LVGL PASS, stary renderer oblewa tę samą asercję koloru.
`NEW/prepare92a_after92.py --execute --compile` działa w sesji69705,
log `NEW/native92a-build.log`. Build92 zachowano bez flash w
`C:/aeh-build/native-context-v92`, manifest e88e30cb311e6a145c6b94815be840fb2dec57a826b411f03d3adac9d6d3ddc6.
Nie ponawiać capture/apply. Capture92a opiera się na immutable92 plus dokładnie
3 pliki adjunctu; nowe zmiany dokumentacji zapisuje jako drift, nie kopiuje ich
do firmware. Helpers SHA: prepare52aef3a980234d2e92f9ab5b4430bda8eb477b7db3192dbddc860c3d31372068,
flash1cb154097b3a32ae3e372c6c3c3633cd9f1f29635d338b2e6c16736b08937962.

Świeży odczyt HA111/układ355 i pięciu providerów demo PASS:
`NEW/extra112-inventory-before-migration.json`. Przejrzana propozycja
`NEW/extra112-migration-proposal.json` zmienia tylko akcje2/3/11/12/13 oraz
nazwę Kontakt→Czujnik zalania i ikonę auto. Nadal NIC nie zapisano do HA.
Po OTA92a i wdrożeniuHA112 wykonać guarded CAS z ponownym odczytem.
`NEW/native92a-ha-helpers-review.json` potwierdza dynamiczną tożsamość92a
w deploy/migrate/Extra acceptance. Oddzielny `NEW/choice92a_visual_probe.py`
SHAfd3d44aeba526f1f570460bdc9bc13772c51d7b398a167d8428a589a211894d9
zachowuje wszystkie guards pierwotnego probe92, zmienia tylko wersję/tożsamość.

**Build92a zakończony PASS, 2026-11-05 11:24:55 CET.** Sesja69705 exit0,
source_after_verified=true. Manifest źródeł
`W/source-v92a-build.json` SHA77eae399d509649283b9ce4d7a0bb22ae314f2171178eabe1d1380af94227f16.
ELF SHA336ba423c2d22018339e2f36ef16686ca4e1be4da7ac58d39c274e649ffe08b5,
static RAM317028B (bez zmiany vs92), flash8409262B (+64B vs92).
Marker kompilacji:2026-11-05 11:13:11 +0100.
`NEW/native92a-capture-20261105/receipt.json` ma status BUILT_NATIVE92A_NOT_FLASHED.
Trwa końcowy audyt dokładnie tego ELF. Dopiero po PASS wykonać
`NEW/panel_flash92a_after91.py` z argumentami capture-receipt, reviewed-elf,
linked-audit, linked-audit-sha oraz execute. Nie uruchamiać preserve/dependency
osobno przed helperem. Nadal live91/HA111/układ355.

**Pojedyncza OTA92a uruchomiona**, sesja4041, `NEW/native92a-flash.log`.
Końcowy audyt PASS: `NEW/stack92a-linked-runtime/report.json`,
SHAa4b8a75661336ce16163ef247430c62f4aee6d531cac86a3ebc09cf52db7ee0c.
Wszystkie99 przejrzanych ramek stosu zachowane vs92, helper palety nie dodaje
ramki, ten sam ograniczony zapas5824B. Input/dependency audit PASS.
Artefakt92a zachowany: manifest c2da02cf169530bac5e4082fd15e1c8635aee3196b1c438f10640a14e5af959e.
Nie ponawiać flash/preserve. Odczytać wynik sesji i
`W/panel92a-firstboot/first-boot.json` przed następnym krokiem.

## Zachowany dziennik etapów

**Wznowiono na polecenie użytkownika 2026-11-05.**
Read-only `C:/aeh-build/device-panels-20261104/resume-20261105-live/report.json`
potwierdził native90d / HA111 / dokładny układ355 oraz COM5. Przerwana próba
pozostaje zachowana. `compile-native90e-resume1`, sesja80448, zakończył się0
z source_after_verified=true (2026-11-05 09:08 CET). ELF SHA
`22a0b7595ad57c46f41ecc216845d9a9912eb01aeb283c172af141f7e1b84b56`,
RAM317036B, flash8355374B. Końcowy setup frame1888+wrapper16 PASS;
audyt pozostałych ścieżek PASS (61 funkcji, ograniczona ocena ścieżek).
Jedna OTA zakończona0, pierwszy start90e potwierdzony09:14 CET:
`W/panel90e-firstboot/first-boot.json`,230399 I2Sframes, wzmacniacz aktywny,
bez mute; te same odzyskane ostrzeżenia prealokacji/startu miksera jak90d,
bez panic/rollback. To nie jest dowód odsłuchu. Manifest artefaktu SHA
`80e955901124804161e156e30dde08760ed0390ffbb3852d231af8f3ed7c27f3`.
Nie ponawiać detail_flash90e_resume1.py ani helperów zachowujących artefakt.
Pełny batch urządzenia90e PASS: sesja44279 zakończona0,40originalJPEG,
`NEW/details90e-device-first/report.json` i `NEW/details90e-uart-first/report.json`.
UART1120362B bez fault/reset; cleanup[], źródła i układ przywrócone.
Wszystkie40 screenshotów przejrzane,5 poprawek potwierdzone:
`NEW/visual90e-review/REVIEW.md` i review.json.
MatchedSettings `NEW/baseline90e/report.json`:54sourceFPS/16197us średnio,
23056us max,0failed. To nie jest pomiar fizycznego60FPS.
Po Settings PSRAM4974976/largest2097152/internal10351; readonly settled probe
potwierdza podobne wartości. Przed Settings internal21759 vs89b23807.
Warunki pogody/życia buforów różnią się; nie twierdzić bez dowodu ani regresji,
ani niezmienionej pamięci. NEW/memory90e-settled/report.json podaje składniki.
Family/menu smoke `NEW/storage90e-smoke-before91/report.json` FAIL na globalnej
obserwacji usług: cykliczne istniejące music_assistant.get_queue i REST odczytu
player_queues/items zostały błędnie policzone jako business commands. Nie było
nativeCOMMAND ani fault/reset; panel zamknięty, Home4. Zachować FAIL. AgentHA
przygotowuje ścisłe rozróżnienie wyłącznie zweryfikowanych odczytów kolejki,
bez wyłączania automatyzacji ani osłabiania kontroli źródeł/układu.
Storage91 jeszcze NIE zastosowany. Gotowy parent-reviewed helper:
NEW/storage91_apply_after90e.py. Osobne entrypointy W/prepare91_after90e.py
i W/panel_flash91_after90e.py przygotowane, nieuruchomione.

**Najnowsze, 2026-11-05 09:45 CET:** powyższy etap został zakończony.
Druga próba globalnego obserwatora też zatrzymała się na niezależnym provisioningu
Pipecat; oba FAIL zachowane. Ostateczny `NEW/storage90e91_scoped_smoke.py`
zachowuje wszystkie guards oraz zero nativeCOMMAND i usług dotyczących13
testowych encji + fizycznych4/7 lub kontekstu panelu; aktywność zewnętrzną zapisuje
osobno, bez twierdzenia o globalnej bezczynności HA. PASS:
`NEW/storage90e-scoped-smoke-before91/report.json`,15originalJPEG,
UART701955B bez fault/reset, cleanup[], dokładne źródła/układ zachowane.
Przegląd wszystkich15 PASS: `NEW/visual90e-family-scoped-review/review.json`.
Zakres90e odebrany (40+15 screenshotów i powyższe ograniczone pomiary).

49plików Storage91 zastosowano lokalnie bez Git/index, z kopią preimages i
hash-check wszystkich11839 plików bazowych. Receipt:
`NEW/storage91-applied-20261105/receipt.json` PASS.
**Capture/config/fullbuild91 PASS**, sesja52624 zakończona0,
source_after_verified=true; `NEW/native91-build.log`.
Source SHA `0bb6dfe9a05f591ed7cb736f4415f12d1853b8554729e00b9e92f9377c75b698`;
ELF SHA `d4034db5375bf29647f9095b60d3feb929c20d13be3252c0094648e6d660624f`.
Static DIRAM315244B (−1792), flash8352622B (−2752 vs90e).
Setup1888+wrapper16B PASS. `NEW/stack91-linked-runtime/report.json` PASS:
minimalny konserwatywny zapas w sześciu sprawdzonych ścieżkach5856B vs560B.
To audyt ograniczonych ścieżek, nie globalny WCET; oszczędności obiektów i
całego firmware nie sumują się. Nie ponawiać capture ani apply.
**Uruchomiono pojedynczą OTA91**, sesja19295, `NEW/native91-flash.log`.
Preserve już zakończony: manifest7930a64b972062ece0164a49c72a76ef4223332271bfcdd3607d5c122df2e3c7.
Nie ponawiać `W/panel_flash91_after90e.py` ani dependency/preserve.
Po potwierdzeniu OTA/firstbootUART:
nested-close91 harness, pełny Detail91 z poprawionym DOWN sampling,
scoped13family/menu oraz matchedbaseline91. Zmiana91 jest wyłącznie storage;
wygląd, protokół i semantyka nie powinny się zmienić.

**Aktualizacja 2026-11-05 10:14 CET:** OTA91 i firstboot PASS,230399 I2Sframes,
te same odzyskane ostrzeżenia startowe, bez panic/rollback; nie jest to odsłuch.
`NEW/native91-ha111-nested-close-first/report.json` PASS:109391B UART,
rzeczywiste caller_stack_min_free_b5856, correlated CLOSE41ms, późny RELEASE
bez polecenia; to syntetyczny test protokołu, nie zmiana fizycznej lampy.
`NEW/details91-device-first/report.json` i `details91-uart-first/report.json`
PASS40screenshots,1117708B UART bez awarii/restartu. `NEW/visual91-review`
PASS40 oraz `NEW/visual91-nested-review` PASS2.39Detail są byte-identical90e;
jedyny zmieniony odczyt to bieżąca temperatura rzeczywistego kotła.
`NEW/storage91-scoped-smoke-after91/report.json` PASS15originals:13family+
Parameters+Home, zero nativeCOMMAND/protected/context services, źródła/układ
zachowane. Przegląd15 jeszcze kończony: Choice27 pokazuje aktywny akcent,
podczas gdy90e snapshot był szary; sprawdzić kolejność readiness/capture.
Matched Settings `NEW/baseline91/report.json`:55sourceFPS, średnio16190us,
max20234us,0failed. Po Settings PSRAM4960316/internal12615 vs90e4974976/10351.
To ograniczona próbka, nie fizyczne60FPS ani dowód identycznego cache pogody.
Nadal HA111/układ355.92 NIE zastosowany; helpers gotowe do przeglądu/aplikacji.

**Najnowszy stan:**91 odebrany w powyższym zakresie.15family visual PASS:
`NEW/visual91-family-scoped-review/review.json`,14byte-identical90e.
Choice ma istniejące również90e próbkowanie kolorów z bieżącego stanu Apply;
szara/akcentowa różnica nie wynika ze zmiany polityki Storage91. Dokładny
trigger kolejności odświeżeń nie był logowany. Oddzielna poprawka92 ma czytać
jawny lokalny kolor DEFAULT, bez przełączania stanu żywego obiektu.

Zastosowano lokalnie, kolejno i bez Git:22native92v2,11product92 oraz22HA112.
Receipty `NEW/native92-applied-20261105/receipt.json`,
`NEW/product92-applied-20261105/receipt.json`,
`NEW/ha112-local-applied-20261105/receipt.json`. Kopie preimages zachowane.
**Urządzenie nadal91, zdalny HA111, układ355.92 jeszcze NIE zbudowany/wgrany.**
Nie ponawiać apply. Czeka osobny adjunct Choice/Detail (lokalne kolory bazowe),
potem `NEW/prepare92_after91.py` po przeglądzie rodzica: capture/config/build,
linked audit, OTA/firstboot, HA112 deployment, jawna migracja pięciu slotów
355→356 i hardware Extra92. Helpery Extra92 acceptance są w v3, SHA
19a662ebc4bcf2dbc29b03b2879b922fc4963a7cb65de3c3783af234784121e1;
`NEW/extra112-preparation-receipt-v3.json` zachowuje v2 i opisuje journal przed
POST + readback po utracie odpowiedzi. Nadal NIE wykonywano zdalnego wdrożenia,
migracji ani nowych prób urządzenia92. Media113 wyłącznie izolowany prototyp.

**Trwa pełny build92**, sesja35996, `NEW/native92-build.log`.
Capture/config zakończone: source SHA
`243139aee1cd0a810de24c533e8d64eb55cf4c13fb85959889a0916371a0b78d`,
`W/source-v92-build.json`; nie ponawiać capture.
Junction SDK wskazuje `C:/aeh-build/native92-sources/fork/esphome/components`.
Choice adjunct5plików zastosowany: `NEW/choice92-applied-20261105/receipt.json`.
Manifest `NEW/choice-style92-adjunct-final/manifest.json` SHA
5c8e4de48eed6e1dc089fa40802bf4494098bb7d35e8607a1c69acabb4e639a0.
Finalny public-LVGL test PASS, oryginalny renderer oblewa rzeczywistą asercję
koloru, drugi caller Detail skompilowany. Zachowano wcześniejsze błędy kompilacji
i błąd konstrukcji testu (null transition descriptor), usunięty z testu przed
finalnym odbiorem; nie był to reset urządzenia.
Capture helper `NEW/prepare92_after91.py` SHA
bbb0084e90d9f4247cb6d05f76e07ef8806e9eb3d11758f70f29f25418079bd2.
Po buildzie final linked/setup audit, następnie jednokrotnie przejrzany
`NEW/panel_flash92_after91.py --capture-receipt NEW/native92-capture-20261105/receipt.json
--reviewed-elf <finalny hash> --execute` (helper SHA
ba6b4404579c804e54fce92f98e6899a036b404cfae7c374301509c982c4f219).
Nie uruchamiać osobno exclusive dependency/preserve przed flash-helperem.
Nowy source-only Choice probe: `NEW/choice92_visual_probe.py`, SHA
c574617632b2b12da3e3834bd551ff43ffa049b0f52f9bf8e27a130228e4c7d8,
parent-reviewed; uruchomić dopiero92/HA112/układ356,4originals across refresh/reopen,
bez poleceń ani zapisów HA. Generic Choice nie eksponuje STATE sequence.
Browser IAB tab1 jest zalogowany i otwarty na edytorze HA; tylko odczyt111/355,
bez niezapisanych zmian. Po112 deployment przeładować i obejrzeć nowe akcje kart.

Nowsze izolowane92: `NEW/native92-after90e-work` (właściwy rebase; stary92
zachowany).19 public-LVGL, independentcorpus/feature tests i10P4units PASS;
P4 Snapshot728/Message960/owner1064 pozostają bez wzrostu, controller+160B.
Nowy produkt `NEW/info-lock-product-after90e-work`, config enabled/disabled PASS,
34obiekty LVGL,822translations; HA111/docs chronione. Nadal NIE wdrożone.
HA112 pełna paczka `NEW/ha112-checked-package`,58files, packageSHA
f0a37bf7529f909d2091f6a2778fec112c287d3adafa3b94bca9ae70dc03aaac;
`NEW/deploy_ha112.py`, `extra_fixture_inventory92.py`, `migrate_extra112.py`
są przygotowane offline, wymagają przeglądu rodzica przed wykonaniem.
Media113 pure-domain prototype `NEW/media113-work` ma21testów PASS,
proposal/wirebounds1580B+DOM4992/5120, ale brak owner/codec/nativeintegracji.
Osobne helpery `preserve_native90e_resume1.py` i `detail_flash90e_resume1.py`
wskazują log zakończonej próby resume1; ich pochodzenie zapisano w
`C:/aeh-build/device-panels-20261104/90e-resume-tool-provenance.json`.
Dalszy tekst to zachowany checkpoint wyłączenia.

Użytkownik polecił zapisać bieżący stan i wyłączyć komputer. Nie kontynuować
samodzielnie po restarcie; wznowić na jego polecenie. Bez commit/push na GitHub.

## Stan urządzenia i repozytoriów

- Ostatni potwierdzony firmware urządzenia: **native90d**, HA **0.4.0.dev111**,
  układ **355**. Podczas zatrzymania niczego nowego nie wgrywano.
- Urządzenie pozostawiono wcześniej na Home5, bez trzymanego dotyku. Mocki po
  testach przywrócone, w tym termostat21°C. Przed następnym zapisem ponownie
  sprawdzić aktualne firmware/HA/układ/dostępność, nie zakładać tego stanu.
- Repozytoria robocze: `C:/Users/kyvai/atmosfera-echo-hub` oraz
  `C:/Users/kyvai/kyvaith-esphome`. Lokalne zmiany pozostają niezacommitowane.
- NEW oznacza `C:/aeh-build/device-panels-20261104`, W oznacza
  `C:/aeh-build/notification-cards-20261102`. Nie usuwać dowodów ani starych FAIL.

## Bezpośredni punkt wznowienia: dokończyć native90e

90d naprawił blokadę regulatora jasności. Testy Light przeszły. Pierwszy pełny
batch zakończył się FAIL na krótkim geście Climate wskutek tempa generatora
dotyku; ten wynik pozostaje FAIL. Osobna kontynuacja Climate, z60ms na
próbkowanie początkowego DOWN, przeszła:21 oryginalnych screenshotów,549359B
UART bez resetów/awarii, dokładnie jedno polecenie22,5°C po puszczeniu.
`NEW/details90d-device-climate-first/report.json` i odpowiedni katalog UART.
Nie zmieniano matematyki łuku ani oczekiwanej temperatury.

90e zawiera pięć drobnych poprawek nowego Detail: przezroczysta nieaktywna
szyna Kelvina, poprawny status listy efektów, neutralny widok po utracie sesji,
polski separator wilgotności oraz uczciwy brak odczytu w termostacie. Produkt
zmienia jedynie prefiks Praca na Stan. Nie zmienia Playera/Kamery/Galerii/Asystenta,
workerów, buforów, rozmiarów struktur ani matematyki regulacji.

Źródła90e zamrożone w `C:/aeh-build/native90e-sources`;
`W/source-v90e-build.json` SHA256:
`b4280f27fef94cd352112b779c2912a6ada73842340c3eb2f633c35861d7b11e`.
Config PASS;36 Detail+11 actualScalar+15 legacyNumber scenariuszy PASS.
`NEW/capture90e-reviewed.json` i `NEW/source-scope84-to90e.json` PASS.

**Pełna kompilacja90e została celowo zatrzymana na polecenie wyłączenia**,
podczas kompilacji ostatniej jednostki main.cpp (log postępu2428/2435).
Zatrzymano tylko zweryfikowane drzewo przygotowania90e, root PID3916.
Sesja47776 zakończyła się kodem1. Nie ma ukończonego artefaktu90e, audytu
końcowego ELF, OTA ani odbioru urządzenia. Istniejący wspólny ELF może nadal
pochodzić z90d — nie wolno go uznać za90e ani wgrać.

Nie uruchamiać ponownie `W/prepare90e.py`: źródła i log istnieją. Dokończyć
build z istniejącego immutable manifestu przez `W/build_native51.py compile`
z nowym unikalnym `--attempt` (np.native90e-resume1), parametrami `--source`
i `--source-sha` powyżej. Najpierw zweryfikować junction
`C:/aeh-build/notification-cards-sdk/components` ->
`C:/aeh-build/native90e-sources/fork/esphome/components`.
Python: `C:/aeh-build/upstream-sync-20261022/.venv/Scripts/python.exe`.
Zachować przerwany `W/compile-native90e.log`; nie nadpisywać go sukcesem.
Helper `W/preserve_native90e.py` odwołuje się do oryginalnego logu/process.json:
przed późniejszym flash przygotować osobny wariant wskazujący zakończoną próbę
wznowienia i jej hashe. Nie omijać audytu źródeł ani11959 zależności.

Po zakończonym buildzie: sprawdzić końcowy SHA ELF, audyt stosu
`NEW/verify_linked_setup_frame.py` (90d frame1888B) i
`NEW/audit90e-linked-runtime.py --elf ... --expected-sha ...`, zachowując
rozróżnienie statycznego audytu ścieżek od dowodu sprzętowego. Następnie jeden
flash z UART pierwszego startu, nie powtarzać helperów tworzących dowody.

Odbiór90e: `NEW/detail_device90e_uart.py --execute --layout-baseline
NEW/layout-after-ha111.json --run-id first`; pełny sampler ma wyłącznie poprawkę
60ms po Climate DOWN. Potem read-only13 rodzin + Parametry:
`NEW/storage90e91_menu_smoke.py --execute --version90e --run-id before91
--capture-parameters` (rozdzielić nazwę opcji i wartość w poleceniu).
Menu smoke SHA `ec1fd8a3645ed2c7995df4b19568425c78e3381fed2e26e119a7cab0470da00f`,
zreviewowany,9 testów offline PASS; nie był uruchomiony live.
Jeden porównywalny pomiar `NEW/panel_baseline.py 90e` wystarczy na pakiet.
Oryginalne JPEG zachować. Przy podejrzanym podglądzie dekodować je bezstratnie
do PNG — podgląd JPEG narzędzia potrafił pozornie pominąć istniejący tekst.

## Następne przygotowane, ale niewdrożone pakiety

1. **Storage91 po90e**: `NEW/refactor91-after90e-work/FINAL-REPORT.md`.
   Freeze SHA `2b973152acd9e1421d8257c02f2aa3ad0f8d10ba53949ee4bc1732c5f3fc42e5`,
   patch `storage91-complete.patch` SHA
   `7d64a7783ff1b758b49fe6a81a6ddbc6f44a90c07c34a7d94fcddd84a4bf0d13`.
   49 plików,36 Detail+11 Scalar oraz4 grupy guarded PASS; wszystkie poprawki90e
   zachowane. Canonical nietknięty. Dopiero po odbiorze90e zastosować z kontrolą
   preimage/hash, osobno zbudować i sprawdzić sprzętowo. W/prepare91.py oraz
   panel_flash91.py mają STAREGO poprzednika90d; potrzebują osobnych wariantów
   po90e. Nie stosować starszego patcha91-after90d.
2. **Info/Lock92**: native `NEW/native92-work` jest WIP na91-after90d;
   strict corpus204+negotiation PASS, DOM5088/5120, renderer jeszcze niegotowy.
   Przenieść tylko nakładkę Extra na nową bazę91-after90e przed kwalifikacją.
   Produkt `NEW/info-lock-product-work/freeze.json` jest izolowany;
   przy integracji zachować polski prefiks Stan z90e. HA112 autorytatywne:
   `NEW/extra-ha112-editor-reviewed-delivery`, patch SHA
   `e7138b968cfa1445c1f78a95c5cfd33a59cc66a8e94aecca0bf92a8f1f77be0e`.
   Nie wdrożono HA112, nie zmieniono układu355. Osobne checkpointy agentów
   doprecyzowują świeże WIP — odczytać przed kontynuacją:
   `NEW/native92-work/RESUME-SHUTDOWN.md` i `checkpoint-shutdown.json`
   SHA `dd616ba51f7542c484c1255cd8c62b1d7d5f50cf293d8f7c761417043aa0a1fc`
   przypinają15 plików draftu. Renderer napisany, ale jeszcze nieskompilowany.
3. **Zewnętrzne media**: `NEW/media-panel-after92-proposal.md` oraz świeży
   read-only `NEW/media-fixtures-before113.json` (slot24/25, dwa osobne
   atmosfera_demo, oba playing, ownership potwierdzony). Lokalny Player/audio
   pozostają poza zmianą. `NEW/media-panel113-WIP-resume.md` zapisuje prace
   projektowe; prototyp protokołu/implementacja Media jeszcze nie powstały.
4. Następnie panele akcji i pozostałych wspieranych domen według
   `device-panels-roadmap-2026-11-04.md`; ten starszy status nie zastępuje
   niniejszego checkpointu ani faktycznych wyników testów.

Użytkownik chce rozpoznawalne dedykowane widoki M3, wyłącznie SVG/natywne
grafiki i kafelki otwierające panele. Wentylator, Humidifier, Cover, Robot/Mower,
Timer, Remote i Power przeszły wcześniejszy odbiór. Mocki nie dowodzą fizycznej
reakcji sprzętu, I2S nie jest potwierdzeniem odsłuchu. Nie powielać testów bez
powodu; nowe zachowanie zawsze zbudować/wgrać i sprawdzić screenshotami.
