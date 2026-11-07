# Zgodność podglądu czasu i jawny brak zapisanego pokoju — HA77

Poprawka frontendu HA77 odebrana na native45, układ 254. Backend, firmware45,
obsługa poleceń, subskrypcje i buforowanie ekranu pozostają jak przy HA76.

Przed zmianą rzeczywisty podgląd Router działa pokazywał249046s, a natywny
sensor_text używał kompaktowych dni/godzin. Przyczyną był ogólny frontend
formatEntityState, a nie nowy błąd renderera. Screenshot przed poprawką:
W2/ha76-browser-duration-before.png, czysty układ246.

Frontend dla rzeczywistych sensor/device_class:duration i siedmiu jednostek
μs/ms/s/min/h/d/w teraz stosuje ten sam istniejący kontrakt: registry display
precision (potem sugestia Core) lub precyzja stanu, half-even przed konwersją,
znak, maksymalnie dwa niezerowe człony, subsecond w jednostce źródłowej,
ASCIIus dla greckiego μ i limit10×366dni. Własna mapa state_labels zachowuje
pierwszeństwo; display_precision karty nadal nie zmienia czasu trwania.
Pozostałe klasy i jednostki zachowują dotychczasowy formatter HA.

Obliczenia używają istniejącego ograniczonego cache Intl.NumberFormat i BigInt
o ograniczonej skali. Nie konwertują precyzyjnego tekstu przez binary float.
Core2026.7.1 _as_display_dict publikuje dp z RegistryEntry.options.sensor
display_precision/suggested_display_precision. Frontend obsługuje publiczne
display_precision i ten skrócony klucz; live fixture ma potwierdzić rzeczywisty
odczyt precyzji. Nie dodajemy żądania WS, pollera ani timera. Zmiana napisu
podglądu następuje w istniejącej aktualizacji stanu; nic nie jest wysyłane do
ESP z browsera.

203wspólne cases/PL+EN pinują dotychczasowy formatter Python, m.in. remisy,
zero/znak, jednostki, granice i nieprawidłowe dane. Dwa Python tests dodatkowo
mają ręczne oczekiwania. Node porównuje niezależną arytmetykę JS z kontraktem.
Zasób duration_preview.json nie zmienia projekcji native.

Room selector ma jednoznaczny aria-label. Gdy zapisany area_id zniknie z
aktualnego katalogu, pokazuje jawne niedostępne, zablokowane pole zamiast
innego pokoju. Odrzucony wybór odmalowuje wartość ze szkicu. Nic nie zmienia
zapisanej akcji, a wybór innego istniejącego obszaru nadal wymaga użytkownika.
Zabezpieczenia backend/state/registry/native z HA76 są niezależne i pozostają.

Live odbiór: rzeczywisty MQTTduration sensor z opcjami Core precision, browser
oraz natywne oryginały dla unit/rounding/locale; room-removal browser/Undo/
noSave i natywne denied-state; zero usług aktuatorów, tylko własne fixtures,
odwrócenie własnych kart, cleanup i standardowy krótki pomiar. Nie wymaga
nowego firmware, bo nie ma zmian C++/YAML/fontów/transportu.

## Odbiór 1 listopada

`C:/aeh-build/feature-continuation-20261031-next/ha77-scoped-acceptance.json`
wiąże 39 zgodnych plików źródłowych, zamrożonych i zainstalowanych z dowodami.
731 testów Python (3 pominięte), 363 Node, critical Ruff i zwykły `git diff
--check` przeszły. Wspólne dane obejmują 203 przypadki w PL i EN.

Rzeczywisty czujnik MQTT i opcje precyzji w rejestrze Core potwierdziły siedem
przypadków na urządzeniu: dni/godziny, dwa remisy half-even, ujemne ms, μs,
godziny i EN. Cztery mają osobne, rzeczywiste dowody browsera z czystym szkicem.
V2 zakończył się później błędnym oczekiwaniem testu `Niedostępne` zamiast
rzeczywistego `Niedostępny`; wąski V3 potwierdził outage i cleanup. V1 błędnie
wymagał jawnego press_enabled=false na biernym sensorze; brak pola oznacza
false. Zachowano oba nieudane raporty i oryginały, nie zmieniano produktu.

Osobna kampania pokoju potwierdziła mapped → usunięcie samego mapowania →
disabled na urządzeniu → przywrócenie. Browser pokazał niedostępny zapisany cel,
jawny wybór Biura i Undo do niedostępnego celu, bez Save i usług odkurzacza.
Odczyt evaluate zwrócił stare wartości formularza i część locatorów przekroczyła
czas; dowodem są widoczny screenshot/AX i skuteczny wybór po selektorze CSS.

15 oryginałów 800×800 (w tym 2 performance) i contact sheet przejrzano.
Każdy oryginał ma pełny nagłówek; różnicowy podgląd obrazu pomijał wspólne
piksele i nie był dowodem ubytku ekranu. Wszystkie cztery własne fixtures oraz
dwa obszary HA usunięto; niezależny audyt SSH nie znalazł referencji. Chronione
dane i opcje, 16 kart, 3 kamery i 8 preferencji zachowano.

Krótka trasa Home/Settings: 79 klatek źródłowych, 54 FPS, średnio 16409 μs,
max 23799 μs, failed=0, segments=2. PSRAM 4878 KiB, internal 27 KiB,
app_work/scroll/close=0; stałe pule bez zmian. To mieści się w pomiarach HA76,
ale nie dowodzi panel FPS, audio ani wielogodzinnego lifetime. Nie było nowej
kompilacji/flash ani publikacji Git: zmiana dotyczy wyłącznie frontendu HA.
