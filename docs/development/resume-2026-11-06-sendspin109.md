# Wznowienie po zakończeniu pracy 6 listopada 2026

**Archiwalny checkpoint. Pracę wznowiono 7 listopada na polecenie użytkownika.**
Aktualny stan to native117 / HA131, układ410, Home1; przetestowane źródła są
zapisane w obu lokalnych repozytoriach. Kontynuować od
[checkpointu117](resume-2026-11-07-actionparams117.md), po sprawdzeniu bieżącej
tożsamości urządzenia. Poniższe polecenie wyłączenia i stan109 są historyczne;
nie stanowią aktualnej instrukcji wyłączenia komputera. Bez commitów i push.

**Prace wstrzymane na polecenie użytkownika około 22:48 CET. Komputer ma zostać
wyłączony. Wznawiać dopiero na nową prośbę. Bez commitów i wysyłania na GitHub.**
Ten plik zastępuje wcześniejsze punkty wznowienia. Szczegółowa historia i dowody
107–109 pozostają w `resume-2026-11-05-datetime.md`.

## Stan rzeczywisty

- Repo produktu: `C:/Users/kyvai/atmosfera-echo-hub`, HEAD
  `5de0e0789ab8b9cc76adc2de5195e622370e51d9`.
- Fork: `C:/Users/kyvai/kyvaith-esphome`, HEAD
  `62745ae0c43a233760ddaf1fed60867736832547`.
- Oba na `feature/ha-dashboard-2026-10-24`; dużo lokalnych zmian zachowanych.
  Nie commitowano, nie pushowano, nie resetowano indeksu.
- Kanoniczne źródła, frozen source i build junction zawierają109.
- Urządzenie: native109, ELF
  `e679aeb10b33cae33cf7d456b88b97245bec569f9f62c3658811080dbf43b9d5`.
- Home Assistant127, układ399, Home1, pięć stron. Ostatni read-only pomiar
  potwierdził rzeczywistą tożsamość109/399. HA127 nie instalowano ponownie.
- IP Atmosfera `192.168.88.82`, USB `COM5`; HA `192.168.88.3:8123`.
  Przed kolejnym działaniem sprawdzić aktualną dostępność i tożsamość.

## Co zakończono

Naprawiono niekontrolowane tworzenie zadań Sendspin: sprawdzenie konfiguracji
i wyniku pthread, sprzątanie częściowego startu i ograniczone ponowienia
(produkt4, upstream default0). Bez nowych zadań, zmian stosów i buforów audio.
Testy źródłowe/host/P4, pełny build i linked audit przeszły. Statyczny RAM
311646 B bez zmian wobec108; obraz flash urósł o1000 B.

Jedna OTA109 się powiodła. Pierwszy boot odzyskał Sendspin po dwóch odmowach
utworzenia zadań Protocol/Sync; marker `running; retries=2`. Bez Guru/abort/
rollback. **Oryginalny test pierwszego bootu nadal FAIL/UNCLASSIFIED:** logger
ESP-IDF odfiltrował Worker WARN wymagane przez parser. Nie przepisywać tego
wyniku ani brakujących phase/errno. Osobna kwalifikacja źródłowa wiąże dokładne
E-caller z retry/running, nie twierdzi, że brakujące dane były w UART.

Późniejszy, osobny read-only pomiar przeszedł:35,77 s, ponad30 próbek, pełne
230399 ramek PCM, wake aktywny, wzmacniacz aktywny, bez nowych faultów/resetów.
RAM wewnętrzny22835 B, PSRAM4921176→4921244 B, największy blok3407872 B.
To potwierdzenie cyfrowego przesyłania audio, bez odsłuchu fizycznego.

Boot109 zawiera dwa DSI underrun. Pełny DSIMEM1 wystąpił w linii poprzedzonej
fragmentem innego logu: MSPI0x18 to normalne zakończenia; cache/AHB błędy0;
CPU RAW0x2c ma zatrzaśnięte timeouty bez daty powstania. Nie ustalono przyczyny
wcześniejszego TLSF/Guru107 przy Agenda→Home. Nie uznawać109 za odbiór
stabilności ani za pomiar wydajności (diagnostyka ROM wpływa na czas).

**Nie wykonano trasy Agendy109, screenshotów109 ani trzech restartów109.**
Screenshoty i restarty107 pozostają oddzielnymi wcześniejszymi dowodami.
Statistics1 oraz przenoszenie kolejnych funkcji są wstrzymane do wyjaśnienia awarii.

## Najbliższy krok po wznowieniu

1. Przeczytać ten plik, poprzedni checkpoint i aktualne AGENTS.md. Sprawdzić
   tożsamość urządzenia, układ i brak aktywnego odtwarzania przed zapisem.
2. Dokończyć wyłącznie admission wrappera
   `NEW/agenda109_route_after_observation.py`. To **niewykonany draft**:
   ostatni test offline zatrzymał się na sprawdzeniu SHA obserwacji/DSI w linii35.
   Najpierw porównać rzeczywiste hashe; w przekazanej ręcznie wartości SHA
   obserwacji była literówka. Nie omijać kontroli ani przepisywać dowodów.
3. Po wąskim review uruchomić jedną diagnostyczną trasę na tym samym109:
   niezmieniony `agenda109_diagnostic_route.py` robi6 PAGE,7 oryginalnych JPEG,
   dwa zamknięcia i powrót Home→pamięć→audio. Bez OTA/CAS/usług providera.
   Dopuszczenie ma jawnie zachować FAIL bootu i rozdzielać późniejszą obserwację.
4. Przy nowej awarii przerwać bodźce, zachować rawUART i dekodować właściwy ELF.
   Gdy DSIMEM nie rozstrzygnie problemu, jest przygotowany plan ograniczonego
   sprawdzenia integralności sterty; nie dodawać go ani nie budować w ciemno.
5. `mixer109_device_restarts.py` jest gotowy, ale wymaga starego PASS-firstboot
   i PASS-route; z aktualnym FAIL nie uruchamiać ani nie obchodzić bramki.
   Ewentualna adaptacja kwalifikacji musi pozostać jawna i źródłowo uzasadniona.
6. Brakujące logi Worker można w przyszłym potrzebnym buildzie zmienić
   z SS_LOGW na SS_LOGE w5 miejscach odmowy startu. Nie wykonano tej zmiany.
   Nie podnosić globalnego poziomu logów ani nie robić OTA tylko dla parsera.

## Pliki i dowody

`NEW = C:/aeh-build/device-panels-20261104`

`W = C:/aeh-build/notification-cards-20261102`

- Frozen109: `C:/aeh-build/native109-sources`; źródła `W/source-v109-build.json`,
  SHA `6d2ed5b83095aa6938df84884455efab763282ba18beb1736b2e11b33febb883`.
- Dostawa: `C:/aeh-build/sendspin109-native-work/delivery-v2/manifest.json`,
  SHA `6739856f128ceeb21319c94db99d69931940a78df1fc7e9d904ad77262a1f8e5`.
- Capture: `NEW/native109-capture-first/receipt.json` — zakończony build;
  nie uruchamiać ponownie.
- Linked audit: `NEW/stack109-sendspin-linked/report.json`.
- Obraz: `D:/aeh-build/native-context-v109/manifest.json`, SHA
  `065a1bc65d8febd8d0bb65afbff469742fb64ef638c6163de7aa2197f2016a24`.
- Zachowany FAIL: `W/panel109-firstboot/first-boot.json` i `device-uart.raw` obok.
- Źródłowe wyjaśnienie: `NEW/native109-startup-source-reconciliation.json`.
- Późniejszy pomiar: `NEW/native109-later-readonly/report.json` i rawUART obok.
- DSI: `NEW/dsimem109-firstboot-readonly.json`.
- Log filtering: `NEW/sendspin109-loglevels-source-review.json`.
- Draft i przerwanie: `NEW/agenda109-wrapper-paused-checkpoint.json`;
  wrapper SHA `bc4b0e0cfaeb534339e3f96cc7cf150218d56a9ae6ec8c10da501f96d7482e1a`.
- Trasa bazowa SHA `99f7af0bd5885a2678680be8e95e66d002a8df39c35a6a6af2ffb5c9172541e0`.
- Plan dalszej diagnostyki: `NEW/heap-integrity-after-dsimem-plan.md`.
- Aktualne hashe dowodów i stan Git są zapisane w
  `NEW/shutdown-20261106-2248/manifest.json` oraz plikach obok.
- Python narzędzi: `C:/aeh-build/upstream-sync-20261022/.venv/Scripts/python.exe`.

Nie usuwać starych źródeł, logów i cache na podstawie nazw. Nie ponawiać
wcześniej odrzuconych usunięć. W tej sesji tylko kompresowano wskazane
historyczne pliki NTFS, aby odzyskać miejsce; niczego nie skasowano.
