"""Light platform for PuGoing integration (integration_blueprint).

Dynamic add/remove Lamp entities using DataUpdateCoordinator.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Set

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)
from homeassistant.helpers import entity_registry as er

from .entity import IntegrationBlueprintEntity
from .const import DOMAIN  # 自己集成的域名

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BlueprintDataUpdateCoordinator
    from .data import IntegrationBlueprintConfigEntry

_LOGGER = logging.getLogger(__name__)

# ----------------------------- setup ------------------------------------ #

async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create Light entities for every Lamp device and listen for changes."""
    coordinator: BlueprintDataUpdateCoordinator = entry.runtime_data.coordinator

    known_ids: Set[str] = set()

    def _create_entity(dev: Dict[str, Any]):
        return PuGoingLampLight(coordinator, dev)

    async def _async_add_initial() -> None:
        lamps: List[dict] = coordinator.data.get("devices_by_type", {}).get("Lamp", [])
        entities = []
        for dev in lamps:
            yid = dev["yid"]
            known_ids.add(yid)
            entities.append(_create_entity(dev))
        if entities:
            async_add_entities(entities)
            _LOGGER.info("Added %d initial Lamp entities", len(entities))

    await _async_add_initial()

    # ---------------- listener: add & remove ---------------------------#
    def _handle_lamp_changes() -> None:  # must be sync for coordinator listener
        lamps_now: List[dict] = coordinator.data.get("devices_by_type", {}).get("Lamp", [])
        current_ids: Set[str] = {dev["yid"] for dev in lamps_now}

        # Detect new lamps
        new_ids = current_ids - known_ids
        if new_ids:
            new_entities = [_create_entity(dev) for dev in lamps_now if dev["yid"] in new_ids]
            known_ids.update(new_ids)
            async_add_entities(new_entities)
            _LOGGER.info("Dynamically added %d Lamp entities", len(new_entities))

        # Detect removed lamps
        removed_ids = known_ids - current_ids
        if removed_ids:
            reg = er.async_get(hass)
            for yid in removed_ids:
                unique_id = f"pugoing_lamp_{yid}"
                ent_id = reg.async_get_entity_id("light", DOMAIN, unique_id)
                if ent_id:
                    _LOGGER.info("Removing stale Lamp entity: %s", ent_id)
                    reg.async_remove(ent_id)
            known_ids.difference_update(removed_ids)

    coordinator.async_add_listener(_handle_lamp_changes)


# ----------------------------- entity ----------------------------------- #
class PuGoingLampLight(IntegrationBlueprintEntity, LightEntity):
    """Representation of a single Lamp device."""

    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, coordinator: "BlueprintDataUpdateCoordinator", device: dict[str, Any]):
        super().__init__(coordinator)
        self._device_id = device["yid"]
        self._device_sn = device.get("sn", self._device_id)
        self._attr_unique_id = f"pugoing_lamp_{self._device_id}"
        self._attr_name = device.get("dname", "Lamp")
        self._state: bool = self._parse_state(device)

    # ---------- helpers ---------- #
    @staticmethod
    def _parse_state(device: dict[str, Any]) -> bool:
        return str(device.get("dinfo", "")).startswith("开")

    def _latest(self) -> dict[str, Any] | None:
        for dev in self.coordinator.data.get("devices_by_type", {}).get("Lamp", []):
            if dev["yid"] == self._device_id:
                return dev
        return None

    # ---------- required props ----- #
    @property
    def is_on(self) -> bool:
        latest = self._latest()
        if latest is not None:
            self._state = self._parse_state(latest)
        return self._state

    @property
    def available(self) -> bool:
        return self._latest() is not None

    # ---------- control ------------ #
    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
            self._device_id, on=True, sn=self._device_sn
        )
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
            self._device_id, on=False, sn=self._device_sn
        )
        self._state = False
        self.async_write_ha_state()

    # ---------- extra attrs -------- #
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        dev = self._latest()
        if dev is None:
            return None
        return {
            "sn": dev.get("sn"),
            "panel": dev.get("dpanel"),
            "room": dev.get("dloca"),
            "online": dev.get("online"),
        }
