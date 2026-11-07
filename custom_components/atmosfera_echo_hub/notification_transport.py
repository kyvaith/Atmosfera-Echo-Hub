"""Notification transport on the existing ESPHome connection, never a new socket."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, replace
from time import monotonic
from uuid import uuid4

from aioesphomeapi import APIConnectionError
from homeassistant.exceptions import HomeAssistantError

from .light_control_transport import authorize_ha_context
from .notification_history import CAPACITY, NotificationHistory, decode_request

DOORBELL_ACTION_SECONDS = 180


@dataclass(frozen=True, slots=True)
class DoorbellNotice:
    notice_id: str
    camera: str
    duration: int
    expires: float
    opened: bool = False


class NotificationTransport:
    def __init__(self, bridge):
        self.bridge = bridge
        self.history = NotificationHistory()
        self.store = None
        self.channel = ""
        self.sequence = 0
        self.offset = 0
        self.epoch = -1
        self.lock = asyncio.Lock()
        self.doorbells: dict[str, DoorbellNotice] = {}

    async def setup(self):
        from homeassistant.helpers.storage import Store

        self.store = Store(
            self.bridge.hass, 1, f"atmosfera_notifications.{self.bridge.entry.entry_id}"
        )
        self.history.load(await self.store.async_load())

    async def save(self):
        if self.store is not None:
            await self.store.async_save(self.history.dump())

    async def push(self, *, detail=None):
        runtime = self.bridge.esphome_entry.runtime_data
        for version, name in (
            (3, "notification_sync_v3"),
            (2, "notification_sync_v2"),
            (1, "notification_sync"),
        ):
            action = self.bridge._find_api_action(name)
            if action is not None:
                break
        if not self.bridge.tile_device_available or action is None:
            return False
        if self.epoch != self.bridge._connection_epoch:
            self.epoch = self.bridge._connection_epoch
            self.channel = uuid4().hex
            self.sequence = 0
            self.offset = 0
        data = {
            "v": version,
            "channel": self.channel,
            "seq": self.sequence,
            **self.history.page(self.offset, version=version),
            "detail": detail,
            "language": self.language(),
        }
        self.offset = data["offset"]
        await runtime.client.execute_service(
            action,
            {"payload": json.dumps(data, ensure_ascii=False, separators=(",", ":"))},
        )
        return True

    def language(self):
        return (
            "pl"
            if (
                self.bridge.device_locale or self.bridge.hass.config.language
            ).startswith("pl")
            else "en"
        )

    def supports_actions(self):
        return self.bridge._find_api_action("notification_sync_v3") is not None

    def _prune_doorbells(self):
        now = monotonic()
        self.doorbells = {
            event: record
            for event, record in self.doorbells.items()
            if record.expires > now
        }

    async def has_doorbell(self, event_id):
        async with self.lock:
            self._prune_doorbells()
            return event_id in self.doorbells

    async def add_doorbell(self, camera, duration, event_id):
        async with self.lock:
            self._prune_doorbells()
            if event_id in self.doorbells:
                return "duplicate"
            title, message = (
                ("Wideodzwonek", "Ktoś dzwoni do drzwi.")
                if self.language() == "pl"
                else ("Video doorbell", "Someone is at the door.")
            )
            record = self.history.add(title, message)
            await self.save()
            if len(self.doorbells) == CAPACITY:
                del self.doorbells[next(iter(self.doorbells))]
            self.doorbells[event_id] = DoorbellNotice(
                record.id, camera, duration, monotonic() + DOORBELL_ACTION_SECONDS
            )
            try:
                await self.push()
                banner = self.bridge._find_api_action("notification_show_passive")
                if banner is not None:
                    await self.bridge.esphome_entry.runtime_data.client.execute_service(
                        banner, {"title": title, "message": message}
                    )
            except (HomeAssistantError, APIConnectionError, TimeoutError):
                pass
            return "notification_saved"

    async def add(self, title, message):
        async with self.lock:
            self.history.add(title, message)
            await (
                self.save()
            )  # Preserve a notice even if the connection drops during delivery.
            try:
                await self.push()
            except (HomeAssistantError, APIConnectionError, TimeoutError):
                pass

    async def report(self, data, context):
        # Permission is checked against this device's actual notify entity.
        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(self.bridge.hass)
        entity_id = registry.async_get_entity_id(
            "notify",
            "atmosfera_echo_hub",
            f"{self.bridge.device_id}_display_notifications",
        )
        if entity_id is None or not await authorize_ha_context(
            self.bridge.hass, context, entity_id
        ):
            return
        async with self.lock:
            if (
                not self.bridge.tile_device_available
                or self.epoch != self.bridge._connection_epoch
                or data["channel"] != self.channel
                or data["seq"] <= self.sequence
                or (data["v"] == 3 and not self.supports_actions())
            ):
                return
            self.sequence = data["seq"]
            self.offset = data["offset"]
            detail = None
            if data["op"] == "dismiss":
                self.history.dismiss(data["id"])
                await self.save()
            elif data["op"] == "open":
                detail = self.history.detail(data["id"])
            if data["v"] == 3 and data["op"] in ("open", "activate"):
                self._prune_doorbells()
                doorbell = next(
                    (
                        (event, record)
                        for event, record in self.doorbells.items()
                        if record.notice_id == data["id"] and not record.opened
                    ),
                    None,
                )
                if doorbell is not None and (
                    detail is not None or self.history.detail(data["id"]) is not None
                ):
                    event_id, record = doorbell
                    if (
                        await authorize_ha_context(
                            self.bridge.hass, context, record.camera
                        )
                        and record.camera in self.bridge.camera_entity_ids
                        and self.epoch == self.bridge._connection_epoch
                    ):
                        remaining = int(record.expires - monotonic())
                        if remaining > 0 and detail is not None:
                            detail["action"] = {
                                "type": "camera_preview",
                                "remaining": remaining,
                            }
                        elif remaining > 0:
                            status = await self.bridge.async_request_camera_preview(
                                record.camera,
                                record.duration,
                                event_id,
                                expires=record.expires,
                            )
                            if status in ("opened", "duplicate"):
                                self.doorbells[event_id] = replace(record, opened=True)
            await self.push(detail=detail)


async def async_route_notification(hass, node_name, payload, context):
    try:
        data = decode_request(payload)
    except (ValueError, TypeError):
        return
    matches = [
        e.runtime_data
        for e in hass.config_entries.async_loaded_entries("atmosfera_echo_hub")
        if e.runtime_data.node_name == node_name
        and e.runtime_data._notifications.channel == data["channel"]
    ]
    if len(matches) == 1:
        await matches[0]._notifications.report(data, context)
