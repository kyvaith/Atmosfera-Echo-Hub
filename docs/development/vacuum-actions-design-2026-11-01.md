# Jawne akcje odkurzacza — HA74

Zakres CTL014/W19: standardowe akcje na istniejącym kafelku, bez nowego ekranu,
taska, timera, protokołu ani bufora firmware. Native45 pozostaje niezmieniony.
Core/provider jest właścicielem możliwości i zaobserwowanego stanu. Integracja
HA sprawdza politykę przy projekcji i ponownie przy wykonaniu. Istniejące
generacje press_enabled, dotyk i kontroler snapshotów zarządzają prezentacją.

Każdy kafelek ma jedno jawnie wybrane polecenie. Nowa karta jest pasywna.
Przyciski w edytorze modyfikują wyłącznie szkic, z Undo/Redo i osobnym Zapisz.
Obsługiwane możliwości konfiguracji nie są tym samym co aktualna możliwość
wykonania. Pauzę można skonfigurować w bazie, ale wtedy urządzenie jej nie wykona.

| Akcja | Dopuszczalny zaobserwowany stan |
| --- | --- |
| start (także wznowienie) | docked, idle, paused |
| pause | cleaning, returning |
| stop | cleaning, paused, returning |
| return_to_base | cleaning, idle, paused |
| locate | wszystkie sześć znanych aktywności, także error |
| clean_spot | docked, idle, paused |

To jawna polityka produktu, nie gwarancja fizycznej reakcji każdego dostawcy.
Nieznany/niedostępny stan, brak rzeczywistej flagi lub usługi blokują wykonanie.
Core IntFlag jest poprawny; bool, ujemne lub niebezpiecznie duże wartości nie.
TURN_ON/TURN_OFF nie zastępują START. Wybór mocy z HA65 zachowuje własny kontrakt.
Powrót do bazy nie oznacza zadokowania, a wysłanie polecenia nie zmienia napisu
na kafelku: potrzebne jest potwierdzenie od dostawcy.

PL/EN korzystają z tłumaczeń HA i pakietu brakujących etykiet. Wbudowany angielski
Error w polskich zasobach ma fallback Błąd; specyficzna translacja encji wygrywa.
Przyciski używają zawijanych opcji z zaznaczeniem i palety istniejącego edytora.
Wybór akcji zachowuje scroll inspektora. Brak zmian w rendererze urządzenia.

Źródło faktycznie zainstalowanego Core2026.7.1 ponownie sprawdzono 1 listopada:
vacuum/__init__.py SHA3ef93e4f71dd1d538cf3a1c8c60591318f1c6408c1c50b93ed2fbefd3131c9f6,
mqtt/vacuum.py SHA26f458353136e5cadd2d6807af5921954bc4999e3a5101a2203d0eece334b68a.
Piny i odczyt tłumaczeń: W2/installed-vacuum-source-20261101.json oraz
vacuum-action-label-preflight.json. API MQTT wysyła dokładny payload polecenia
na command_topic i czeka na stan JSON. Test używa wyłącznie własnej encji MQTT.
Mapy, clean_area i komendy dostawców są odrębnym etapem z rzeczywistym mapowaniem
segmentów do HA areas; nie zgadujemy identyfikatorów pomieszczeń.

Wymagany odbiór: testy polityki/adaptera/edytora, instalacja z pinami i zachowaniem
układu, realny browser wybór/Undo/noSave, rzeczywiste dotknięcia urządzenia,
dokładne komendy HA i MQTT przed feedback, utrata capabilities/outage/error,
held-ABA, drag cancel, PL/EN, oryginały screenshotów, pomiar i odwrócenie tylko
własnych zmian. Fizyczny odkurzacz pozostaje osobnym testem.

Źródła: [Vacuum](https://www.home-assistant.io/integrations/vacuum/),
[MQTT Vacuum](https://www.home-assistant.io/integrations/vacuum.mqtt/).
