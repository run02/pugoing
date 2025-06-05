"""Light platform for PuGoing integration (integration_blueprint).

This file maps devices of type **Lamp** returned by the DataUpdateCoordinator
into Home Assistant `light` entities.

Assumptions
-----------
* `coordinator.data["devices_by_type"]["Lamp"]` is a list of **dict** objects
  exactly matching the payload you provided earlier.
* The API client (`IntegrationBlueprintApiClient`) exposes an
  `async_set_lamp_state(device_id: str, *, on: bool, brightness: int | None = None) -> None`
  coroutine that actually sends the control command.  If it does not exist yet,
  add a stub with the appropriate REST/WebSocket call – see the TODO.

If your real device model differs (for example, dimmable or coloured lamps),
expand the entity below accordingly (e.g. add `supported_color_modes`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)

from .entity import IntegrationBlueprintEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BlueprintDataUpdateCoordinator
    from .data import IntegrationBlueprintConfigEntry


# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
known_ids: set[str] = set()

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data.coordinator
    known_ids.update(dev["yid"] for dev in coordinator.data["devices_by_type"].get("Lamp", []))

    # 初次添加实体
    entities = [PuGoingLampLight(coordinator, dev) for dev in coordinator.data["devices_by_type"]["Lamp"]]
    async_add_entities(entities)

    # 监听 coordinator 数据更新，增量添加新设备
    async def _async_new_lamps():
        new_entities = []
        for dev in coordinator.data["devices_by_type"].get("Lamp", []):
            if dev["yid"] not in known_ids:
                known_ids.add(dev["yid"])
                new_entities.append(PuGoingLampLight(coordinator, dev))

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_new_lamps)



# -----------------------------------------------------------------------------
# Entity implementation
# -----------------------------------------------------------------------------
class PuGoingLampLight(IntegrationBlueprintEntity, LightEntity):
    """Representation of a single Lamp device."""

    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(
        self, coordinator: "BlueprintDataUpdateCoordinator", device: dict[str, Any]
    ) -> None:
        super().__init__(coordinator)

        self._device_id: str = device["yid"]  # Unique within the cloud
        self._device_sn: str = device.get("sn", self._device_id)
        self._device_name: str = device.get("dname", "Lamp")
        self._attr_unique_id = f"pugoing_lamp_{self._device_id}"
        self._attr_name = self._device_name
        self._state: bool = self._parse_state(device)

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    @staticmethod
    def _parse_state(device: dict[str, Any]) -> bool:
        """Return True if the lamp is currently reported as ON."""
        return str(device.get("dinfo", "")).startswith("开")

    def _current_device_dict(self) -> dict[str, Any] | None:
        """Return the latest dict for this device from coordinator.data."""
        for dev in self.coordinator.data.get("devices_by_type", {}).get("Lamp", []):
            if dev["yid"] == self._device_id:
                return dev
        return None

    # ---------------------------------------------------------------------
    # Home-Assistant required properties
    # ---------------------------------------------------------------------
    @property
    def is_on(self) -> bool:
        """Return True if light is on."""
        dev = self._current_device_dict()
        if dev is not None:
            self._state = self._parse_state(dev)
        return self._state

    @property
    def available(self) -> bool:
        """Entity is available only if device still shows up in the cloud list."""
        return self._current_device_dict() is not None

    # ---------------------------------------------------------------------
    # Control methods
    # ---------------------------------------------------------------------
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the lamp on (optionally with brightness)."""
        await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
            self._device_id, on=True, sn=self._device_sn
        )
        self._state = True  # 临时更新
        # self.async_write_ha_state()
        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the lamp off."""
        await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
            self._device_id, on=False, sn=self._device_sn
        )
        self._state = False  # 临时更新
        # self.async_write_ha_state()
        # await self.coordinator.async_request_refresh()

    # ---------------------------------------------------------------------
    # Extra attributes (optional, shown under «Device Info»)
    # ---------------------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        dev = self._current_device_dict()
        if dev is None:
            return None
        return {
            "sn": dev.get("sn"),
            "panel": dev.get("dpanel"),
            "room": dev.get("dloca"),
            "online": dev.get("online"),
        }
