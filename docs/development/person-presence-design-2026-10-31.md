# Osoba i zgłaszana strefa — HA70, odbiór ograniczony

Status: odebrany zakres native45/HA70/209. Fragment CTL022/W18.
18oryginałów Person +14 Calendar +7 performance, prawdziwy browser,53sourceFPS/failed0
na aktywnej karcie i po cleanup. Pełne dowody: validation-2026-10-31.md.
Pasywna karta jednego person.*, bez zdjęcia, mapy ani komend.

Core Person jest jedynym właścicielem rozstrzygania lokalizatorów i stanu.
Atmosfera używa wyłącznie state: home/not_home lub nazwa strefy. Home Assistant
dostarcza pierwszeństwo tłumaczeń home/not_home; brakujące etykiety PL/EN są
w projekcie. Nazwa strefy zachowuje wielkość liter i podkreślenia, po zamianie
na zwykły tekst do40znaków, z jawnym ... przy skróceniu. Puste/unknown/
unavailable nie są interpretowane jako poza domem.

Katalog przekazuje dokładny ograniczony stan i oba podpisy, bez user_id,
trackerów, source, GPS/accuracy, zdjęcia i URL. Edytor pokazuje podpis tylko
dla zgodnego bieżącego stanu; brak encji oznacza offline zamiast starego
stanu katalogu. Istniejące odświeżanie metadanych5s, bez nowego pollera/timera.
Nowa karta domyślnie ma opcjonalny state_color: akcent tylko dla dokładnego
home, surface dla pozostałych stanów. Wyłączenie opcji zachowuje wybraną paletę.

Tylko szeroki slot12 (kafelek440px, rzeczywisty podpis290px).
HA69/V2 przeszedł funkcje/browser/cleanup199, lecz zrzut długiej nazwy W255
ujawnił clipping mimo limitu40znaków; wariant nie został odebrany wizualnie.
HA70 caption_width.py zawiera319 metryk Roboto16 z faktycznie działającego
native45 (main.cpp SHA59eb4429e303474eb71f74a013cc2ba74738de4d7dff00e131d4440abd462f1d).
Caption ma limit40znaków oraz288px (2px marginesu); końcowe... pozostaje w
polu, nawet dla samych szerokich liter. Liczymy advance i końcowy ink extent,
nie używamy fontów hosta ani estymacji szerokości według liczby znaków.
Nieznany glyph ma zachowawczy koszt19px; to nie dodaje brakujących glyphów.
Zmiana fontu lub geometrii wymaga ponownego wygenerowania tabeli i odbioru.
Ten sam fitter chroni Calendar. Zwykłe krótkie etykiety pozostają bez zmiany.
Walidacja server/editor/placement/import/recovery, sensor/actionnone; również
raw/legacy requests nie mogą wysłać akcji. Bez nowych fontów, native danych,
buforów, tasków i protokołu. Właścicielami snapshotów i aktualizacji nadal są
istniejące subskrypcje HA/presentation i komponenty nawigacji. Hidden work
pozostaje odroczony do zwykłego przejścia na stronę.

Plan odbioru:7focused/fullPython/fullNode/static; rzeczywista własna osoba
z user_idNone i własny MQTTrouter tracker, bez kontaHA i bez GPS. Unknown,
home/away/customzone, PLEN, długi/markup/niepoprawny tekst, aktualizacja poza
stroną, tracker unavailable (Core ignoruje źródło → person unknown), brak
source/recovery, pasywne tapy bez usług, realny browser/titleedit/Undo/noSave,
oryginały urządzenia i performance. Przywrócić dokładnie własne pola slot12,
zachować pozostałe15kart/3kamery/8prefs. Usunąć wyłącznie własną osobę,
discovery/topic/registry po sprawdzeniu ownership i braku referencji.

Core2026.7.1: W2/installed-person-source.json, person-schema-preflight.json,
person-crud-source.json. Person SHA
e25368cce1679676b9fd551444368c5fb9728efa5709fc5c5639fc26ded82569.
[Person](https://www.home-assistant.io/integrations/person/).
