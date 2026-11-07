# Dzwonek i podgląd kamery — projekt W15

Wariant Home działa w native76 / HA100 / układ305. Akcja
`atmosfera_echo_hub.doorbell_preview` otwiera wybraną kamerę na czas
15–90 sekund i korzysta z cyklu życia aplikacji Kamera. W podglądzie
obowiązuje stabilny klucz źródła, a zwykły wybór kamery ma osobny stan.
Powtórzenia są rozpoznawane w oknie czterech ostatnich zdarzeń.

Na urządzeniu potwierdzono rzeczywisty MJPEG i wzrost licznika prezentowanych
klatek, identyczny zrzut strony 2 przed i po automatycznym powrocie, zamknięcie
gestem na stronie 4 oraz wybudzenie i powrót na stronę 3. Stan zajęty
potwierdzono podczas otwartych Ustawień, trzymanego dotyku i innego podglądu.
Test z HA użył dostępnego strumienia akwarium. Fizyczny przycisk wymaga
encji lub zdarzenia z integracji dzwonka, a `camera.front` była niedostępna.
Dowody są w `C:/aeh-build/notification-cards-20261102/doorbell76-device`.

Drugi etap dodaje odpowiedź `notification_saved` w trakcie innej aplikacji.
Home Assistant odkłada tekst do historii. W szczegółach pojawia się akcja
„Pokaż kamerę”, ważna przez trzy minuty od zapisania zdarzenia. Kiedy inna
aplikacja jest otwarta, szczegóły pokazują instrukcję powrotu na ekran główny.
Powiadomienie nie zamyka aplikacji. Voice i aktywna kontrolka encji zachowują
ekran bez wysuwanego banera. Na Home jawne dotknięcie akcji zamyka centrum,
oddaje ekran nawigacji i używa tego samego podglądu co pierwszy etap.

Powtórka korzysta z tego samego ID. Udany podgląd zużywa akcję. Po wygaśnięciu
lub restarcie HA pozostaje tekst. Wersja v3 protokołu przesyła typ akcji,
pozostały czas i ID rekordu. Kamera i ponowna kontrola dostępu pozostają po
stronie HA. Poniżej zachowano pierwotne rozpoznanie i kolejność prac.

## Podłączenie zdarzenia w Home Assistant

W automatyzacji wybierz wyzwalacz dostarczany przez integrację dzwonka.
Dodaj akcję „Pokaż kamerę wideodzwonka”, wskaż urządzenie Atmosfera i kamerę
z jego katalogu. Opcjonalny identyfikator zdarzenia pozwala rozpoznać
ponowne dostarczenie tego samego sygnału. Czas podglądu obejmuje 15–90 sekund.
Wynik `opened` oznacza przyjęcie podglądu, a `notification_saved` zapisanie
powiadomienia. To, czy kamera już pokazuje obraz, zależy od gotowości źródła.

## Co potwierdzono w obecnym kodzie

- `LvglNavigation::open_application_()` odrzuca otwarcie, gdy aktywna jest inna
  aplikacja. Samo wywołanie `debug_open_camera` nie zapewnia przerwania,
  zapamiętania kontekstu ani późniejszego powrotu. Nie będzie ścieżką produktu.
- Nawigacja zachowuje `last_home_page_index_`, ale nie ma stosu kontekstów
  aplikacji ani tokenu uprawniającego do automatycznego przywrócenia aplikacji.
  Ponowne otwarcie Voice lub kontrolki po zamknięciu nie odtwarza ich sesji.
- Istniejące `camera_select_source` przesyła indeks. Katalog może zostać
  zastąpiony; sekwencja „wybierz indeks, otwórz” nie jest atomowym żądaniem
  wybranej kamery. W YAML ujemny indeks jest ponadto zamieniany na0.
- HA posiada allow-listę encji, podpisane URL i katalog źródeł. Camera używa
  istniejącego stream workera, JPEG/DSI, loadera i drain przy zamykaniu.
  W15 nie potrzebuje kolejnej kopii klatki ani nowego właściciela transportu.
- `async_show_notification` przenosi obecnie tekst/ikonę/czas. Nie ma pola
  „otwórz tę kamerę” ani typowanej akcji. Sam tekst nie będzie uznany za taką
  funkcję, a kliknięcie zamykające nie może niejawnie otwierać kamery.

## Kolejność wdrożenia

1. Ustalić wersjonowany kontrakt żądania uwagi i jego wyniku. HA przyjmuje
   istniejącą kamerę z allow-listy, a nie URL użytkownika; wybór urządzenia
   i uprawnienia pochodzą ze zwykłego kontekstu usługi HA.
2. Dodać do reusable warstwy kamery atomowy wybór po stabilnym, nieprzezroczystym
   kluczu źródła. Oddzielić tożsamość katalogu od obrotu podpisanych URL.
   Brak/utrata klucza ma odrzucać żądanie, nigdy wybierać pierwszego źródła.
   Dopiero potwierdzony wybór może uruchomić otwarcie Camera.
3. Dodać mały, opcjonalny kontroler uwagi przy istniejącej nawigacji. Posiada
   najwyżej jedno bieżące żądanie, jeden token powrotu i deadline; zero buforów
   obrazu. Produkt deklaruje priorytety, kontroler posiada kolejność przejść
   i odwołanie tokenu. Callback YAML nie odtwarza tej maszyny stanów.
4. Pierwszy osobno odbierany wariant otwiera Camera z bezczynnego Home i wraca
   do dokładnej strony Home. Aktywny gest/settle kończy się przez właściciela
   nawigacji. Aktywnej aplikacji nie zamyka się bez odebranej polityki.
   Wynik „zajęty” jest jawnym wynikiem, a nie pozornym sukcesem.
5. Następnie dodać typowaną akcję powiadomienia i zachowanie podczas aplikacji.
   Voice zachowuje pierwszeństwo; nie wolno zatrzymywać rozmowy dla podglądu
   ani później otwierać nieaktualnej sesji. Kontrolka z cofniętym tokenem nie
   jest kontekstem do przywrócenia. Gallery/Settings/Player potrzebują osobno
   przetestowanych reguł wznowienia. Zdarzenia powtarzane są koalescowane,
   a po utracie ważności nie uruchamiają się z opóźnieniem.
6. Udostępnić usługę HA do automatyzacji dzwonka, z wyborem kamery z katalogu
   i jasnymi wynikami przyjęcia/odrzucenia. Konfigurator nie zakłada jednego
   uniwersalnego typu encji dzwonka: integracje raportują różne zdarzenia.

## Powrót i zasoby

Token powrotu obejmuje właściciela nawigacji, generację żądania i nadal ważny
kontekst. Samo zachowanie numeru aplikacji jest niewystarczające. Ręczna zmiana
kontekstu, zamknięcie przez użytkownika, reset/ponowne połączenie lub utrata
źródła unieważniają nieaktualny powrót. Kolejny dzwonek nie może nadpisać
pierwotnego kontekstu tokenem wskazującym na własną Camera.

Wszystkie otwarcia i zamknięcia używają zwykłego lifecycle Camera i nawigacji:
drain prezentera, wyłączny DSI lease, coherent base LVGL i deterministyczne
zwolnienie obrazu. Loader96×96 pozostaje dotychczasowym direct Lottie.
Nie powstaje nowy raw800×800, kolejka klatek ani drugi stream worker.

## Bramka odbioru

Host: stan/token/deadline/koalescowanie/utrata katalogu, zmiana kolejności
źródeł między żądaniem a obsługą, odrzucenie braku klucza i ponowna dostawa
tego samego zdarzenia. Testować rzeczywistą kompozycję z nawigacją, nie tylko
kopię algorytmu w teście. Nowe opcje upstream domyślnie wyłączone.

Sprzęt: Home1/2/3/4, drag/settle i dotknięcie podczas powrotu, wolny proxy
startup, zerwanie źródła, ponowne żądanie, ręczne zamknięcie, utrata HA,
Voice/Gallery/Settings/Player i wygaszony ekran według jawnej polityki.
Przed/Camera/powrót: zrzuty, rzeczywiste present counter/FPS, pamięć,
DSI FIFO i ciągłość audio. Samo przyjęcie API lub wzrost decode FPS nie
potwierdzają widocznego podglądu. Osobno potwierdzić fizyczny dzwonek.

Najbliższy krok to kontrakt klucza źródła i tokenu nawigacji, potem kod,
testy komponentu, pełna kompilacja, flash i pomiary względem native46.
Nie ma jeszcze zmian źródeł HA94 ani firmware47.
