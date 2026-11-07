# Kierunek rozwoju po przeglądzie z 2 listopada 2026

To doprecyzowanie planu z24 października. Obowiązuje dla kolejnych pakietów;
nie oznacza wdrożenia opisanych niżej widoków. Stan przyjęty: native46 / HA94 /
układ298. HA94 zmienia wyłącznie rozmiar Wi-Fi w podglądzie i wersję zasobu HA.

## Player i wideo

Dedykowany Player jest główną aplikacją lokalnego odtwarzania: Sendspin,
artwork, kolejka, grupy i głośność pozostają w istniejącej ścieżce. Dodane
adaptery dowolnych `media_player` są opcjonalnymi skrótami sterującymi innymi
odtwarzaczami. Dalsze browse/favourites/seek należy projektować przede wszystkim
jako rozwój naszego Playera, bez drugiego właściciela I2S.

Dzwonek i inne strumienie używają istniejącej aplikacji Kamera, katalogu HA,
normalizacji MJPEG, sprzętowego JPEG i DSI lease/present. Nie powstaje drugi
dekoder/worker ani nowy surowy bufor pełnoekranowy. Projekt dzwonka pozostaje
w [osobnym dokumencie](doorbell-design-2026-11-01.md).

## Ikony urządzeń

Obecny katalog konfigurowalnych kafelków nie zawiera jeszcze ikon kosiarki
ani robota odkurzającego. Nie uznajemy ogólnej strzałki akcji za właściwą ikonę
tych urządzeń. W najbliższym pakiecie firmware dodać semantyczne `mower` i
`vacuum`, pasujące ikony Material Design Icons i ich ograniczony zestaw glifów
we wszystkich faktycznie używanych rozmiarach fontu. Edytor i firmware muszą
mieć to samo mapowanie; wdrożenie HA dopiero razem ze zgodnym firmware.

Produkt korzysta teraz z Google Material Symbols Rounded, natomiast katalog HA
z MDI. Są to różne mapy kodów. W oficjalnej mapie Google potwierdzono `vacuum`
U+EFC5; nie znaleziono nazwy mower. Nie przypisywać zgadywanego kodu z innego
fontu. Dla robota i kosiarki można dołączyć dwa zweryfikowane glify MDI do
istniejących subsetów zamiast całego drugiego fontu. Dowód mapy Google i hash:
W3/material-symbols-rounded-codepoints.txt. W3 oznacza katalog dowodów
`C:/aeh-build/feature-continuation-20261102`, poza repozytorium.

## Termostat

Istnieją adaptery pojedynczej nastawy, HVAC, presetów, wentylatora, kierunku
nawiewu i docelowej wilgotności. To wspólne Number/Choice, nie dedykowany ekran
termostatu. Nie ma jeszcze ładnego widoku termostatu ani edytora histerezy.

Nowy ekran M3 Expressive powinien pokazywać bieżącą temperaturę, nastawę,
rzeczywisty stan grzania/chłodzenia i zakres urządzenia. Pierścień jest
prezentacją; regulacja nastawy korzysta z istniejącego właściciela sesji,
autoryzacji i potwierdzenia źródła. Układ nie wykonuje usługi przy samym
otwarciu. Szczegóły/parametry mają własny bounded scroll.

Histereza nie jest tym samym co krok temperatury ani zakres heat_cool.
Publiczny Climate nie daje uniwersalnej usługi ustawiania histerezy.
[Generic Thermostat](https://www.home-assistant.io/integrations/generic_thermostat/)
ma osobne parametry cold_tolerance i hot_tolerance oraz reguły cyklu.
Nie dodawać lokalnej pętli sterującej palnikiem obok regulatora HA/urządzenia.

Dzisiejszy odczyt dwóch integracji użytkownika nie wykazał encji ani usług
histerezy, także pod polską nazwą. Jedna encja działa, druga raportuje unknown.
Aktywna encja nie publikuje target_temp_step, wymaganego przez dotychczasowy
adapter dokładnej nastawy. Przed rozszerzeniem odczytać kontrakt jej providera;
nie zgadywać kroku. Histerezę udostępnić przez rzeczywistą encję/usługę konkretnej
integracji albo jawnie skonfigurowany regulator HA. W innych przypadkach pokazać
brak obsługi. Niczego nie zmieniono w nastawach ogrzewania.

## Powiadomienia od góry i centrum

Obecnie działa NotifyEntity HA oraz dolny panel z czteroelementową kolejką.
Nie istnieje historia ani żądane gesty. Docelowe zachowanie:

1. Nowe powiadomienie wsuwa się z góry, w bezpiecznym obszarze okrągłego panelu.
2. Gest od górnej krawędzi w dół otwiera centrum przeszłych powiadomień.
3. Przesunięcie wiersza w bok zamyka konkretny wpis; tap otwiera jego szczegóły.
4. Jawny, typowany action ID może otworzyć np. istniejącą Kamerę. Samo zamknięcie
   nie wykonuje akcji. Brak dowolnej usługi/URL/kodu otrzymywanego z firmware.

HA posiada historię i retencję: proponowane100 metadanych/24h,8 wpisów na stronę.
Urządzenie używa ograniczonej puli wierszy i jednego właściciela aktywnego
widoku. Dismiss ma trwałe ID i rewizję, by opóźniona odpowiedź nie przywracała
usuniętego wpisu. Offline pozwala przejrzeć posiadane dane; wykonanie akcji
wymaga aktualnego kontekstu i połączenia.

Gest górnej krawędzi musi wejść do obecnego arbitra gestów. Nie może równocześnie
uruchamiać Home swipe, close aplikacji lub kliknięcia kafelka. Kamera/Gallery/
Voice wymagają pauzy i drain prezentera oraz poprawnego powrotu. Obecny overlay
nie ma jeszcze kompletnego kontraktu uwagi i exclusive full-screen handoff;
samo odwrócenie znaku animacji nie stanowi wdrożenia centrum.

## Dodatkowe strony karuzeli

Pierwszy etap W12 udostępnia pięć stron i 32 bindingi, w tym dwa ukryte
sloty zgodności. HA zapisuje kolejność i widoczność, Home zostaje na
początku, a Aplikacje pozostają dostępne. Zmiana trasy zachowuje powiązania
kafelków ze stronami. Profile starszych urządzeń zachowują 16 bindingów.

Limit produktu wynosi pięć stron. Próba native84 objęła 36 przesunięć
przy czterech stronach i 48 przy pięciu. Mediana wyniosła odpowiednio 44
i 44,5 FPS. Licznik sprzętowy DMA rósł przez każdą serię. Przy pięciu
pozostało co najmniej 4,39 MiB PSRAM i 21,4 KiB pamięci wewnętrznej
w próbkach po przejściach. Po pełnej trasie aplikacji wewnętrznej pamięci
pozostało około 12,8 KiB. Szósta strona wymaga pomiaru kolejnego szablonu
i szczytowego zużycia pamięci przy aplikacjach.

Istniejący compositor ma trzy surowe sloty oraz JPEG backing dalszych stron,
worker prefetch i recykling slotu po zmianie okna. Trzy raw RGB888800×800
kosztują5 760 000B niezależnie od liczby stron. Kod ma również wspólny limit
24 wpisów cache, obejmujący inne źródła snapshotów; trzeba go uwzględnić.

Zachować bieżącą stronę i sąsiadów. Dwie strony wcześniej można przygotować
skompresowane backing; zdekodowanie dodatkowej pełnej strony wymagałoby czwartego
raw slotu1 920 000B albo wyrzucenia nadal potrzebnego sąsiada. Domyślnie tego
nie dodawać. W oknie pozostają trzy sloty; hardware JPEG odtwarza kolejną stronę
do bezpiecznie zwolnionego slotu. Dirty/generation i anulowanie prefetch po
zmianie kierunku zapobiegają użyciu starego obrazu.

Sprawdzona tabela partycji dokładnego native46:

| Obszar | Rozmiar |
| --- | ---: |
| app0 | 16 128KiB |
| app1 | 16 128KiB |
| NVS | 448KiB |
| Pozostałe | otadata8KiB, PHY4KiB, obszary boot/tabeli i wyrównania |
| Nieprzydzielony obszar ponad ostatnią partycją | 0B |

Wolne miejsce wewnątrz slotu OTA nie jest bezpiecznym filesystemem cache.
Nie nadpisywać nieaktywnego firmware ani NVS snapshotami. Flash backing wymaga
osobnej partycji i migracji układu/rollback; zapis tylko dirty z koalescowaniem,
CRC/generation, atomowym zastąpieniem i odbudową po utracie zasilania.
Ograniczenia erase/write opisuje
[Espressif](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-reference/storage/wear-levelling.html).
To ogólna charakterystyka flash, nie propozycja zmiany naszego IDF5.5.6.

Przed podniesieniem limitu do sześciu stron zmierzyć JPEG w PSRAM, szczytowe
i utrzymane zużycie pamięci oraz szybkie zmiany kierunku. Flash lub karta SD
pozostają opcją po pomiarze kosztu i sprawdzeniu sprzętu.

## Testy i kolejność pakietów

Pełna trasa wydajności przy każdym małym adapterze była nadmiarowa. Były też
wartościowe odkrycia, np. rzeczywisty zaległy tap naprawiony w native46.
Zachowujemy testy poprawności i screenshoty, grupując pełne pomiary.
Szczegóły są w [polityce walidacji](validation.md#batch-validation-policy-2-november-2026).

1. Odbiór wymagań i lista stanu; szybka poprawka Wi-Fi w HA94 — zakończona.
2. Pakiet UI: semantyczne ikony i powiadomienia od góry/centrum; jeden wspólny
   kontrakt uwagi, testy gestów i framebuffer lifecycle, pełna kompilacja/flash.
3. Dedykowany termostat z parametrami rzeczywiście dostępnymi z backendu.
4. Dzwonek na istniejącej Kamerze, z typowaną akcją i tokenem powrotu.
5. Pięć stron z trzema raw slotami wdrożone. Kolejny szablon i resize
   wymagają osobnego pomiaru i odbioru.
6. Dalszy rozwój dedykowanego Playera: biblioteka/ulubione/picker/seek.

Kolejność może się zmienić ze względu na zależności kontraktów, bez wracania do
serii drobnych adapterów zewnętrznych odtwarzaczy. Bez commit/push bez polecenia.
