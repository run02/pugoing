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
async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationBlueprintConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create Light entities for every Lamp device."""
    coordinator: BlueprintDataUpdateCoordinator = entry.runtime_data.coordinator

    lamp_devices: list[dict[str, Any]] = coordinator.data.get("devices_by_type", {}).get(
        "Lamp", []
    )

    entities: list[PuGoingLampLight] = [
        PuGoingLampLight(coordinator, dev) for dev in lamp_devices
    ]

    async_add_entities(entities)


# -----------------------------------------------------------------------------
# Entity implementation
# -----------------------------------------------------------------------------
class PuGoingLampLight(IntegrationBlueprintEntity, LightEntity):
    """Representation of a single Lamp device."""

    _attr_supported_color_modes = {ColorMode.ONOFF}

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
        # `dinfo` == "关" / "开" – you may need to adjust if your backend
        # uses other strings or a binary flag.
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
    def is_on(self) -> bool:  # noqa: D401 “is …” preferred
        """Return True if light is on."""
        dev = self._current_device_dict()
        if dev is not None:
            self._state = self._parse_state(dev)
        return self._state

    @property
    def available(self) -> bool:  # noqa: D401
        """Entity is available only if device still shows up in the cloud list."""
        return self._current_device_dict() is not None

    # ---------------------------------------------------------------------
    # Control methods
    # ---------------------------------------------------------------------
    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: D401
        """Turn the lamp on (optionally with brightness)."""
        # brightness: int | None = kwargs.get(ATTR_BRIGHTNESS)
        # TODO: adjust client call if your backend expects 0-100 or 0-255
        await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
            self._device_id, on=True,sn=self._device_sn, # brightness=brightness
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: D401, ARG002
        """Turn the lamp off."""
        await self.coordinator.config_entry.runtime_data.client.async_set_lamp_state(
            self._device_id, on=False,sn=self._device_sn,
        )
        await self.coordinator.async_request_refresh()

    # ---------------------------------------------------------------------
    # Extra attributes (optional, shown under «Device Info»)
    # ---------------------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:  # noqa: D401
        dev = self._current_device_dict()
        if dev is None:
            return None
        return {
            "sn": dev.get("sn"),
            "panel": dev.get("dpanel"),
            "room": dev.get("dloca"),
            "online": dev.get("online"),
        }
