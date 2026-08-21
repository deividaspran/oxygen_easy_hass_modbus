"""Switch controls for Oxygen Easy Modbus."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import OxygenModbusCoordinator
from .entity import OxygenModbusWritableEntity
from .exceptions import OxygenModbusError


@dataclass(frozen=True, kw_only=True)
class OxygenModbusSwitchDescription(SwitchEntityDescription):
    """Describe a writable on/off register."""

    address: int
    requires_power_permission: bool = False


SWITCHES: tuple[OxygenModbusSwitchDescription, ...] = (
    OxygenModbusSwitchDescription(
        key="power",
        translation_key="power",
        address=1,
        icon="mdi:power",
        requires_power_permission=True,
    ),
    OxygenModbusSwitchDescription(
        key="airing", translation_key="airing", address=32, icon="mdi:weather-windy"
    ),
    OxygenModbusSwitchDescription(
        key="away",
        translation_key="away",
        address=33,
        icon="mdi:home-export-outline",
    ),
    OxygenModbusSwitchDescription(
        key="party",
        translation_key="party",
        address=34,
        icon="mdi:party-popper",
    ),
    OxygenModbusSwitchDescription(
        key="fireplace",
        translation_key="fireplace",
        address=35,
        icon="mdi:fireplace",
    ),
    OxygenModbusSwitchDescription(
        key="schedule",
        translation_key="schedule",
        address=37,
        icon="mdi:calendar-clock",
    ),
    OxygenModbusSwitchDescription(
        key="automatic",
        translation_key="automatic",
        address=59,
        icon="mdi:autorenew",
    ),
    OxygenModbusSwitchDescription(
        key="boost_1",
        translation_key="boost_1",
        address=90,
        icon="mdi:fan-plus",
    ),
    OxygenModbusSwitchDescription(
        key="boost_2",
        translation_key="boost_2",
        address=91,
        icon="mdi:fan-plus",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Oxygen switches."""
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OxygenModbusSwitch(coordinator, description) for description in SWITCHES
    )


class OxygenModbusSwitch(OxygenModbusWritableEntity, SwitchEntity):
    """Control an Oxygen on/off register."""

    entity_description: OxygenModbusSwitchDescription

    def __init__(
        self,
        coordinator: OxygenModbusCoordinator,
        description: OxygenModbusSwitchDescription,
    ) -> None:
        super().__init__(coordinator, description.address, description.key)
        self.entity_description = description
        self.requires_power_permission = description.requires_power_permission

    @property
    def is_on(self) -> bool | None:
        """Return the current register state."""
        value = self.coordinator.value(self.address)
        return None if value is None else value == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the mode."""
        await self._async_set_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the mode."""
        await self._async_set_state(False)

    async def _async_set_state(self, enabled: bool) -> None:
        try:
            await self.coordinator.async_set_register(self.address, 1 if enabled else 0)
        except OxygenModbusError as err:
            raise HomeAssistantError(str(err)) from err
