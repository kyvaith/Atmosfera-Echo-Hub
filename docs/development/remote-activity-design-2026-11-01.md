# Aktywności pilota we wspólnym Choice — projekt kolejnego fragmentu W19

Stan: ograniczony odbiór native45 / HA81 / układ263 zakończony. Bez publikacji
Git i bez zmiany, kompilacji lub ponownego wgrywania kodu native45.

Core2026.7.1 publikuje ACTIVITY4 oraz activity_list/current_activity. Zmiana
aktywności to remote.turn_on(activity=...), również gdy pilot jest już on.
Lista komend IR/RF nie ma wspólnego odpowiednika w Core; keypad pozostaje
oddzielnym fragmentem zależnym od dostawcy. Źródło Remote przypięto w projekcie
zasilania; nie zakładamy zgodności z samą aktualną dokumentacją internetową.

Najmniejszy spójny kontrakt: jawne v3 control/choice/property:activity. Użyć
istniejącego app6, jednej sesji i jawnego Apply. Maksymalnie8 różnych opcji,
każda do32 bajtów, z dotychczasową walidacją tekstu/fontu. Nie dodawać nowego
transportu, okna surowego obrazu, taska, timera ani protokołu C++.

Backend musi wymagać rzeczywistej flagi4, registered turn_on i dokładnego
activity_list. On/current_activity w katalogu daje aktualny indeks; off oznacza
jawny brak aktywności niezależnie od zatrzymanego starego current_activity.
Wykorzystać istniejące empty_choice_version1 jak przy fan manual. On z brakującą
lub obcą aktywnością oraz unknown/unavailable nie może udawać pierwszej opcji.
Zmiana katalogu unieważnia sesję, a zmiana samego indeksu podlega istniejącej
generacji, również ABA podczas trzymania. Wysłane pole musi zachować dokładną
wartość z katalogu HA, bez tłumaczenia nazwy usługi.

Zachować zwykłe dwie akcje zasilania z HA79 bez dodatkowych pól. Zamiast otwierać
activity w ogólnym typed service editor, walidator live rozpoznaje wyłącznie
zaufany wybór Choice: remote.turn_on z dokładnie jednym activity, ponownie
sprawdzonym w bieżącym katalogu i on/off. Statyczne karty service nadal odrzucają
activity, command i obce cele. Deduplikację i redundant Apply posiada wspólna
sesja. Provider nie może optymistycznie zmieniać stanu po samym poleceniu.

Home zachowuje podpis zasilania zgłaszany przez HA. Szczegóły Choice pokazują
rzeczywistą aktywność; nie dokładamy długich nazw do małych podpisów Home.
Frontend wybiera tryb przez istniejący modal migracji do v3, jawne potwierdzenie,
Undo i Save. Metadane obserwować przez obecny cykl, bez nowego pollera.

Wymagane zmiany: choice_domain/service/state/empty; ChoiceControlPolicy;
deklaracja layout/profile; metadane i live gate cards; frontend availability,
modal i rozpoznanie rodzaju kontroli. Najpierw sprawdzić wszystkie whitelisty
property/domain, zanim zmieni się runtime. Testy modelu, sesji i edytora muszą
potwierdzić power bez regresji, starego peera, off z zatrzymaną aktywnością,
1/8/9 opcji, nieobsługiwany tekst, brak flagi/usługi oraz dokładny target.

Odbiór live: nowy izolowany provider Core RemoteEntity, tym razem z IntFlag4
i rzeczywistymi atrybutami aktywności. MQTT potwierdza komendę przed feedback.
Native wejście z off → wybór → Apply, zmiana aktywności przy on, redundant,
ABA/list-change/drag/outage/off-window/PLEN, real browser/Undo, screenshoty,
guarded inverse, niezależny cleanup/archiwum źródeł QA i krótki pomiar. To nadal
nie potwierdza działania fizycznego nadajnika lub domowego telewizora.

## Implementacja i odbiór 1 listopada

Kontrakt i adaptery opisane powyżej są wdrożone. Metadane remote_activity oraz
schema_remote_activity udostępnia HA. ChoiceControlPolicy rozpoznaje domenę i
property, a istniejący właściciel sesji egzekwuje katalog, generację, kontekst,
autoryzację, deduplikację i potwierdzenie stanu. Home zachowuje zasilanie z HA;
szczegóły pokazują aktywność. Nie dodano bufora, taska, timera, pollera ani pola
protokołu native. Zwykłe karty service nadal odrzucają activity i obce pola.

742 testy Python (3 skip), 368 Node końcowego81, 7 celowanych testów modelu i
sesji, critical Ruff oraz zwykły git diff --check przeszły. 39 plików canonical,
frozen81 i installed jest zgodnych. Python backend80 i81 jest identyczny;
81 poprawia wyłącznie powtórzoną opcję w edytorze, zbędne objaśnienie zasilania
i dostępność pola Po dotknięciu. W rzeczywistej przeglądarce potwierdzono jedną
opcję, wybór przez dokładną etykietę, modal, Confirm, dwa Undo i brak Save.

Receipt: `C:/aeh-build/feature-continuation-20261031-next/ha81-remote-activity-scoped-acceptance.json`.
Nieudany V1 zakończył się po14 ukończonych przypadkach i trzech dokładnych
komendach Radio/Telewizja/„ Żółty ” przed feedback. Test wymagał atrybutów
aktywności podczas unavailable, a rzeczywisty Core je pomija. Zachowano raport,
aktor i oryginały; poprawiono jedynie warunek testu. Wąski V2 na końcowym81
potwierdził 11 pozostałych przypadków, w tym offline, on z nieznaną aktywnością,
1/8/9 opcji, dokładne A7 przed feedback, off-window oraz PL/EN. Nie kopiowano
ACK przeglądarki ze starszej kampanii i nie oznaczono całego V1 jako PASS.

Łącznie25 przypadków, 26 oryginałów funkcjonalnych oraz2 performance przejrzano
w oryginalnym800×800 i contact sheets. Nagłówki mają komplet888 pikseli
nieczarnych w kontrolnym obszarze. Odczyt wycinka oryginału off-window potwierdza
Pilot QA/wyłączono; różnicowy podgląd obrazów potrafi pominąć wspólne piksele.
Przeszły start z off pomimo retained activity, zmiana przy on, redundant,
held ABA, zmiana katalogu, utrata/odzyskanie flagi, unknown, outage i brak
zgadywania pierwszej opcji. Cztery polecenia wykonano na własnej prawdziwej
Core RemoteEntity, która wysyła wyłącznie MQTT i nie posiada nadajnika IR/RF.

Obie kampanie przywróciły własne pola układu, usunęły własny entry/rejestr/stan/
tematy i odwołały tokeny, faults[]. Niezależny audyt SSH potwierdził brak
referencji i przeniósł cztery sprawdzone pliki QA poza custom_components.
16 kart, 3 kamery, 8 preferencji i chronione dane/opcje pozostały zachowane.

Krótka trasa Home/Settings:79 klatek źródłowych,53 FPS, avg16451/max29974 μs,
failed0/segments1; wcześniejszy zakres52–55 FPS i max33034 μs. PSRAM4886 KiB,
internal27, largest2816; app_work/scroll/close0, stałe pule bez zmian. Free+8 KiB
wobec79 odpowiada JPEG−7 KiB; nie przypisujemy tego jako przyspieszenia kodu.
Nie zmierzono utrzymującej się utraty pamięci w tej trasie. Panel FPS, audio,
lifetime oraz fizyczny pilot/GT911 pozostają oddzielnymi bramkami. Keypad,
duże katalogi i komendy zależne od dostawcy nadal są na liście.
