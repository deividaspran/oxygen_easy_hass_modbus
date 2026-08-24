"""Filter maintenance buttons for Oxygen Easy Modbus."""

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, REGISTER_FILTER_RESET
from .coordinator import OxygenModbusCoordinator
from .entity import OxygenModbusWritableEntity
from .exceptions import OxygenModbusError


@dataclass(frozen=True, kw_only=True)
class OxygenModbusButtonDescription(ButtonEntityDescription):
    """Describe a momentary filter maintenance command."""

    command: int


FILTER_RESET_BUTTONS: tuple[OxygenModbusButtonDescription, ...] = (
    OxygenModbusButtonDescription(
        key="reset_supply_filter",
        translation_key="reset_supply_filter",
        command=2,
        icon="mdi:air-filter",
    ),
    OxygenModbusButtonDescription(
        key="reset_extract_filter",
        translation_key="reset_extract_filter",
        command=3,
        icon="mdi:air-filter",
    ),
    OxygenModbusButtonDescription(
        key="reset_both_filters",
        translation_key="reset_both_filters",
        command=7,
        icon="mdi:air-filter",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up filter maintenance buttons."""
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OxygenModbusFilterResetButton(coordinator, description)
        for description in FILTER_RESET_BUTTONS
    )


class OxygenModbusFilterResetButton(OxygenModbusWritableEntity, ButtonEntity):
    """Reset one or both filter usage counters."""

    entity_description: OxygenModbusButtonDescription

    def __init__(
        self,
        coordinator: OxygenModbusCoordinator,
        description: OxygenModbusButtonDescription,
    ) -> None:
        super().__init__(
            coordinator,
            REGISTER_FILTER_RESET,
            description.key,
        )
        self.entity_description = description

    async def async_press(self) -> None:
        """Send and verify a filter reset command."""
        try:
            await self.coordinator.async_reset_filters(self.entity_description.command)
        except OxygenModbusError as err:
            raise HomeAssistantError(str(err)) from err
