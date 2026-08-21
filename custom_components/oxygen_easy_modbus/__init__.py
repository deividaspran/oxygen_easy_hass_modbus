"""Oxygen Easy Modbus integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_TIMEOUT
from homeassistant.core import HomeAssistant

from .api import OxygenModbusClient
from .const import (
    CONF_DEVICE_ID,
    CONF_MESSAGE_WAIT_MS,
    DEFAULT_MESSAGE_WAIT_MS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import OxygenModbusCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an Oxygen controller from a config entry."""
    client = OxygenModbusClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        device_id=entry.data[CONF_DEVICE_ID],
        timeout=entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
        message_wait_ms=entry.options.get(
            CONF_MESSAGE_WAIT_MS, DEFAULT_MESSAGE_WAIT_MS
        ),
    )
    coordinator = OxygenModbusCoordinator(
        hass,
        entry,
        client,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Oxygen controller."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_shutdown()
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after connection options change."""
    await hass.config_entries.async_reload(entry.entry_id)
