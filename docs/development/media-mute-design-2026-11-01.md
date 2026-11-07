# Jawne wyciszanie odtwarzacza — HA82, MED003

Stan: ograniczony odbiór native45 / HA83 / układ268 zakończony.

Kafelek `media_player.*` może otrzymać jawną akcję
`media_player.volume_mute` z wymaganym bool `is_volume_muted`. Edytor oferuje
dwa przyciski M3: wyciszenie i przywrócenie dźwięku. Zmieniają szkic, podlegają
Undo i wymagają zwykłego zapisu układu. Domyślne Play/Pause pozostaje bez zmian.

HA posiada konfigurację, obserwowany stan i dispatch usługi. Dopuszczamy
on/idle/playing/paused/buffering, bit VOLUME_MUTE=8, rzeczywisty bool stanu,
zarejestrowaną usługę i cel przeciwny do obserwowanego. Brak danych, wyłączenie,
standby, unknown/unavailable, utrata flagi, ukryta/bierna karta lub powtórzenie
osiągniętego celu nie wysyłają polecenia. Podpis opisuje stan źródła, a nie cel.
Tłumaczenie atrybutu z HA ma pierwszeństwo przed pakietem PL/EN.

Kontrakt sprawdzono w zainstalowanym Core2026.7.1 i dokumentacji
https://www.home-assistant.io/integrations/media_player/ . Publiczne pole to
is_volume_muted, a provider otrzymuje async_mute_volume(mute: bool).
OFF i unavailable mogą pomijać atrybuty; nie uznajemy ich braku za feedback.
Źródła i hashe: W2/installed-media-player-source-20261101.json.

Native45 nadal posiada kontekst dotknięcia, generację press_enabled, wszystkie
bufory, snapshoty i obraz. Zmiana nie dodaje pól protokołu, pamięci obrazu,
tasków, timerów, pollingów ani subskrypcji. Metadane edytora są związane ze
świeżym stanem i flagami. Stare peers zachowują dotychczasowy wire.

Odbiór używa własnej izolowanej rzeczywistej Core MediaPlayerEntity, z wejściem
i wyjściem przez własne tematy MQTT, bez transportu do domowego głośnika.
Wymagane: dwa natywne tapy → dokładne bool True/False → po jednym broker message
przed feedback; bez pauzy/zmiany utworu/głośności; redundant/offline/unknown/
brak flagi/brak bool/held ABA/drag/off-window/PLEN; rzeczywisty browser i Undo,
oryginały800×800, odtworzenie układu i preferencji, niezależny cleanup, pomiar.
Nie jest to test akustyczny ani fizycznego dotyku GT911. Nie wymaga nowego
firmware, ponieważ używa już zainstalowanego kontraktu native45.

## Odbiór

W2/ha83-media-mute-scoped-acceptance.json wiąże39 plików canonical=frozen83=
installed,749Python(3skip)/371Node/7focused, criticalRuff i normaldiff pass.
Pierwszy test82 zatrzymał się przed pierwszym pełnym przypadkiem: Core zwracał
samo „nie”.83 dodaje kontekst „Wyciszenie: nie/tak” / „Muted: No/Yes”, zachowując
wartość z HA. Oryginalny nieudany raport i źródła82 pozostają w W2.

V2 przeszedł19 przypadków: dwa dokładne natywne polecenia boolTrue/False z
pojedynczym MQTT przed feedback; stan playing,volume.42,titleTrackQA bez zmian
przed feedback. Utrata flagi,brak/string/int bool,off,standby,unknown,offline,
heldABA,drag,off-window,PLEN i redundant blokują niewłaściwe polecenia.
Przejrzano22 oryginały800×800 (20 funkcjonalnych+2 pomiarowe) i contact sheet.
Rzeczywisty browser83: oba przyciski,required boolean,dwaUndo,czysty szkic i
brakSave.16kart/3kamery/8preferencji i chronione opcje/dane odtworzono;268.
Entry/rejestr/stan/tematy usunięte,token odwołany,faults[]. Niezależny SSH audit
przeniósł4 dokładne pliki QA poza custom_components po wyładowaniu.

Standardowa trasa55sourceFPS,79klatek,avg16575/max23453us,failed0,segments1;
wcześniej52–55. PSRAM4884/internal27/largest2112KiB, JPEG912 i stałe pule bez
zmian,work/scroll/close0. RóżnicaPSRAM−2KiB względem81 nie dowodzi trwałej
straty ani przyspieszenia. To pomiar źródła, nie panelFPS/audio/lifetime.
Native45 bez zmian, bez nowego build/flash i bez commit/stage/push.
