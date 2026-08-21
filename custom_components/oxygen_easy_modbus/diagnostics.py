"""Privacy-conscious diagnostics for Oxygen Easy Modbus."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import OxygenModbusCoordinator
from .registers import firmware_version

TO_REDACT = {CONF_HOST, "unique_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics without endpoint or controller identity data."""
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "entry": async_redact_data(
            {
                "data": dict(entry.data),
                "options": dict(entry.options),
                "unique_id": entry.unique_id,
            },
            TO_REDACT,
        ),
        "controller": {
            "firmware": firmware_version(coordinator.value(0)),
            "available_registers": sorted(coordinator.data or {}),
            "last_update_success": coordinator.last_update_success,
        },
    }
