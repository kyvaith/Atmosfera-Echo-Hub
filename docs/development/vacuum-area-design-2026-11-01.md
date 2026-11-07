# Sprzątanie przypisanego obszaru — HA76, odbiór ograniczony

Odebrane native45/HA76/246:24scenariusze+Home25oryginałów,3exactusługi/MQTT
przedfeedback i genuine osobny browser V2 na identycznym frozen76.
Siedem serii kontrolnych75:52–54FPS/mediana53;76:53–55/mediana54, failed0.
39canonical=frozen=installed;729Python(3skip)/360Node. Wszystkie cztery
fixtures i osiem własnych obszarów usunięto, także po ponownych restartach HA.
Fizyczny robot i GT911 osobno; bez nowego firmware lub publikacji.
Szczegóły: [walidacja](validation-2026-11-01.md).

Kolejny fragment CTL014/W19: jeden zapisany obszar HA na kafelek, przez
rzeczywistą usługę vacuum.clean_area. Bez mapy, protokołu producenta, nowego
ekranu lub bufora firmware. Nie wybieramy pierwszego obszaru automatycznie.

Core2026.7.1 przyjmuje cleaning_area_id (cv.ensure_list); pojedynczy zapisany
identyfikator HA jest normalizowany przez Core do listy. Core odczytuje
registry_entry.options.vacuum.area_mapping i deduplikuje segmenty przed
async_clean_segments. MQTT publikuje JSON z listą segmentów na
clean_segments_command_topic. Wykorzystujemy ten standardowy kontrakt, bez
zgadywania roomIDs/vendor commands. Lista nazw pochodzi z rejestru obszarów HA;
segmenty pozostają po stronie Core i nie są katalogiem urządzenia.

HA-owned vacuum_areas.py sprawdza rzeczywisty CLEAN_AREA16384, poprawny zapisany
mapping i istniejące obszary. IntFlag jest poprawny; bool/coercion/niebezpiecznie
duże flagi są odrzucane. Maksymalnie32mapowania i32niepuste różne stringi
segmentów na obszar, każdy do128znaków. Nieprawidłowa struktura wyłącza katalog;
usunięty z HA obszar nie jest wyborem. Brak capability, usługi lub mapowania
nie tworzy domyślnego celu. Znane możliwości konfiguracji są odrębne od
wykonania: start obszaru tylko docked/idle/paused. Stan/feedback należy do
Core/provider; polecenie nie udaje sprzątania.

Pole akcji cleaning_area_id jest wymaganym pojedynczym stringiem HA, do128
znaków. Live descriptor zawęża go do aktualnych mapowanych obszarów. Resolver
ponownie sprawdza aktualne mapowanie, obszar, stan, flagę i usługę przy tap.
Nie przyjmuje listy segment_ids, komend producenta ani identyfikatora obcego
obszaru. Wybór w edytorze robi jeden Undo-able szkic, bez Save lub usługi.
Nazwy są etykietami; polecenie nadal używa dokładnego area_id. Dotychczasowe
akcje i moc ssania pozostają osobno. Na kafelku widoczny jest rzeczywisty stan;
użytkownik zachowuje kontrolę nad tytułem karty.

Registry może zmienić mapowanie bez state_changed. Dlatego bridge ma dwa
usuwalne listenery entity_registry_updated/area_registry_updated wyłącznie,
gdy ma widoczną kartę clean_area. Filtruje zdarzenia do jej encji/obszaru,
używa istniejącego coalesced push i usuwa listenery na rebind/unload. Nie ma
nowego timera, pollera lub zadania firmware. Edytor używa obecnej5s cadence
do odświeżenia metadanych wybranego odkurzacza, z istniejącym pending/epoch
fence, oraz jawnego Odśwież pomieszczenia. Wspólne natywne generations,
press_enabled, touch arbitration i snapshoty nadal są właścicielem pikseli.

Piny Core/MQTT pozostają jak przy HA75. Dodatkowe źródła:
W2/installed-vacuum-area-support-source.json (vacuum/websocket.py,
helpers/entity_registry.py, helpers/area_registry.py) oraz
installed-vacuum-area-api-source.json (publiczne WS config/entity_registry
i config/area_registry). Odczytano rzeczywiste options_domain/options i
vacuum/get_segments; fixture ma własną encję i własne obszary.

Odbiór: realne MQTT segments, dwa własne obszary i mapping Core, nazwy/Undo/
noSave w browserze, natywny tap, dokładna usługa i wiadomość segmentów przed
feedback, zmiana/usunięcie mapowania bez zmiany stanu, featureloss/outage,
held ABA/drag, brak komendy w ruchu/error/unknown, oryginały screenshotów,
matched performance i cleanup tylko własnych identyfikatorów. Fizyczny robot,
mapa i wiele obszarów jedną akcją są osobnym etapem.

[Vacuum](https://www.home-assistant.io/integrations/vacuum/),
[MQTT Vacuum](https://www.home-assistant.io/integrations/vacuum.mqtt/).
