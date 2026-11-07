# MQTT Vacuum: nieopublikowana zmiana CLEAN_AREA w Core2026.7.1

Obserwacja podczas testów HA76, bez zmian w Core i bez publikacji upstream.
Nie ustalono tutaj, czy nowszy Home Assistant ma już poprawkę.

Po usunięciu clean_segments_command_topic discovery poprawnie odejmuje
CLEAN_AREA od stanu encji. Po ponownym dodaniu topic i JSON segments, gdy
aktywność/fan_speed/bateria nie zmieniają się, wewnętrzny provider ma już
możliwość sprzątania obszaru, ale zapis w hass.states nadal jej nie pokazuje.

Własna fixture w AreaV4 potwierdziła jednocześnie:

- publiczny vacuum/get_segments zwraca success i prawidłowe segmenty;
- opublikowane State.attributes.supported_features wynosi13852, bez16384;
- po rzeczywistej zmianie aktywności testowego providera na idle, a następnie
  paused, opublikowane flags wynoszą30236 i Atmosfera odblokowuje akcję.

Oryginalny dowód:
`C:/aeh-build/feature-continuation-20261031-next/vacuum-area-v4/core-provider-feature-only-proof.json`.
AreaV2/V3 zachowują wcześniejsze nieudane próby przywrócenia wyłącznie flagi,
z kompletnym odwróceniem ich zmian. Nie są zaliczone jako pełne kampanie.

Pinowany MQTT vacuum.py (SHA26f458353136e5cadd2d6807af5921954bc4999e3a5101a2203d0eece334b68a)
zmienia _attr_supported_features w _state_message_received, ale jego
_prepare_subscribe_topics monitoruje tylko _attr_battery_level,
_attr_fan_speed i _attr_activity. MQTT entity.py
(SHA2b4091a203bf4d3e8b2d3b79d75fd072ed36beffd49b5114438f3206655b4ba6)
w _message_callback zleca publikację tylko po zmianie jednego z monitorowanych
pól, o ile force_update nie jest włączone. Z kolei vacuum/get_segments w
vacuum/websocket.py sprawdza wewnętrzne supported_features providera.

Możliwa poprawka upstream to dodanie _attr_supported_features do zbioru
monitorowanych atrybutów subskrypcji Vacuum i test regresji feature-only.
To propozycja wymagająca osobnych testów HA, nie wdrożony patch. Źródła
zachowano w W2/installed-vacuum-area-support-source.json oraz
installed-mqtt-subscription-support-source.json.

Atmosfera nadal używa opublikowanego hass.states jako autorytetu, więc przy
niezgłoszonej capability nie wysyła ruchu. Nie dodano wywołań prywatnych
providerów, wymuszania flags lub fikcyjnego feedback. Własna fixture V4
przechodzi prawdziwą zmianę aktywności przed próbą odblokowania akcji.
