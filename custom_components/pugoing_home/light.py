"""Light platform for PuGoing integration (integration_blueprint).

Dynamic add/remove Lamp entities using DataUpdateCoordinator.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Set

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from .entity import IntegrationBlueprintEntity
from .const import DOMAIN, LAMP_STATE_DEBOUNCE_SECONDS
from .pugoing_api.error import PuGoingAPIError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BlueprintDataUpdateCoordinator
    from .data import IntegrationBlueprintConfigEntry

_LOGGER = logging.getLogger(__name__)
from homeassistant.helpers import (            # ★ 新增
    device_registry as dr,                     # ★
    area_registry as ar,                       # ★
)

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
        self._last_manual_control: datetime | None = None

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
        if self._last_manual_control:
            if datetime.now() - self._last_manual_control < timedelta(seconds=LAMP_STATE_DEBOUNCE_SECONDS):
                return self._state

        latest = self._latest()
        if latest is not None:
            self._state = self._parse_state(latest)
        return self._state

    @property
    def available(self) -> bool:
        return self._latest() is not None

    # ---------- control ------------ #
    async def async_turn_on(self, **kwargs: Any) -> None:
        try:
            await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
                self._device_id, on=True, sn=self._device_sn
            )
            self._state = True
            self._last_manual_control = datetime.now()
            self.async_write_ha_state()
        except PuGoingAPIError as e:
            _LOGGER.warning("Failed to turn on lamp %s: %s", self._device_id, e)

    async def async_turn_off(self, **kwargs: Any) -> None:
        try:
            await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
                self._device_id, on=False, sn=self._device_sn
            )
            self._state = False
            self._last_manual_control = datetime.now()
            self.async_write_ha_state()
        except PuGoingAPIError as e:
            _LOGGER.warning("Failed to turn off lamp %s: %s", self._device_id, e)

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
        
    @property
    def device_info(self) -> DeviceInfo:
        """让每盏灯各自成为一个设备。"""
        dev = self._latest() or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},            # ← 唯一
            name=dev.get("dname") or f"Lamp {self._device_id}", # 避免 undefined
            manufacturer="PuGoing",
            model=dev.get("dpanel", "Lamp"),
            # sw_version=dev.get("fw", ""),                       # 有的话
            # via_device=(DOMAIN, "pugoing_gateway"),             # 如果你有网关，可留空
            # suggested_area   =dev.get("dloca") or None,   # 👈 这里
            # configuration_url=f"http://47.123.5.29:18021/",
        )
     # ---------- HA 回调：实体已加入 ---------------- #
    async def async_added_to_hass(self) -> None:        # ★ 新增
        """实体注册完成后，自动把设备归到对应区域。"""
        await super().async_added_to_hass()             # 保留父类逻辑

        area_name = (self._latest() or {}).get("dloca") # ① 取 API 里的房间名
        if not area_name:
            return

        # ② 取 / 创建 Area
        area_reg = ar.async_get(self.hass)
        area     = area_reg.async_get_area_by_name(area_name)
        if area is None:
            area = area_reg.async_create(area_name)

        # ③ 更新设备的 area_id
        dev_reg  = dr.async_get(self.hass)
        device   = dev_reg.async_get_device({(DOMAIN, self._device_id)})
        if device and device.area_id != area.id:
            dev_reg.async_update_device(device.id, area_id=area.id)

