# Raw deferred Home press identity repair

Status: native46 built, flashed once and qualified with HA90/layout290.

Volume90's first campaign passed the initial Core volume_up and negative states,
but an extra command appeared after held volume42.5→80→42.5 feedback. Its first
report attributed it to the subsequent drag. A second run adds input timestamps,
swipe diagnostics and a longer independent post-release wait: the command occurs
after the held release, before any drag. Both failed reports remain immutable.
Each restored the owned card fields and deleted its own Core entry/state/topics;
the diagnostic switch was independently restored to its original false value.

Home intentionally defers LVGL PRESSED while classifying tap versus drag. The old
TileSurface captured identity only when the deferred PRESSED was finally replayed
on release. Caption updates change the tile's presentation generation without
changing its action context or forcing context readiness false. Therefore the
late PRESSED could capture the new generation and issue a stale held contact.
The existing availability ABA test exercised true→false→true and waited only60ms;
its snapshot gate did not cover this caption-only path.

The optional generic LVGL DeferredPressContext event now captures a widget-owned
generation on raw down, without sending PRESSED or rendering a child state.
Before replay, the listener validates the same target and generation. Material
tiles opt in through the existing action_availability:false-by-default option.
They use the full bounded tile presentation generation and current admission.
Caption, identity, action eligibility or theme changes invalidate a held tap;
an unrelated tile update does not. Existing post-PRESSED context checks still
protect the40ms synthetic release window. Drag capture still suppresses replay.

Ownership: the LVGL input listener owns one small fixed context record for its
current deferred contact; TileSurface owns the generation. All callbacks run in
the LVGL/component input context, with no new worker, task, timer, subscription,
wire message, full-screen allocation or display-buffer handoff. Event registration
uses one process-wide LVGL event ID and adds no per-tile callback. No CPU copies
or display ownership policy changes are introduced. The generic feature define
is generated only when a material surface explicitly enables availability.

Focused tests compile the production listener, navigation defer predicate and
TileSurface against the actual public LVGL dependency. They cover caption ABA,
re-enabled context acknowledged before release, unrelated caption updates,
existing eligibility ABA and disabled contacts. A binary compiled without the
new feature reproduces the exact delayed caption ABA assertion. Default-off and
mixed-instance code generation are separately verified. Test results under
C:/aeh-build/feature-continuation-20261031-next/native46-*tests.log.

Hardware gate: complete native ESP-IDF build and preserved-source audit, fresh
pre-flash marker/full ELF, one OTA, startup and exact post-flash identity. Rerun
Volume90 on native46 with at least one second after held release, genuine browser
Undo/noSave, original800×800 screenshots and before/after performance route.
Retain physical GT911, actual acoustic output and long-duration testing as
separate evidence boundaries. No Git publication is authorized.

## Device acceptance


**Odbiór01.11 native46/HA90/układ290.** W14/MED003: Głośniej/Ciszej z kafelka,
Core volume_up/down i rzeczywisty krok odtwarzacza, opis obserwowanego%.25case,
35oryginałów800×800,actual90browser/dwaUndo/noSave,2exactpublicactions+2Core
poziomy przedfeedback,cleanup39plików/16kart/3kamer/8prefs.777Python(3skip)/
385Node/6focusedVolume/3realLVGL+6codegen. Wykryto i naprawiono opóźniony
deferred tap po zmianie opisu podczas przytrzymania: raw generation przed
PRESSED,bez nowychbuforów/tasków/protokołu. Native46 zbudowany i wgrany1OTA.
Dwie trasy54sourceFPS vs54przed; średnio16673/16704us vs16256,failed0/DSI0.
Nie widać narastającej straty pamięci; zmienna fragmentacja sprawdzona także
rzeczywistą galerią i kamerą(60presentów/10.1presentFPS). Brak fizycznego
odsłuchu/GT911 i nowego odbioru audio/lifetime. [Projekt głośności](media-volume-actions-design-2026-11-01.md),
[poprawka dotyku](deferred-tap-context-design-2026-11-01.md). W14 nadal częściowy:
pełny suwak,seek,browse/favourites/detail pozostają planem. Bez commit/stage/push.

W2/ha90-media-volume-native46-scoped-acceptance.json is the scoped receipt.
The new ELF is7c7ec7a27acb3bd6b577af020b1afa2ee95f3ac8c3e07ad5855dbf560e2dd3de.
SDK configuration, partition table and bootloader are byte-identical to45;
generated main.cpp differs only in frozen-source directory comments. RAM+40B,
flash+512B; no new PSRAM pixel allocation. All11959 shared dependency files and
registry locks were verified unchanged after the native build. Source manifest,
compile inputs, ELF/OTA, map and support files are retained onC. Initial fresh
dependency-copy and scratch relocation attempts exhausted storage; only these
new failed duplicate seeds were removed after verifying intact originals. The
successful build reuses the exact existing dependency cache and a D object
scratch, to be retired only after acceptance and exact artifact verification.
