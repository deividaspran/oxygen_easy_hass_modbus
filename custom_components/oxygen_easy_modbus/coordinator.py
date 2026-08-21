"""Data coordinator for Oxygen Easy Modbus."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OxygenModbusClient
from .const import (
    DOMAIN,
    POLL_BLOCKS,
    REGISTER_POWER_WRITABLE,
    REGISTER_SETTINGS_WRITABLE,
)
from .exceptions import OxygenModbusError

_LOGGER = logging.getLogger(__name__)


class OxygenModbusCoordinator(DataUpdateCoordinator[dict[int, int]]):
    """Poll and update one Oxygen controller."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: OxygenModbusClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[int, int]:
        try:
            data = await self.client.async_read_blocks(POLL_BLOCKS)
            self._update_filter_notification(data)
            return data
        except OxygenModbusError as err:
            raise UpdateFailed(str(err)) from err

    def _update_filter_notification(self, data: dict[int, int]) -> None:
        """Keep one persistent notification while either filter is exhausted."""
        worn = [
            name
            for name, address in (("supply", 86), ("extract", 87))
            if data.get(address, 0) >= 100
        ]
        notification_id = f"{DOMAIN}_filters_{self.config_entry.entry_id}"
        if worn:
            persistent_notification.async_create(
                self.hass,
                "Replace the "
                + " and ".join(worn)
                + " air filter"
                + ("s" if len(worn) > 1 else "")
                + ". The controller reports 100% filter usage.",
                title="Oxygen ventilation filters need replacement",
                notification_id=notification_id,
            )
        else:
            persistent_notification.async_dismiss(self.hass, notification_id)

    async def async_set_register(self, address: int, value: int) -> None:
        """Write, verify, preserve state continuity, then refresh all data."""
        await self.client.async_write_register(address, value)
        if self.data is not None:
            updated = dict(self.data)
            updated[address] = value
            self.async_set_updated_data(updated)
        await self.async_request_refresh()

    def value(self, address: int) -> int | None:
        """Return a register value from the latest successful poll."""
        return None if self.data is None else self.data.get(address)

    @property
    def settings_writable(self) -> bool:
        """Return whether the controller permits parameter writes."""
        return self.value(REGISTER_SETTINGS_WRITABLE) == 1

    @property
    def power_writable(self) -> bool:
        """Return whether the controller permits start/stop writes."""
        return self.value(REGISTER_POWER_WRITABLE) == 1

    async def async_shutdown(self) -> None:
        """Close the transport."""
        await self.client.async_close()
