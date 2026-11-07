# Tryb dźwięku odtwarzacza HA — W14 / MED003

Stan: ograniczony odbiór native46 / HA91 / układ292 zakończony.

Zainstalowany Core2026.7.1 publikuje sound_mode, sound_mode_list oraz capability
SELECT_SOUND_MODE65536. Publiczna usługa media_player.select_sound_mode wymaga
jednego pola sound_mode typu string i deleguje je do MediaPlayerEntity.
Źródła z hashami: W2/installed-media-player-source-20261101.json oraz
media-sound-mode91-installed-contract.json. Lista jest własnością integracji
danego odtwarzacza; nie wymyślamy nazw Muzyka/Kino ani domyślnego pierwszego trybu.

HA91 mapuje jawne v3 choice/property:sound_mode na istniejącego właściciela
Choice, ekran app6 i pulę ośmiu wierszy. Katalog musi zawierać1..8 różnych nazw,
każda do32bajtówUTF8, bez sterujących separatorów i sentinelunknown/unavailable.
Wymagamy aktywnego stanu on/idle/playing/paused/buffering, bitu65536 i obecnej
usługi. Znany bieżący tryb jest dokładnym indeksem; brak lub wartość spoza listy
nie wybiera pierwszego trybu. Istniejący ekran może pokazać brak bieżącej wartości
z wyłączonym Apply; edytor dopuszcza konfigurację nowej karty dopiero dla znanego
trybu. Utrata katalogu/capability unieważnia sesję, a stary index nie wraca po ABA.

Własność nie zmienia się: HA posiada katalog, tłumaczenie, uprawnienia i pojedynczy
service fence; natywny Choice posiada kandydat i gest Apply. Nazwy usług/pól nie
pochodzą z urządzenia. Wysłanie jednej komendy z dokładną surową nazwą nie zmienia
optymistycznie playback/source/volume/mute/repeat/shuffle ani samego trybu.
Potwierdzenie pochodzi ze źródła. Opis Home i edytora ma136px i prefiks Tryb:/Sound:;
widoczna wielokropkowa końcówka nie skraca wartości usługi ani natywnego katalogu.

Bez zmian w forku/native46, protokole, buforach, taskach, timerach, subskrypcjach
i właścicielu I2S. UI używa istniejącego przeglądu szkicu M3/Undo/noSave. Weryfikacja:
7focused Python, cały zestaw784(3skip),389Node i criticalRuff. Następna bramka to
rzeczywista własna CoreMediaPlayerEntity emitująca tylko własnyMQTT, natywne tap/
Choice/Apply, powtórzone żądania, heldABA, zmiana listy/capability/outage,1/8/9opcji,
PLEN, długie/Unicode nazwy, zgodność opisów, browser/Undo, screenshoty, performance,
odwrócenie wyłącznie własnych pól i archiwizacja własnej tymczasowej integracji.
Fizyczny amplituner/DSP pozostaje osobnym dowodem.

## Odbiór


**Odbiór01.11 native46/HA91/układ292.** W14/MED003: wybór trybu dźwięku
z rzeczywistego sound_mode_list,bit65536/select_sound_mode. Istniejący Choice/
app6/1..8nazw32UTF8b; bez nowych buforów/tasków/protokołu/nativeflash.
5exactstrusług+MQTT przedfeedback, w tymUnicode/spacje i długa nazwa; playback,
source,volume,mute,repeat,shuffle,title bez zmian.32case/35oryginałów800×800,
aktualny91browser/review/dwaUndo/noSave,cleanup39plików/16kart/3kamer/8prefs.
784Python(3skip)/389Node/7focused/criticalRuff/diff. Trasa54sourceFPS/avg16399/
max24821us/failed0/DSI0. PSRAM3501/internal23/largest2560KiB/JPEG2104,rawwork0;
free−6vs poprzedni media-check odpowiadaJPEG+5 i zaokrągleniu, stałe pule te same.
[Projekt i dowody](media-sound-mode-design-2026-11-01.md). Fizyczny amplituner/DSP
osobno; W14 nadal częściowy. Bez commit/stage/push.

Receipt: W2/ha91-media-sound-scoped-acceptance.json. Własna rzeczywista
CoreMediaPlayerEntity emituje dokładne publiczne sound_mode i provider_typestr:
Movie,Music,` Żółty `,A7,`Dolby Surround Living Room`. Przedfeedback cały
stan i atrybuty są niezmienione. Brak powtórzeń przy redundantnymApply/heldABA,
zmianie listy/utraciecapability/unknown/outage.1/8/9opcji,off/standby/off-window,
PLEN i długie nazwy przeszły. Pełne nazwy w natywnym Choice i MQTT, mierzone
136px opisy z widocznym... na Home i w edytorze. Rewizja292 przywraca oryginalny
układ, chronione opcje/dane i preferencje. Entry/registry/stany/tematy usunięto,
token odwołano, cztery dokładne źródła niezależnie zarchiwizowano poza aktywnym
custom_components. Native46 zachowany z tym samym pełnymELF; brak nowejkompilacji
lubflash dla adapteraHA91. W tej serii native46 wcześniej zbudowano i wgrano
dla naprawy rawdeferredtap; dowód jest oddzielny od odbioru adapterówHA.
