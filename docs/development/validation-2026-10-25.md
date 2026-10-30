# Resumed device validation — 2026-10-25

This follows the [stop checkpoint](resume-2026-10-25.md). Nothing was committed
or published. HA17 is now installed; earlier HA12 browser acceptance is
recorded in the [HA ledger](ha-dashboard-2026-10-24.md).

## Raport stanu na koniec dnia

Prace zostały zatrzymane na prośbę użytkownika 25.10.2026. Działa **firmware 26,
integracja HA 0.4.0.dev17 i układ 12**. Przywrócony jest akcent AEE2FF i język
polski. Wilgotność pozostaje na miejscu 6, Światło 1 na 7, W domu na 15 — numery
wewnętrzne od zera. Pomocniki testowe usunięto, szkic tytułu cofnięto, edytor
nie ma niezapisanych zmian. Nie wykonano commitów ani push na GitHub.

### Co zostało zaimplementowane

| Obszar | Działający zakres | Granica potwierdzenia |
| --- | --- | --- |
| Integracja i edytor HA | Wybór ekranu, katalog encji z wyszukiwaniem/filtrami, podgląd, konfiguracja i przeciąganie kart w istniejących miejscach | Zainstalowane w rzeczywistym HA; dotyczy obecnego profilu i edytowalnych stron, nie dowolnego kreatora stron |
| Narzędzia edycji | Undo/redo, szkice, import/eksport, kopiowanie oraz ograniczone operacje grupowe/wygląd | Testy hostowe i scenariusze przeglądarkowe; szersze warianty wielu klientów i urządzeń pozostają do domknięcia |
| Zapis konfiguracji | Rewizje, walidacja, konflikt zapisu, osobne zapisano/wysłano/odebrano i stan snapshotów | Odebranie konfiguracji nie jest automatycznym potwierdzeniem fizycznego wyświetlenia wszystkich stron |
| Dane HA na kafelkach | Rzeczywiste stany, etykiety i formatowanie zamiast części stałych napisów; aktualizacja przez istniejące API ESPHome | Zastosowany zakres opisuje osobny rejestr sensorów; pełny katalog wszystkich domen nadal otwarty |
| Panel światła | Włącz/wyłącz i regulator jasności, powrót do Home oraz obsługa sesji | Natywny ekran, usługi i stan wirtualnego pomocnika HA oraz screenshoty; brak podłączonej fizycznej lampy |
| Number/input_number | Przyciski minus/plus, kroki ułamkowe, zakres min/max, wartości ujemne i potwierdzenia stanu HA | Izolowane testy HA/urządzenia i oryginalne obrazy; pełna lista interakcji długiego przytrzymania pozostaje otwarta |
| Lokalizacja | Polski/angielski w odebranych widokach; pogoda i panel wartości; poprawny separator 0,25/0.25 | Firmware 26 przeszedł PL→EN→PL na urządzeniu bez zmiany wartości; nie oznacza pełnego pokrycia każdej encji HA |
| Nowa sesja sterowania | Usunięcie starego wyniku polecenia po przyjęciu nowej sesji | Osobny test przed/po: nowa sesja wraca do gotowości bez dodatkowego polecenia |
| Dostępność input_button | Niedostępny kafelek nie uruchamia akcji; zmiana dostępności w trakcie przytrzymania unieważnia ten kontakt | Izolowany test urządzenia z obserwatorem usług HA i screenshotami |
| Powrót z ustawień | Opcjonalny powrót do Home po bezczynności, domyślnie wyłączony | Ograniczony test ustawień; rozszerzenie na pozostałe aplikacje jest osobnym zadaniem |
| Podgląd kolorów HA17 | Aktualny akcent z urządzenia, te same role tła i kontrast tekstu co firmware, odświeżenie kolorów bez utraty szkicu/fokusu | Rzeczywiste AEE2FF→CDBBFF→AEE2FF, osiem kolorów CSS zgodnych z metadanymi urządzenia, dwa oryginalne screenshoty i cofnięcie szkicu bez Save |
| Dokumentacja rozwoju | Porównanie trzech projektów, 108 rodzin funkcji, właściciele kodu, zależności i kolejność W00–W26 | To mapa całego zakresu, obejmująca także funkcje istniejące; nie 108 ukończonych nowych funkcji |

Galeria, kamera, player, głos i podstawowa nawigacja są istniejącą bazą projektu;
nie liczymy ich ponownie jako nowych funkcji tej serii. Ich dalsze rozszerzenia
są osobno w planie.

### Co jest przygotowane, ale jeszcze nie wdrożone

**HA18: rozszerzenie dostępności na zwykłe button/scene/script.** Kandydat poza
głównymi źródłami zmienia dwa pliki HA i istniejące testy. Przeszedł 22 testy
dostępności i 301 istniejących testów regresji. Nadal wymaga domknięcia przeglądu,
adopcji/pakietu, wdrożenia i testu na urządzeniu. Przygotowany szkic testu używa
własnej sceny oraz wirtualnego input_boolean; niczego z tego nie utworzono w HA.
HA18 nie działa jeszcze na instalacji użytkownika.

### Kolejność dalszych prac

1. Uzupełnić walidację HA17 jednym porównawczym pomiarem Ustawień po jego
   instalacji. Dzisiejszy pomiar firmware 26 / 31 FPS wykonano jeszcze z HA16.
2. Dokończyć HA18 i jego izolowany test: brak akcji dla zablokowanego/utrzymanego
   kontaktu, jedna nowa akcja po świeżym dotknięciu, następnie dokładne sprzątnięcie.
3. Domknąć wspólną obsługę oczekiwania, błędów i wyniku zwykłych akcji oraz
   pozostałe testy regulatorów: fizyczny dotyk, długie drag/hold, dłuższa praca,
   współbieżność z audio i prawdziwe urządzenia, kiedy będą dostępne.
4. Dodać kolejne kontrolki: wybór opcji, rolety/bramy, wentylator, climate,
   temperatura/RGB/efekty światła, timery, zamki/alarm i automatyzacje.
5. Rozwinąć kompozycję: własne strony i podstrony, kolejność/ukrywanie stron,
   rozmiary kart, pasek strony, zdalna nawigacja i budżety pamięci widżetów.
6. Dodać widoki danych i aplikacje: historia/wykresy, kalendarz, energia, mapy,
   odkurzacz, prognoza pogody, rozszerzenia media_player, kamer i powiadomień.
7. Późniejsze pakiety: harmonogram jasności/tryb nocny, sekwencje wygaszacza,
   instalator i recovery, podgląd host/WASM, katalog aplikacji oraz narzędzia AI.
   Osiem rodzin sprzętowych wymaga osobnych decyzji o sprzęcie/profilu.

Pełna lista wszystkich 108 rodzin i ich ID jest w
[rejestrze funkcji](feature-roadmap-2026-10-24.md), a kolejność i sposób realizacji
w [planie implementacji](implementation-plan-2026-10-24.md). Żadnego z powyższych
otwartych zakresów nie oznaczono jako ukończony na podstawie samego kodu.

### Wydajność i punkt wznowienia

Firmware 26: jeden porównywalny cykl Ustawień — 49 klatek, 31 źródłowych FPS,
średnio 31,296 ms, maksimum 33,067 ms, 0 nieudanych klatek; dsi_under=0 i unsafe=0/0/0.
Po zamknięciu 7482 KiB wolnej PSRAM i 52 KiB pamięci wewnętrznej; bufory
app_work/scroll/close zwolnione. W porównaniu z wersją 25 nie zaobserwowano regresji
w tym scenariuszu. Nie wykonano pełnego długotrwałego testu audio/pamięci ani
osobnego cyklu wydajności po instalacji HA17 przed zatrzymaniem prac.

Kod produktu: `C:\Users\kyvai\atmosfera-echo-hub`; fork:
`C:\Users\kyvai\kyvaith-esphome`. Dowody i kandydaci:
`C:\aeh-build\feature-wave2-20261024`; zachowane źródła/buildy:
`D:\aeh-build\feature-research-20261024`. Oba repozytoria zachowują lokalne zmiany.
Końcowy odbiór HA17: `ha-dev17-root-acceptance-v1.json`, SHA
`c8d33a26260ef8ac0889953493c1dbb2f30b87494d29235f4ae68845ea59603e`.
Żadne dalsze wdrożenia ani testy nie są uruchomione.

## Technical checkpoint

Current accepted checkpoint is native26 with HA17 and clean layout12. Its three
Number locale originals and one Settings comparison have scoped hardware/visual
acceptance. The temporary fixture is removed after its exact five-field inverse
and fresh actual unbound/closed proof. Native25/clean layout10 is the prior clean
reference; native24/layout8 remains the earlier reference. Human Humidity6 and
Light7 positions remain preserved.

## Native26: localized Number display separator

Canonical adoption SHA is
`b4acc82325e0f4094542df1c8fa6349a59ac595bf4a9404e1a838628bcbc9243`;
frozen proposal V2 SHA is
`d2235f0a6fc79638263ca915599b57c0589b4e202bf9e06fe18b1e1eee7a201f`.
Seven existing files change: one native display branch, one product provider,
two language packs and three host test streams. All four runtime files match
the first positively tested candidate exactly. V2 replaces a mirrored test
expectation loop with independent literal pairs. Its affected method passes in
17.415s; the exact parent yields five precise comma assertions in19.850s with
no compiler/harness failure. Three other unchanged positive methods retain
their earlier result; they are not claimed as rerun on V2.

The view owns a transient65-byte display copy and checks the active font's
non-placeholder comma glyph. Wire/owner/index/generation remain canonical;
no new fields, task, image buffer, font asset, define, schema or public setter
is introduced. Existing i18n capacity is332/512 entries. Root preserved all seven
preimages and verified that canonical files do not alias immutable parent25.
Frozen source26 SHA is
`4d19cc55ab09ccd2a7c520098e30ba0740ef5c5558f8f2e2bb2a16dfa8198da2`,
with fork11730/product283 members and only the seven admitted changes. Historical
noncompiled backend/docs in this native map remain inherited; installed HA16
and current canonical docs are separately identified. Generation passes with
source-after verification. Whole generated main SHA is
`b1a23c4ba83d51785b4e6911b595760191eaaf8816c3581a7c8f34f692a7de42`.
Root review SHA `f62c51ab119fd8285a129046acb28093e16f6ab2322c54b139ab9a566153d46e`
accepts exactly one provider-line replacement and two translation additions
after comments/#line removal; all other nonblank code is unchanged. Raw UTF8/LF
and literal/whitespace fidelity are retained. All50 byte-array and28 glyph-array
bodies match25. One local review assertion initially expected five changed lines;
the provider stays on one line, so the actual four-line diff was inspected and
bound exactly before compile. No SDK mutation came from that local review.
Complete compilation passes with the separately bound full-main pin and
source-after verification. The compile log SHA is
`5a17f106a7c9e0332b8374ba70e6e97407ceb9ba545691dfff78b43c2520870a`.
Static RAM remains295544B; reported Flash is7939956B,272B above25. Build marker
is2026-10-25 21:19:39 +0100; full ELF is
`f69bb7698034f29127d984358d10f759d1b0a79cd7cd6bbd9aed81ae5698719a`,
OTA SHA is `1e60e0316d6c6f117fb4687522c6c89686865830ca3f1a60ac3a2dff20fd0d12`.
All14 raw artifacts and the323-header supplemental umbrella are preserved;
context SHA is
`c4bb42cd59642053979c51eac8005414b06ff5e1cb68fca37d724e4ec84de965`.
The exact2304-unit/527-emitted-member input audit passes, SHA
`a285196bbace447d18f4708452bedd2892db29a205e437940ff611015f19b695`.
Only main, build metadata and the Number view compiled inputs changed; defines,
headers, SDK, lock, CRT, assets and glyph bodies retain the parent inputs.
One OTA finishes2026-10-25T20:50:35.197982UTC. Actual full running identity,
60.001678s health and original Home1 pass in report
`3d717742e2c29ef279c84eb82d9de1a2bccdf6ca95a5f5970dc5c39b09099e47`.
Root reviewed the clock and visible rainy-weather original; a still image does
not establish weather motion FPS. Normal controller route1->2->3->4 passes
with18 samples/three released streams, without physical GT911 claims.

The isolated initial0.25 Number fixture uses stable card15 and layout11. No
provider service initializes or changes its value. The actual PL->EN->PL actor
receipt is `7f49340a80c9e53a6ffbd21e0414c1b8183dc4c4f97fe903ebaca8914b0c33cd`.
It records six accepted pointer requests/three openings with distinct grant
tokens, two observed locale writes and one final explicit owned close. There
are zero Number/provider/setup commands or selected semantic state changes;
final selector ispl-PL, preferences unchanged, owner closed, no owned pointer,
no sticky fault and temporary auth revoked. Root's three-original acceptance is
`d338d6d48da461f5b0d2c4041148c32431d143575f96af92e7f2e25b0ec27346`:
PL0,25 with Polish footer, EN0.25 with English footer, then PL0,25 again. First
and restored PL JPEG bytes match exactly; EN differences are confined to the
value/footer bounding rectangle[320,208,480,680]. Existing locale policy closes
the panel before reopening it with the next grant.

One Settings cycle reports49 frames/31 source-rendered FPS/average31296us/
maximum33067us/failed0, dsi_under0 andunsafe0/0/0. Report SHA is
`55bd0c30d61693948d155fe2c6a3717fc0f630fcc15248d9e05857fae2c03223`;
root original/performance acceptance is
`9b22426e6ceb467f22bc88fb8b9e0411ee3e46aa80894c8d43e3f600436e6b78`.
Post-close free PSRAM7482KiB/internal52KiB and app_work/scroll/close0 compare
with25's7486KiB/internal52KiB and31 FPS. JPEG backing varies. This matching
single cycle shows no observed regression; it does not prove heap lifetime,
leak absence, panel FPS, p95, steady CPU, audio or cold-start behavior.
The exact five-field inverse changes11->12, receipt SHA
`e0729145a0de9ca1cf1dd9724c6b45763b51bf1e94cd2e30c87dda78726bc582`.
Fresh actual native full16/current12/unbound/closed proof SHA is
`13ca6ca8263c693437738dd577fa048eb050bbc69c8a8b8161c797796eea343f`.
Exact helper deletion/absence/revocation receipt SHA is
`b02f92f526c068219c1b57cdcc2529bba542ac192ecefae0ae44c0c6e2b9b61d`.
Root reviewed the separate final Home4 original and clean HA browser: saved,
sent and received12, Save/Undo/Redo disabled, Humidity6/Light7 preserved and
W domu restored at15. Clean26 root acceptance SHA is
`e68e46cfdd2446ef9331549fc753acd2e7bbf05e058e535f13a1b97044508f9e`.
The final capture retains post-capture pending masks observationally, separately
from the earlier readonly proof that authorized helper deletion. There is no
physical synthetic-pointer getter; no-owned-pointer evidence derives from the
actual released actor streams, nonpointer Settings cycle and root continuity.

## Earlier native24 / HA16 ordinary input_button checkpoint

Root acceptance `w01-native24-availability-root-acceptance-v1.json`, SHA
`5f1456dd497de5413628034dfa6a7b1186cade5c85e16ffc7facb3216048ae67`,
keeps build, source audit, running identity, HA feedback and visual review as
separate evidence. Source24 is
`b035cf7e75aaed4009f01d6f03f77ef79f1765d9097f2186050fb30d7c00757e`;
preserved context is
`d09f78de2e5ec0f173f27d2c2940d206573cff29a7f51ca0ee94c3c1cb451a7b`;
running ELF is
`c83442e1c176cb35a9c285040c8b4244dfbfa2e95f08594b12216f5274afb68d`,
marker2026-10-25 18:54:07 +0100. The2304-unit/527-member compiler-input audit has
three expected changed compiled units and no unexpected input. One OTA, full
running identity and60.015s Home1 health pass with no unexpected fault, unchanged
five preferences, HUDoff, RAW3 storage and an original Home1 image. The normal
controller route1->2->3->4 uses18 fixed samples/three released streams; final
visible Home4 context is ready after a fixed quiet period. It is not physical
GT911 transport proof.

HA16 acceptance `ha-dev16-root-acceptance-v1.json` has SHA
`ad1f7c910ff8612500f6fe31bf8b276a6dcbb6e2017a0fba4f65271bccc74d89`.
The isolated input_button campaign at revision7 records8 accepted native pointer
requests, two contextual reports, exactly two selected `input_button.press`
services and six observed selected state transitions. Five REST state writes
only set up or change this owned helper; the actor directly calls no HA service.
Unknown-first-press works; disabled contact and availability false->true while
held produce no extra report. A fresh contact recovers. Root reviewed disabled
and enabled originals; the changed bounding box is confined to the target tile
and the header matches native23. Human humidity6/Light7 positions remain.

Actual P4 static layout cost is8B per binding/128B for16, with unchanged surface
size and linker static RAM295544B. `native24-tile-dwarf-sizes-v2.json` records the
preserved ELF layouts; these are not heap/lifetime measurements. Three matching
Settings cycles each render49 frames at31 source-rendered FPS, failed0, averages
31320/31393/31325us and maxima33196/33539/32737us. The two native23 cycles were
also49 frames/31 FPS/failed0. Warm free PSRAM is7475/7479/7476KiB; largest block
4352/2816/4352KiB recovers on the third run, with internal-free52KiB and released
app-work/scroll/close buffers after each close. All three final Home4 originals
are byte-identical to the reviewed enabled original. No scoped regression is
observed; differing warmed weather/snapshot content prevents a cross-firmware
absolute heap-improvement claim. No panel FPS, per-frame p95, steady CPU,
long-duration leak, physical actuator, cold-power-cycle or new audio acceptance
is claimed. Only ordinary input_button availability is covered; other domains'
pending/error/result UX remains open.

Cleanup completed after acceptance: one normal CAS inverse restored only the
five owned fields of card info-20261024-15, advancing layout 7 to 8 while
preserving current user positions and other fields. Native readback confirms
all 16 cards, the restored sensor and removal of its press_enabled flag. The
compiled capability stays at version 1. A separate exact-ID delete removed the
owned input_button definition, state and registry entry; both temporary HA
tokens were revoked. The earlier four QA helpers remain removed.

Inverse receipt SHA: f6dc0ba9f36db337cef0b9c92c9b773248546486abf336746866d0626426293d.
Native unbound proof SHA: 9a8cfb1b44c188302f7ff50f4a06f45fd096beeb6486e095abd938774e9a3e8b.
Deletion receipt SHA: c81e1901d4b525e60c6fc312f1d72d9f3f7ef3dd130b0fa1adad03215687adb9.
The no-held proof derives from the eight accepted pointer requests ending in
release, subsequent non-pointer Settings cycles and root continuity, alongside
a freshly observed closed app/owner with pending command zero. There is no
passive synthetic/physical-contact getter; physical contact absence is not
claimed. The final layout-8 original and the clean HA browser original were
viewed by root: W domu is restored at slot 15, humidity/light remain at 6/7,
labels are readable and HA reports saved/sent/accepted revision 8. Native
capture report SHA is
`7200727832dd17a9d019f990ae6408345ecca48c4de7dc410c250ae49d525608`;
original JPEG SHA is
`27df4d7f1eb46095a7875449a9a969e11eae3fa93f0a4017c12d79afa05d9431`.
The first visual helper invocation failed on a local diagnostic-module import
before target creation; supplying the verified module path allowed the same
operator to perform one wake and 18 capture chunks. No firmware change or
additional input was involved.

## Fresh-GRANT feedback (25): scoped device/performance/cleanup accepted

The canonical fork now resets the cached command result/reason only when a new
GRANT is fully accepted. This is two assignments in the common native owner;
no protocol, YAML, framebuffer, task or HA change is included. Four existing
test files extend the legacy and generic Light/Number regressions. Two focused
methods (five executable cases) pass; the parent produces three precise reset
assertion failures. Renewal, close-cancel, old-token exclusion and existing
expiry/timeout behavior remain covered. Proposal SHA is
`c9b374d3a33eeaeb1907bc6e34c4d46c51ab438b7996a4fa11fb6a7b9d76888b`;
canonical adoption SHA is
`f785fa1ad651f04cd00b67fbc2c590e21aaa331fd6ae1ddb172476345bf4f806`.
Native25 now runs on the device. Its build, running identity, scoped UI
acceptance, one Settings comparison and exact Number fixture cleanup pass.

The native25 source snapshot is now
`05117070864d998b12d2b43d649df1f8dfc465bd388b9452e7a1b40476859625`.
Configuration generation and source-after checks pass; generated main
`4a88af706ec3683b6caa84270b30bbeeace076fefb29e94072dcd8a8d85a0fd5`
equals native24 after comments/#line removal while preserving literals and
remaining whitespace. The complete native build and source-after verification
pass. Static RAM is 295544 bytes and reported Flash is 7939684 bytes, equal to
native24. The preserved context SHA is
`0275fc1fead4a54f8eee59783aaa30edfd02618be010c16ab613de261a94358d`;
ELF is `ae318c846541c185e7f1e867482055d0c0fb098da08776349c3f6bcc32b6c070`,
marker 2026-10-25 20:06:47 +0100. The 2304-unit/527-file audit passes with SHA
`f7a84357566b0499195b4dcea20e24cc7d84148e4297b6c101f5de8b7806bb9a`.
One preserved-image OTA completed. Full running identity, 60.003 uninterrupted
healthy seconds, unchanged observed preferences/HUD-off and the original Home1
weather/clock image pass. The normal Home1->2->3->4 route passed 18 controller
samples and three releases, with no remaining owned controller stream and clear
visible-page pending masks. Unvisited off-window pending slots are not treated
as a failure or as globally ready.

For the before/after campaign, one isolated
`input_number.atmosfera_qa_grant_20261025` is temporarily bound at card 15 in
layout 9 (normal five-field CAS from the accepted layout 8). Its initial state
is 0, range -1..1, step 0.25, unit °C. The provisioning receipt SHA is
`6e50fa411900085d5c621e719374b7c490d451da0d6d80869b06cfcca7670c05`;
the token was revoked and all user card positions retained. Baseline native24
now reproduces stale feedback after a new GRANT: six pointer ACKs, two opens,
two owned closes, one native/provider 0-to0.25 change and zero extra command
after fresh reopen. New open sequence/generation and different close tokens
prove a new selection. The terminal and fresh-reopen originals are byte-exact;
root viewed them. Baseline raw SHA is
`71ad48be6307c98815dcf9a5b7a911c490445f57ad662f5ec4d288ab34b82ad1`;
root baseline acceptance SHA is
`b305461024285fe44644d661d37b23211bcc6205ff001b88fc8c4394dafd1bbb`.

The first partial baseline performed one confirmed change and stopped on its
post-close guard. A later diagnostic retained owner-zero/clear target masks but
overflowed its callback log bound; it is partial evidence. V3 retains guard
samples and uses fixed two-second post-close quiet plus a fresh status read.
It passes the same readiness checks. The original failure did not retain its
exact masks, so its cause remains a timing inference. Both failed artifacts
remain separate; their calls are not hidden in the successful campaign counts.
The same post-flash native25 cycle passes six pointer ACKs, two opens, two owned
closes, exactly one observed provider call and one semantic 0-to0.25 change after
the separately counted zero setup. Its first and fresh reopened statuses are
`ready`, while the actual command still produces `state_matches`. Open sequences,
selection generations and close-token hashes differ; fresh reopening sends no
extra command. Root viewed all three originals: the terminal acknowledgment is
retained after the command and replaced by the normal instruction on a fresh
open. The app ends closed with no owned synthetic pointer, no uncertain
ownership, no sticky fault and a revoked temporary token. Root hardware/visual
receipt SHA is
`80968240c16ef07cf98a4686bcb302b402539fcbdf837420091948252f680d32`.
This accepts the isolated virtual Number flow, not physical GT911, an actuator,
audio, lifetime or panel FPS. The earlier input_button fixture remains removed.

One native25 Settings benchmark completes 48 frames at31 source-rendered FPS,
average31425us/maximum34753us/failed0. Native24 retained49 frames/31FPS/failed0,
average31320/31393/31325us and maximum33196/33539/32737us. The same finite
inertia program can finish a different frame count. Sampled DSI underflow and
unsafe counters remain zero. Post-close PSRAM is7486KiB, largest4352KiB and
internal-free52KiB; app-work/scroll/close buffers are all0. Observed preferences
are unchanged, one open/benchmark/close completed and root reviewed the Home4
original. Root comparison receipt SHA is
`1d1b757164f527fb140a2f6d168d468e3cb64f459e0afe3139daa020602e48b3`.
No scoped regression is observed; one run does not establish lifetime, panel
FPS, CPU or per-frame p95, and varying live content prevents an absolute
heap-improvement claim. An unused v1 operator failed source review because a
callback failure could reach a later dispatch. The v2 pre-dispatch check and
focused negative fake passed before this single actual execution.

The Number fixture inverse passed one normal CAS Save9->10, restoring only its
five owned fields and preserving all current user positions/other edits. Its
receipt SHA is
`25e5da4333219ded38381d7e15e807252c69bee7d42e096bd3a4b25cdb7260ab`.
The post-inverse collector retained full16 revision10 readbacks before/after a
complete original screenshot, with the restored sensor. Its before/after logs
parse to closed app/owner and pending-command0, but it failed a final post-read
guard before retaining the corresponding status. That attempt remains failed;
its exact final status/mask is unknown. Root accepted the original image only.
A separate fresh read-only completion passes current10/full16, two full-ELF
status samples, target mask clear, app/owner closed and pending-command0. It
links the earlier accepted original without claiming a new capture, preserves
the failed collector separately and saves status before each guard. Proof SHA:
`324948e6e357870f28685e83a485655c0c696238d92ecf14837bf1bc71a30a86`.
One exact-ID delete then removes the owned definition/state/registry with
absence readback and revoked token; receipt SHA:
`01dc307a1980c8ad83448353fdcb673f64c47336c27dbbf13eb38a5f177ad725`.
The clean HA editor shows saved/sent/received10, disabled Save/Undo/Redo and the
preserved humidity6/Light7/sensor15 positions. Root viewed its original and the
native original; final checkpoint receipt SHA:
`de688b0f138e8693565d099440db47299c5b62f904b45fd4e773e5c29cb98505`.
No Git commit or publication was performed.

## Earlier native23 / HA15 checkpoint

At the preceding checkpoint the device was native23 with installed HA dev15. The complete build and
2304-unit input audit, one OTA, full running ELF,60-second Home1 observation and
original-image review passed. Polish weather now shows `Pochmurno`; the boot-only
locale correction is verified. The Number panel also passed Polish glyph/unit
review and one owned open/close with zero Number commands. The earlier isolated
Number0→0.25 state-feedback pass remains scoped to native22. Native23 additionally
passed isolated min/max and two signed fractional steps with paired HA feedback.
Two Settings scroll cycles passed at31 source-rendered FPS without failed frames;
physical input, held-state changes, audio and lifetime gates remain open.

The user saved a manual drag-and-drop change as layout revision5: humidity6,
Light7 and the QA Number card15. All16 identities/visibility/control kinds matched
HA/native readback. After testing, one normal inverse Save changed only the six
QA fields and advanced5→6, preserving those user-selected positions; card15 is
again the original home sensor. Revision6 is accepted by the device. The four
exact owned QA fixtures were removed and their states/registry IDs are absent;
all temporary HA refresh tokens were revoked. HA14 was active during these tests. The following
revision4/5 tests retain their historical scope.

HA15 subsequently passed actual eighteen-module container imports, one atomic
source exchange/restart, public24 package parity and retained old24 rollback.
The full selected entry, layout6 and three camera selections remain unchanged.
Its only behavior change removes the Light-only explanation from the Number
inspector. All211 host editor tests pass. Browser review in Polish confirms the
Number-only minus/plus hint and unchanged Light explanation. The three temporary
draft edits were undone; reload confirms disabled Save/Undo/Redo and clean saved6.
Fresh API readback still reports accepted6, generic Light/Number ready, and the
exact versioned JS bytes. The device's full native23 ELF and original Home4
capture pass after HA reconnect. English has host-render tests only. No new
firmware was built for this frontend-only update. Root receipt is
`ha-dev15-root-acceptance-v1.json` (SHA
`936056dd6122bc0ad4bd950b5867f8d7a0fcf0f6698e06ce20dbe985261ed5fa`).

Preceding native21 passed its Power fix checks, five open/close pairs and one
On/already-matched software test with both buttons ready. HA14 source, storage,
rollback, API, asset and read-only browser checks passed. Native20's failed On
test remains the negative control.

User clarification on the resumed day: “Światło 1” is not an available physical
lamp in this installation. Do not request another physical observation or treat
its retained on/raw202 state as actuator evidence. Existing dispatch/timeout
records retain their software scope; the earlier Zigbee route correlation does
not establish a physical outcome. Subsequent positive HA state-feedback tests
must use isolated virtual helpers, without operating household equipment.

Previous native19 checkpoint: five owned open/close pairs, nine cold
readiness observations and original panel visual checks passed. A subsequent
single brightness60 release reached HA exactly once, but provider state stayed
at raw202 and the panel correctly showed `not_confirmed`. Positive state/physical
actuation and broader performance gates remain open. At that checkpoint HA13
ran the shared-session refactor and unused pure numeric-domain module; Number
was not advertised.
The native view-lifecycle extraction is locally adopted and passes its focused
host tests. Its native20 hardware results and the subsequent failed input test
are recorded separately below.

## Native23 locale correction and current layout

Native23 source SHA is
`15b34d0211ec16812f0dee22283bde0045814b8f5db29328f8073cad1da41b2b`;
running ELF SHA is
`bf849a7978dad484d8973ff1a641008712e05e77e58727a5c29eb8471de18236`,
marker `2026-10-25 16:58:02 +0100`. Complete compilation and source-after
verification passed. The direct22 input comparison preserves2304 compilation
units,527 emitted members, existing defines/umbrella/assets, with only main and
build metadata changed. Original Home1 review confirms the restored Polish
weather text; the60-second health observation records no sticky fault and
unchanged diagnostic preferences (receipt SHA
`89f942bb72527bdf037aee8906e6c0e23f4ff346f5dd0a7d188056c16086c997`).

The first Number open stopped before any touch because Home4 contexts were not
prepared after diagnostic page selection. One normal controller4→3→4 route and
quiet preparation made the visible Home4 context ready; no firmware or guard
change was needed. The same admitted open/close scenario then passed, with two
owned tile pointer requests, zero Number commands, an original Polish panel and
an original settled Home4 after one owned close. Root visual acceptance SHA is
`be61ee9db988f59bca40676f9a97f08dbb6c56eb020bc6f697fd859309a1d2b8`
(native receipt `71ae77823ece9a8a463249e743aa6acdecd55dd074776838bdce519dba8aaff5`).
This uses diagnostic LVGL input, not physical GT911, and does not test boundaries.

The first Generic Light campaign stopped before Off: the operator incorrectly
required Scalar quiescence while its live renderer was active. Live Light
requires quiescent0; Number's inactive Scalar requires quiescent1. Zero commands
were sent. The corrected, explicitly retargeted revision5 native campaign has
completed Off→On→brightness60 with three state_matches,12 acknowledged pointer
requests, one open/owned close and four root-reviewed originals. The completed
paired HA observer records exactly three selected services and authoritative
Off/On202/On153 state feedback; its temporary token was revoked without errors.
Both layers prove this isolated virtual-helper sequence, not a physical lamp or
GT911. Root acceptance is `native23-generic-light-root-acceptance-v1.json`.

Number boundary acceptance is separate: two isolated setup calls select1/−1;
disabled Plus-at-max and Minus-at-min contacts emit no command, and two owned
steps reach0.75/−0.75. Exactly10 pointer requests, two native commands, matching
HA service/state feedback, one owned close and five reviewed originals pass.
Both HA tokens were revoked without errors. The receipt is
`native23-number-boundaries-root-acceptance-v1.json`. Held-state/domain changes
and physical GT911 are not covered.

Historical Home1 health runs21/22/23 have no enabled FPS/loop-duration stream, so
there is no historical FPS or frame-p95 baseline. Their final PSRAM-free samples
are4899/4922/4898KiB; internal-free46/45/45KiB and largest blocks4032/4096/3968KiB.
Scalar capacity is unchanged at246912 bytes, including189568 canvas,49152 glyph
reserve,3257 glyph use and8192 worker stack. The23-versus22 free difference is
−24KiB alongside+29KiB of known snapshots; locale and saved contents differ, so
this is not a matched leak or performance verdict.

Two later owned Settings benchmark cycles each render49 frames at31 FPS,
average31257/31306us and maximum33077/33614us, failed0. Sampled DSI underrun and
unsafe counters are0. Free PSRAM is7142→7157→7157KiB. The largest block temporarily
drops4224→2368KiB and recovers to4352KiB on the second cycle; there is no accumulating
free-heap loss across these two cycles. Scalar stays246912B and app-work/scroll/
close buffers are0 after both closes. The first use creates one persistent
static-stack scroll worker (41→42 tasks); the repeat stays42→42. Both restored
Home4 originals are byte-identical and reviewed. Logging flags are restored by
the source-ordered completion lambda, unchanged observed false switches and a
quiet stream; there is no independent raw-flag getter. Root receipt is
`native23-settings-performance-root-acceptance-v1.json`. These are source-render/
submission FPS and window totals/maxima, not panel FPS, historical p95, steady
CPU, audio or long-duration leak proof. No further benchmark was needed.

After all observers ended and a fresh closed/no-held/no-pending proof, one
normal CAS Save restored only the six QA fields by stable card ID, preserving
the user DnD. One fixed readback confirms revision6 and native acceptance6.
Cleanup then removed only the four recorded fixture IDs, with unchanged restored
layout and final state/registry absence checks. No direct source/storage edits, household service calls or inverse actuator
commands were used. Receipts are
`virtual-qa-inverse-save-layout5-actual-v1/layout-operation-receipt.json` and
`virtual-qa-owned-fixtures-layout6-cleanup-actual-v1/public-cleanup-receipt.json`.

## Earlier native21 Power presentation fix: source and host checks

### Subsequent HA14 and Number22 checkpoint

HA14 activation completed at15:07:43UTC with one successful HA restart. A fresh
read proves the installed24 files equal the reviewed package, the retained
rollback22 files equal HA13, and the complete selected config entry, including
data/options, remains unchanged. Layout/catalogue/panel API reads succeeded;
the ephemeral API login was revoked. The versioned editor JavaScript returned
HTTP200 and its exact reviewed hash. The browser showed the connected editor,
saved revision3, live states, profile limitations and existing Light settings;
this browser inspection sent no control or layout-save command.

Native22 compilation completed15:16:54UTC with source-after verification.
Source manifest SHA is
`4ca0a4a417d55877300bad0d9325213479e0d4050b2decf6ddbec932df538fa6`;
compile log SHA is
`10a150201e5b79d4c3d82382392b904392528b43192d59e44331cc9bfff2f4d0`.
ELF SHA is
`b0e495b3b4aa965d5230768753baebd089666003b24f295d0a806941b384318c`.
Linker static RAM is295528 bytes (+608 versus21), flash7938580 (+43184).
The target DWARF sizes are Component7152 (+208), Scalar2696 (unchanged) and
ControlViewLifecycle40 (unchanged). These figures describe static data/object
sizes; they do not prove free heap, leak behavior or runtime performance.
Generated-code review preserved all18 critical setter sets,16 tile bindings,
six pages and all existing byte-array/glyph assets. The2304-unit input audit
passed all13 checks, with no unexpected units. One OTA completed15:38:08UTC;
fresh full ELF/marker and generic Light+Number capability reads passed.
The60.015-second Home1 run has no sticky fault, unchanged five diagnostic
preferences, three raw Home slots/5625KiB and a complete original image.
Controller Home1→4 and Home4→3→4 checks also passed. Health receipt SHA is
`54c63a895e3e85e6e28f9433b45c1c78c7ce895eb2f79e8f4d4946aa50e63214`.

The original image exposed English weather text despite the saved pl-PL select.
Source inspection proves restored select publication at priority800 precedes
bridge setup at395. The early locale script rejects its null backend and never
commits the locale. The23 fix initializes only bounded locale data while boot
is unfinished and the component is not ready. All following runtime
invalidate/drain/navigation/refresh guards remain byte-identical; no buffer,
worker or fork change is involved. Adoption receipt SHA is
`4ae3e63062a65576087ac7ba1a98a31051f51e4b0b47d28790e1320c24c1b7e3`.
Source23 SHA is
`15b34d0211ec16812f0dee22283bde0045814b8f5db29328f8073cad1da41b2b`.

The first Number pilot stopped safely after wake and before any pointer or
command: its diagnostic phase allow-list omitted the actual Home-settle
helper's phase. Its failed record and paired zero-transition observer are
retained; neither is positive Number acceptance. The corrected helper must
preserve the two consecutive settled-Home observations and pass an actual
caller/allow-list integration check before a new independently observed run.

The corrected v2 adds only the two actual Home4 diagnostic phases; the actual
Home-settle helper now passes its caller/allow-list integration check. A new
paired90-second observer and native run passed: exactly four owned pointer
requests produce one Number step, expected index4→5/value0→0.25, then one owned
close to Home4. Native reports state_matches, view_ready1/scalar_ready0,
command_pending0 and no sticky fault. HA records exactly one selected
input_number.set_value(0.25) and one authoritative0→0.25 semantic transition;
the ephemeral token is revoked. Original before/after images preserve title,
unit and both buttons byte-for-byte in decoded pixels; only value/status change.
The browser also shows0,25°C. Root scoped acceptance SHA is
`803771313c9ee557f7d8a82ef7c356829a6f79ad52ddec2f918518bba16fbf47`.
This proves software feedback on the isolated helper, not physical GT911,
an actuator, range boundaries, hold or a broad performance pass.

The local fork adopts exactly four reviewed runtime postimages, with all
preimages retained in `canonical-native21-power-fence-adoption-v1`. Receipt SHA
`8c9c0d1108028ace22474c0eb48f68600286a77b4b543e078e5db2f45126f20a`
binds them to native20. Frozen21 source SHA
`4fdb46e24fa22edffbe1ec133d89bca38b8d9526e6214662787b69e5ce4a35fe`
contains zero compiled product changes, the unchanged HA13 package22 and no
Number/HA14 changes. Generation/configuration validation and full ESP-IDF
compilation passed. Compile ran14:11:18–14:20:07UTC and its source-after check
passed. Subsequent scoped device results are recorded below.

Native21 ELF is
`a38489528fb321a63b311fe6481aa784be8bb7a0384dc7746ec3699bdfae9b5c`,
marker `2026-10-25 15:09:56 +0100`. The fourteen-file preservation manifest SHA
is `9bb602ddc95481f45bcc557daff61d665df86b85d94cefe5e20c8d90d965a84a`.
Generated main has58455 lines and equals20 after only exact source-root
normalization; generated headers and the umbrella match20. Linker static RAM
is294920 bytes (+16) and flash7895396 bytes (+1152). Target DWARF measures
Component6944 (+16), Scalar2696 (unchanged) and lifecycle40 (+8) bytes.
These are static object sizes, not heap or lifetime measurements. The2300-unit
compiler-input audit passed all twelve checks, SHA
`102585016d40447ba420858d1d92553b58ec010b3cbbaf590acd2494641e47f1`.

One OTA completed14:27:42UTC, followed by fresh full-ELF checks and60.007 seconds
without a sticky fault. The original Home1 image is complete; five preferences
and the native wire1/revision3/sixteen-card config stayed equal across capture.
Root health/visual receipt SHA
`b5938e02b6a3927428671be27180e55a79b427f7475a449c06d375f4a91cd7f1`.
Five owned pairs completed in40.608 seconds with nine ready observations.
Original first/last JPEGs both SHA`f4df6450d5a556657867470f84c02235d51d5b1c92ca7669ac136e7455e3bbaf`;
full pixel decoding and original review confirm the complete enabled panel.
Warm/end free PSRAM7119KiB/largest4032KiB/internal54KiB stayed equal. Scalar
named246912B and persistent compositor189568B remain unchanged. Against20,
free PSRAM is6KiB lower, JPEG backing5KiB larger, largest block64KiB smaller;
these are recorded without a causal or broad-performance claim. All observed
DSI first-fatal values were zero. A paired180-second HA observer saw zero
explicit selected-light On/Off/Toggle services. Five-cycle receipt SHA
`e7cc7fc2bd57859f016ce8636c62204e88da2f4d1e05fdee404738799a78db4d`.

The separate owned On test completed13.134 seconds, with one accepted native
turn_on report, one acknowledged release and one owned close. Its fixed cold
post-release sample reports already_matched, no pending command, both controls
ready, and regional request11/selection24 accepted at matching base182. Eight
submitted sources retired accepted, with zero unconfirmed outcomes. This is
software source retirement, not panel ACK or motion latency. Original pixels
changed only inside[280,656,520,680], the bottom status message; all other UI
regions exactly match the accepted original. The complete paired180-second HA
observer confirms zero explicit selected-light services and unchanged on/raw202.
Root software receipt SHA
`f03523544c1266d39d2f5414fe1e707702969e880c1a19bef3cd3d0fa638b826`.
This closes the scoped Power UI/NoOp regression. There is no physical lamp for
this entity per the user, so physical actuation is not claimed. GT911, sustained
drag, full FPS/p95, audio and lifetime acceptance are separate.

Root independently ran all seventeen focused unittest methods (15.552 seconds),
including the unchanged forty Scalar cases and stale-base case37, component,
codec and schema/codegen checks. Real LVGL passed eight explicit state/pressed
flush schedules and eleven cancellation/ownership cases. A separate build with
no ESP32/MIPI/PPA passed two successive power commands and terminal feedback
with zero Scalar loop calls. The root host receipt is
`native21-root-host-validation-v1.json`, SHA
`5fb97eeeaa35283b1c1bbadf1733d335d6f3f32b0c64aaedd351663953b4eafc`.

Five additive portable regression files are now canonical, separately from the
frozen firmware sources. Their actual canonical run passed three pytest tests
and nineteen subtests in171.12 seconds while the firmware compiled. Receipt
`canonical-native21-portable-regression-adoption-v1/test-process-v2.json` SHA
`378729efdac1426db1b41d305f54e94b50730b389756a5b085f99395c10a842c`
retains the first exit4 setup failure: pytest-cov was absent, so the second run
overrode only coverage addopts. Original Scalar tests, including case37, retain
their exact bytes. Public LVGL was freshly built; P4 timing is not inferred.

Frozen19 and20 each reproduce the failure class in all eight explicit host
schedules. This establishes the ordering defect but does not identify the
unlogged origin of actual native20 request7. The fix drains/consumes before
native pressed presentation and resumes from the final current native boundary;
it does not relax stale-base equality, retry a command, allocate a new buffer or
add a task. P4 object sizes, running identity, screenshots, On outcome and
performance remain separate hardware gates.

## Native20 build and On-input failure

The Phase A extraction compiled with zero product C++ changes after exact source
root normalization. The 2300-unit audit passed: only main, build metadata and the
two owning C++ units changed. Five emitted fork files, all generated headers,
SDK settings/dependencies and the deterministically derived umbrella header
matched the admitted source. Fourteen artifacts and the supplemental umbrella
are preserved under `C:/aeh-build/feature-wave2-20261024/native-context-v20`.
One OTA completed; a fresh connection verified full ELF
`7d886813efef301e318fd3cb08a079f84b902d008450a645d3b2c5c5998f7973`
and marker `2026-10-25 13:56:34 +0100`. The 60.010-second health observation and
original Home1 image passed, with five observed switch preferences unchanged.

Target ELF debug information measures component 6896→6928 bytes and Scalar
2708→2696 bytes: pair +20 bytes, bridge32. These are target object sizes, not
heap costs. Linker static RAM is +16 and flash +1376 bytes. No new pixel buffer
or task is introduced by the extraction.

Five cycles completed in 39.631 seconds with nine ready owner/widget observations.
Both originals equal the accepted native19 ready panel byte-for-byte. Warm/end
PSRAM stayed 7125 KiB, largest block4096 KiB, internal54 KiB; the earlier4907 KiB
point retained1792 KiB Weather and is not matched. Prior HA13/native19 warm free
was7117 KiB/largest4224 KiB/internal54 KiB. JPEG backing changed1007→1000 KiB;
the128 KiB smaller largest block is recorded without a causal/performance claim.
The paired180-second observer found zero explicit selected-light services.

The later one-shot On test accepted its four diagnostic pointer requests and
retired release, but received no turn_on report. It stopped without close,
retry, inverse or configuration writes. A separate read-only capture confirmed
both power buttons disabled. The current render7/selection26 completed against
base183 while the owner observed184: accepted0/success0, view_ready0/scalar_ready0.
The matched failure suspends the renderer and cancels captured power input.
Owner/input and stale-base rejection paths predate Phase A; the initiating
render event is unlogged. A coincident STATE update is plausible, not established.
Zero HA services after zero native commands is not an accepted idempotent command.

The failed test stays failed. Existing stale-base test37 must remain fail-closed.
A real-LVGL pressed-style plus STATE reproduction and ownership-boundary fix
are the next gate before Number deployment. The older error feedback surviving
fresh grants is a separate known finding. Physical actuation, sustained input,
audio, FPS/p95 and lifetime gates remain open.

Evidence: `v20-five-cycle-root-acceptance-v1.json`,
`v20-root-health-layout-and-visual-v1.json`,
`v20-single-On-failure-root-assessment-v1.json`, and original images in
`v20-after-failed-On-readonly-v3` under the same evidence root. The first two
read-only probes timed out because the new probe awaited a void API response;
the successful third uses return_response=None. No input action was repeated.

## HA13 deployment and native19 compatibility

The dev13 package passed fourteen imports in the actual HA container before
activation. A single atomic source exchange and restart retained both the old
twenty-file source and a separate source backup. Post-restart verification found
all twenty-two installed hashes equal to the package and canonical source. The
full selected entry, data and options remained equal to the fresh pre-stage
witness: layout v3/revision3/sixteen cards and three selected cameras.

The first API read preceded integration startup and returned unknown_command;
it remains retained. After startup, layout and catalogue APIs and the registered
panel passed. The versioned dev13 editor URL returned HTTP200 with the unchanged
editor JS hash. This is not a new browser interaction acceptance.

On unchanged native19, five owned open/close pairs completed in 41.773 seconds.
All nine fixed cold reads showed view/scalar readiness and enabled On/Off buttons.
Original first/final screenshots showed complete 79-percent panels. They also
expose a separate existing bug: the previous command's not_confirmed feedback
survives a fresh selection. The view-lifecycle refactor does not include that fix.
The paired 180-second observer recorded zero explicit selected-light On/Off/Toggle
calls, unchanged observed state and a revoked temporary token. Three matched
Home4 samples stayed at 7117 KiB free PSRAM, 4224 KiB largest block and 54 KiB
free internal memory. No camera callback was observed. Physical touch/actuation,
sustained dragging, audio, FPS/p95 and lifetime acceptance remain open.

Evidence is in `ha13-native19-root-scoped-acceptance-v1.json` under
`C:/aeh-build/feature-wave2-20261024`; initial startup failure and original JPEGs
are retained alongside the successful observations.

## Native18 identity and Home

The previous one-shot OTA completed at 2026-10-24T22:06:28Z. Today's independent
connection verified MAC `30:ED:A0:E2:0B:CD`, build marker
`2026-10-24 22:30:19 +0200`, and full running ELF
`348fd682dbc88828fa20344fd6155dfc1ff33df9fa2df5bde4f8899328b9cfc6`.
A 60.005-second Home1 observation completed without a sticky fault. Root
reviewed the original 800x800 screenshot: aligned overlapping clock digits,
weather artwork, one-line condition text, accent, microphone and indicators.
This still does not prove animation FPS or physical touch.

The first light pilot correctly refused before any touch or app opening:
Home4's contextual snapshot was not ready. The diagnostic page selector had
not established the page-to-RAW mapping. Three allocated RAW slots and a valid
live screenshot do not establish that mapping. A separately reviewed, fixed
controller-only Home4→3→4 route completed twelve samples and two releases.
After one fixed two-second quiet period, Home4's visible pending mask was zero;
6204 remained pending on the unvisited Security page. No readiness retry or
manual readiness override was used. The original failed pilot stays FAILED.

## Native18 Light readiness failed (retained negative control)

The subsequent pilot completed five owned open/close pairs in 43.476 seconds.
Its nine fixed cold observations and original captures are retained. The first
view was ready. Cycle 2 had a not-ready scalar with still-enabled power buttons;
its retained completion belonged to an older selection, so it does not explain
that cold sample. Cycles 3–5 had matching current completion identities with
`accepted=1`, `success=0`, and recorded current base exactly one greater than
the completed base. The same cold samples show `view_ready=scalar_ready=0`;
both power buttons were disabled. Cycle 5 was already disabled before its screenshot. The retained
tuple records the last current owner decision, not a freshly presented frame
or a physical panel acknowledgement.
Root reviewed the original first view and the independently decoded last view.
Completing five transitions is not readiness acceptance.

This identifies the immediate rejection mechanism. The initiating extra native
frame remains under investigation. Source inspection and a real-LVGL host
reproduction found a compatible delayed-opacity transition mechanism.

Local native19 source adopts a product-owned policy in the existing boot hook,
after persisted settings and before the first application preview. Public
`lv_obj_remove_theme` calls remove only MAIN DEFAULT/PRESSED theme entries from
the two On/Off buttons. Declared styles, 80% pressed opacity, focus and disabled
behavior remain; the inherited extra pressed black recolor35 is intentionally
removed. Generation equality checks, buffers and tasks are unchanged. The
native18 readiness failure remains the retained negative control; native19's
separate results follow below.

Matched settled Home4 warm/end free PSRAM was 7121→7129 KiB, largest block
3072 KiB and free internal memory 54 KiB. Scalar named storage stayed
246912 bytes; the existing global persistent regional copy retained 189568 bytes. The earlier
4911 KiB sample still retained 1792 KiB of Weather, so it is not an equal-retention
comparison. These endpoints do not establish a leak or latency percentile.
Physical GT911 touch, sustained dragging, audio concurrency, animation FPS and
overall memory/lifetime acceptance remain open. These tests also leave the
earlier provider-state and physical-actuation gates open.

## Native19 build, upload and first hardware observations

The complete ESP-IDF build passed. The 2300-unit input audit found only
`src/main.cpp` and generated build metadata changed; emitted fork runtime,
SDK configuration and normalized dependency locks matched native18. All fourteen
artifacts are preserved separately on C. Static RAM increased by sixteen bytes;
this is not a live-memory measurement. Source manifest SHA is
`7593dd6d74e1279f1f0e2dce02d41dd102bdc2b8c27a99850978b31db1c3c30a`;
artifact manifest SHA is
`9bac98bd15542fdab09826e3b47d7248665c0ddf7ef1dd41396970cc3d590da6`.

One OTA completed at 2026-10-25T11:23:18Z. The first API connection timed out
before any native action; its original failed record remains unchanged. A new
observation after a separate reachable TCP check verified full running ELF
`b5cc2239e92e3e6de08c32c006d74b44e8460ffe85694fa0bf230fcb6d3c1a04`
and marker `2026-10-25 11:58:44 +0100`. Its uninterrupted 60.011-second health
window completed, with the five observed Boolean preferences equal before and
after. Root reviewed original Home1 and Home4 screenshots. The same fixed
controller Home4→3→4 route completed twelve samples and two settled legs; the
visible Home4 context mask was clear. Still images do not establish motion or FPS.

The first native19 light pilot stopped at the third close after an unexpected
native report. It completed two validated pairs and observed three opens; all
five collected cold samples had `view_ready=scalar_ready=1` and both buttons
enabled. The original first screenshot shows a complete, active 79% panel.
This is encouraging partial evidence, not five-cycle readiness acceptance.
The original observer omitted the rejected report and assertion text, so its
exact cause is unknown. The guard stopped all later requests; no input remained
held or uncertain. A separate read-only screenshot shows the returned Home4.

The paired HA observer completed 180 seconds with zero explicit selected-light
On/Off/Toggle calls and revoked its temporary refresh token. Its scope excludes
indirect area/device/group-only targets. No reset, generation override, raw
buffer, reusable runtime change or actuator test was added to recover this run.

A separate diagnostic copy added bounded rejection evidence without changing
the strict guard, actions or schedule. It stopped at 11:33:27Z after two opens
and one validated close. The captured rejected service was
`atmosfera_echo_hub.report_camera_source`, a non-event report with empty raw data.
The original observer rejected every non-light service before its protocol
parser could ignore unrelated traffic. Source inspection confirms that the API
broadcasts HA action reports to subscribed clients and that a catalog push may
publish the camera selection while Light is open. This establishes this second
run's harness false positive; the first run's discarded message remains unknown.
The three cold samples collected in this second run were also ready. Its paired
180-second observer again completed with zero explicit selected-light actuator
calls and a revoked temporary refresh token.

The diagnostic stop left the second panel open with no held or uncertain input.
An optional one-close recovery helper was prepared, reviewed and left CLOSED;
it was never admitted or executed. By the later read-only observation, the
normal 300-second inactivity policy had enough time to revoke Light and return
Home before blanking. The original capture and independent Pillow decode show
complete Home4. The capture establishes the current frame; the exact timing
and sleep reason are source-consistent inferences, not a recorded lifecycle
transition. The next pilot must freshly verify Home4 before any contact.

The corrected diagnostic recognises only the exact frozen, passive camera
envelope and records its class/count without source text. Malformed camera,
unknown service, ordinary tile and all invalid Light reports still stop the
campaign. Eight focused pure fixtures cover this seam; actions, schedule,
identity and generation checks did not change. The final fresh pilot completed
five owned open/close pairs in 39.339 seconds, at 11:45:10–11:45:49Z. All nine
fixed observations showed selected/owner/renderer ready, no pending command and
both buttons enabled. Completion IDs 48–52 matched the observed current
selection/request and recorded accepted/success. Their retained base equality
does not imply a current physical acknowledgement; current readiness is
established separately by the explicit owner/widget fields.

Root reviewed the first original and an independent decode of the fifth
original. Both unchanged originals are byte-identical, showing the complete
79% panel with active On/Off controls. All three settled Home4 memory samples
were 7119 KiB free PSRAM, largest block 4224 KiB and free internal 54 KiB.
Scalar named capacity remained 246912 bytes and global persistent regional
capacity 189568 bytes. Native18's comparable warm/end points were 7121/7129 KiB
free, with largest block 3072 KiB and the same internal/named capacities;
JPEG backing differed (1006 versus 1002/995 KiB). These sparse observations do
not establish a lifetime leak or performance percentile. Seventy-one observed
DSI first-fatal/recovery samples were zero. Cumulative renderer counters include
earlier long-open epochs, so no run-local FPS or latency percentile is derived.

The paired 180-second HA observation completed with zero explicit selected-light
On/Off/Toggle calls and confirmed token revocation. Root's scoped readiness,
visual and HA-absence acceptance is
`v19-five-cycle-root-acceptance-v1.json`, SHA
`a5b2c2cfc4ad5c064b287ed0341dc54bd59d64170886db87c1f4784ef5625432`.
The independent data review is `v19-final-pilot-independent-assessment-v1.json`.
This actual final run contained zero camera callbacks; it does not prove live
camera/Light interleaving. The earlier diagnostic's observed camera report and
the pure classifier fixtures remain separate evidence. Physical GT911,
brightness/power actuation, sustained dragging, audio and broad performance
acceptance remain open. Both earlier interrupted pilots retain their original
FAILED status.

Evidence under the existing wave directory:

- `native-context-v19/`, `v19-compiler-input-admission.json`.
- `v19-upload-process.json`, `v19-post-ota-health/` (first failed connection).
- `v19-post-ota-health-after-startup-v1/`, `v19-home1-home4-root-visual-v1.json`.
- `v19-controller-home4-home3-home4/`, `v19-home4-after-normal-navigation/`.
- `v19-five-open-close-after-controller-route-v1/`,
  `v19-first-pilot-root-assessment-v1.json` and its observer-revocation addendum.
- `v19-after-third-close-failure-readonly/`,
  `v19-pilot-ha-light-service-observer-v2.json`.
- `v19-five-cycle-rejection-evidence-investigation-v1/`,
  `v19-rejection-diagnostic-ha-light-service-observer-v2.json`,
  `v19-after-inactivity-readonly/`.
- `v19-five-cycle-camera-classified-v1/`,
  `v19-camera-classified-pilot-ha-light-service-observer-v2.json`,
  `v19-five-cycle-root-acceptance-v1.json`,
  `v19-final-pilot-independent-assessment-v1.json`.

## Native19 single brightness release and unconfirmed outcome

After fresh HA observation of `light.swiatlo_1` on/raw202, one bounded native
gesture requested brightness60. The 27.800-second scenario completed one open,
eight accepted input acknowledgements (tile tap plus six rail samples), one
release-time native command and one owned close/Home4 return, without a sticky
fault, held input, retry or inverse. It retained the panel for fourteen natural
seconds before one fixed outcome read and the original result screenshot.
The same selection45 remained owner/view/scalar-ready, with terminal
`not_confirmed` and `command_pending=0`. Root reviewed the complete before
original and independently decoded after original: authoritative 79% remained,
with the explicit Polish state-not-confirmed message instead of a false success.

The complete paired 180-second HA observer recorded exactly one explicit
`light.turn_on` for this entity with `brightness_pct=60`. Both its endpoint
states and independent fresh REST reads stayed on/raw202 with the original
provider `last_updated`. Dispatch is established; state153 and physical effect
are not. HA's event timestamp and host input ACK are different endpoints/clocks;
their ordering is not a device-release timing or latency measurement.

A bounded backend log window contains a Zigbee2MQTT
`NwkRouteDiscoveryFailed (0xd0)` error for IEEE `a4c1387912fad765`. The selected
entity's current platform is Lightener. A filtered read of its config entry and
matching storage records did not establish the current wrapper-to-IEEE mapping,
so this temporal route-error observation does not by itself prove the command's
physical destination or cause. Native `not_confirmed` alone does not identify
HA service/state timeout versus the native timeout fallback.

Root dispatch/negative-outcome acceptance:
`v19-single60-root-dispatch-and-negative-outcome-acceptance-v1.json`, SHA
`8b2b977a72235fb01d8212029c88772f2c340eda45f8b32d88ba506dd14dc716`.
Evidence remains under `v19-single-brightness60-outcome-v1/`,
`v19-single60-ha-service-observer-v2.json`, the fresh before/after state records,
the filtered backend/binding records and
`v19-single60-independent-assessment-v1.json`. The question about observing the
physical lamp is pending; no answer or physical confirmation was inferred.

## W04 local source preparation, not deployed

The shared HA session extraction is locally adopted in `control_session.py`
and the Light wrapper. Existing wire codec and transport remain unchanged.
The three behavioral Light suites and fifteen JSON fixtures now live under
`tools/tests`, including its portable `fixtures/light_control` directory.
The four outside-workspace AST/baseline proof tests were not added to the repo.
The actual canonical 250-case HA aggregate passed after adoption.

Git applied its configured CRLF line endings, causing the initial raw-byte
comparison with LF proposal copies to fail after applying the patches. All
twenty files were then explicitly checked: universal-newline bytes matched,
five Python ASTs matched and fifteen JSON values matched. The measured canonical
hashes and this initial check remain in
`canonical-w04-shared-session-adoption-v1/receipt-v1.json`; no source change was
silently hidden by a broad normalizer.

The pure `numeric_domain.py` module and twenty-two portable behavioral tests
are also adopted. An initial import-order lint finding in the new test loader
was corrected; all twenty-two cases and Ruff passed. The combined canonical
250+22 aggregate then passed 272 cases. Negative/fractional bounds, exact step
lattices, null/off-grid state, metadata change and lossy service-float conversion
are covered. Independent offline review also exercised 5970 deterministic
domain probes. At this local-adoption checkpoint installed HA12 and running
native19 were unchanged. HA13 deployment is recorded above; no new numeric
control is advertised or accepted.
The positive Light state/physical gate remains open rather than inferred from
this refactor. New protocol, UI, real-HA and hardware validation are subsequent
steps.

## Auto Home functional checks (native18)

Off stayed in settled Settings for 32.084 seconds with 2381 KiB of resident scroll
storage, then returned to Home4 through one normal close. No Number was written.
Idle30 admitted one observed 0→30 change. A completed host lifecycle poll observed
Home after 32.462 seconds from wake dispatch, within the reviewed 30–40-second
host bound. A new independent cleanup connection observed the owned 30, sent 0
once, and confirmed the captured original 0. Display Timeout was observed at 300
before both cases and during fresh cleanup; neither case wrote it. Root reviewed
Settings and the returned Home view; all four before/returned Home JPEGs are
byte-identical to the reviewed original.

The paired 180-second HA observer covered the light pilot and Off, with zero
explicit `light.swiatlo_1` On/Off/Toggle calls and a revoked temporary token.
It excludes indirect area/device/group-only targets and other entities/services.
Idle30 occurred later, outside that observation window; its narrow native
command allow-list is separate evidence. The reports retain initial five
switch values, without establishing their final equality. Host poll timing is
not the exact firmware transition or physical presentation time, physical touch,
scrolling motion or a latency percentile.

## Evidence and image decoder limitation

All current proof is under `C:\aeh-build\feature-wave2-20261024`:

- `v18-post-ota-health/`, `v18-post-ota-health-root-visual-v1.json`.
- `v18-five-open-close-diagnostic/`: original pre-touch refusal.
- `v18-controller-home4-home3-home4/`,
  `v18-controller-roundtrip-root-visual-v1.json`.
- `v18-home4-before-normal-navigation/` and
  `v18-home4-after-normal-navigation/`.
- `v18-five-open-close-after-controller-route-v1/`,
  `v18-pilot-root-readiness-assessment-v1.json`.
- `v18-pilot-after-route-ha-light-service-observer-v2.json`.
- `v18-auto-home-off-v1/`, `v18-auto-home-idle30-v1/`,
  `v18-auto-home-root-functional-visual-v1.json`.

Some original JPEGs appeared partly black in the tool viewer. Complete Pillow
decoding of the unchanged original bytes produced full 800x800 views. Retained
PNG files are independent verification decodes, not edited replacement captures.
The original first/last panel screenshots genuinely differ in button readiness;
the viewer artifact must not be confused with that device failure.
