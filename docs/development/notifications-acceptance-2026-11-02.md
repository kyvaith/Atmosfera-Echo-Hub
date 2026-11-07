# Odbiór powiadomień i ikon — 2 listopada 2026

**Na urządzeniu: native49, integracja HA0.4.0.dev95, układ298.**
Pakiet obejmuje górny baner, centrum historii i semantyczne ikony robota/kosiarki.
Typowane akcje oraz obrazy w powiadomieniach pozostają do dodania.

## Działające funkcje

- HA przechowuje do100 wpisów przez24 godziny, z trwałym ID i kolejnością od
  najnowszych. Urządzenie ponownie używa8 wierszy i pobiera dalsze strony.
- Gest od górnej krawędzi otwiera centrum. Tap otwiera pełny tekst, przesunięcie
  w bok usuwa konkretny wpis. Zmiana wiersza podczas kontaktu nie otwiera
  zastępczego wpisu. Zamknięcie nie wywołuje usługi domowego urządzenia.
- Są polskie i angielskie napisy, akcent użytkownika, pastelowe powierzchnie
  i kontrast tekstu. Długie szczegóły przewijają się; powrót ukrywa cały ich viewport.
- Właściwe ikony MDI robota odkurzającego i kosiarki działają w edytorze HA,
  domyślnych ikonach nowych kart oraz subsetach fontów firmware. Rzeczywiste
  zrzuty potwierdzają rozmiary36/44/68. Wybrane wcześniej ikony użytkownika zachowano.

Wywołanie przez rzeczywiście sprawdzony cel HA:

```yaml
action: notify.send_message
target:
  entity_id: notify.atmosfera_echo_hub_display_notifications
data:
  title: Dom
  message: Przykładowa wiadomość
```

## Pamięć i własność ekranu

Wersja47 ujawniła fragmentację w Asystencie:6038KiB wolne, lecz największy blok
1824KiB nie mieścił1875KiB ciągłego tła. Bezpiecznie odmawiała otwarcia.
Końcowy komponent ma8 wyrównanych pasów po240000B, razem1920000B wyłącznie
podczas nakładki. Odtwarza je przez PPA do jednego wolnego DSI lease i prezentuje
kompletną klatkę. Nie dodaje zadania ani stałego pełnoekranowego bufora.
Po zamknięciu:0 pasów /0 bajtów. Obowiązuje [kontrakt komponentu](../architecture/notifications.md).

Baner i centrum wracają do Kamery, Galerii, Ustawień i wizualnego Asystenta.
Na końcowym49 ponownie sprawdzono Kamerę i Asystenta; licznik prezentacji Kamery
79→143, odczyt12,9 FPS. Jest to prezentacja strumienia, nie tylko licznik dekodera.

## Wyniki testów

- 810 testów Python,3 pominięte;397 testów Node bez błędów.
- 13 scenariuszy z rzeczywistym LVGL na hoście, obejmujących gesty, fragmentację,
  nieudany drain/restore, zmianę generacji, locale i list/detail/back.
- Pełny build natywny i OTA końcowej49: PASS.533 wygenerowane pliki /207 jednostek
  ESPHome zgodnych z zamrożonym źródłem;11959 wspólnych plików bibliotek i lock
  niezmienione.41 plików canonical=frozen=installed HA95.
- 10 scenariuszy Home48;7 scenariuszy współbieżności48; osobny odbiór trwałości
  i powtarzalnego zwalniania48;4 skupione scenariusze końcowej49.49 oryginalnych
  zrzutów800×800 zweryfikowano rozmiarem i hashem w zbiorczym odbiorze.
- Przeładowanie integracji zachowało32 dokładne, uporządkowane rekordy. Wyczyszczono
  wyłącznie35 własnych ID testowych (poza dwoma usuniętymi wcześniej gestem).
  Archiwum na końcu puste; brak zmian opcji/danych HA,16 kart i3 kamery.
- Przywrócono wszystkie8 preferencji i testowe nadpisania ikon. Finalnie Home1,
  brak aktywnej nakładki, kontaktu QA i tymczasowego tła.

## Porównywalna trasa wydajności

Home1→Home2 rzeczywistym listenerem LVGL, Ustawienia/przewijanie, zamknięcie
doHome2 i powrót doHome1. FPS dotyczy źródła kompozytora, nie panelu.

| Pomiar | native46 przed | native49 po |
| --- | ---: | ---: |
| Średni czas kompozycji |16,552ms|16,358ms|
| Maksymalny czas |25,273ms|23,782ms|
| Source FPS |55|54|
| Nieudane klatki |0|0|
| DSI underrun / recovery |0 /0|0 /0|
| Wolna PSRAM po trasie |4882KiB|4858KiB|
| Największy blok |2016KiB|2112KiB|
| Wolna pamięć wewnętrzna |31KiB|30KiB|

Koszt końcowego porównywalnego stanu wynosi24KiB PSRAM i około1KiB pamięci
wewnętrznej. Po rozgrzanych aplikacjach oraz zmianach locale/akcentu odnotowano
osobno4260KiB PSRAM i22KiB wewnętrznej, Gallery pool=NO/2 segmenty Ustawień.
Nie porównano tego bezpośrednio ze stanem bazowym pool=YES. Kontrolowany restart
programowy i sprawdzona gotowość wejścia przywróciły zgodny stan pool=YES/1 segment.
To nie test fizycznego odłączenia zasilania ani dowód przyczyny wszystkich zmian cache.

## Screenshoty i dowody

Katalog dowodów: `C:/aeh-build/notification-center-20261102`.

- [Historia8 wierszy (48)](C:/aeh-build/notification-center-20261102/notification-campaign-v48-home/history-page1-original.jpg)
- [Lista po długich szczegółach (49)](C:/aeh-build/notification-center-20261102/notification-campaign-v49-focused/list-after-long-detail-original.jpg)
- [Pusta historia bez starego scrollbara (49)](C:/aeh-build/notification-center-20261102/notification-campaign-v49-focused/empty-after-long-detail-original.jpg)
- [Angielski i fioletowy akcent (49)](C:/aeh-build/notification-center-20261102/native49-visual-icons-locale/empty-english-purple-original.jpg)
- [Kosiarka68/44 — tymczasowy test fontu (49)](C:/aeh-build/notification-center-20261102/native49-glyphs/mower-page2-original.jpg)
- [Odkurzacz36 — tymczasowy test fontu (49)](C:/aeh-build/notification-center-20261102/native49-glyphs/vacuum-page4-original.jpg)
- [Końcowy Home (49)](C:/aeh-build/notification-center-20261102/native49-cold-performance-r2/home-real-input-after-original.jpg)

Zbiorczy receipt: `native49-ha95-notification-acceptance.json`. Zachowano również
nieudane próby QA: idle WebSocket48, wyścig tymczasowej ikony z autorytatywnym
odświeżeniem HA oraz odrzucony kontakt przed gotowością boot. Poprawione, ograniczone
scenariusze są zapisane osobno. Fixture host49 wymagał uzupełnienia istniejącego
pola `created`; r8 bada identyczny kod runtime49 z poprawioną fiksturą.

Pełny ELF49: `75f08dc16ccf452ded9cfd61928ce6f0d3a9d9dce01d9a46f9e3b0633dd59a28`.
Artefakt: `C:/aeh-build/native-context-v49`, marker `2026-11-02 15:13:37 +0100`.

Nie badano fizycznej latencji GT911, pełnej rozmowy/audio, pracy kotła, ruchu
robota/kosiarki ani zimnych startów po odłączeniu zasilania. Nie zmieniono
partycji, układu HA ani źródeł kamer. Nie wykonano Git stage/commit/push.
Następny pakiet: [termostat](thermostat-contract-2026-11-02.md).
