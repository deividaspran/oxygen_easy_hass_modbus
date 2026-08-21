"""Select controls for Oxygen Easy Modbus."""

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import OxygenModbusCoordinator
from .entity import OxygenModbusWritableEntity
from .exceptions import OxygenModbusError


@dataclass(frozen=True, kw_only=True)
class OxygenModbusSelectDescription(SelectEntityDescription):
    """Describe an enumerated register."""

    address: int
    values: dict[str, int]


SELECTS: tuple[OxygenModbusSelectDescription, ...] = (
    OxygenModbusSelectDescription(
        key="fan_level",
        translation_key="fan_level",
        address=4,
        values={"low": 3, "medium": 4, "high": 5},
        icon="mdi:fan",
    ),
    OxygenModbusSelectDescription(
        key="season",
        translation_key="season",
        address=38,
        values={"summer": 1, "winter": 2, "automatic": 4},
        icon="mdi:sun-snowflake-variant",
    ),
    OxygenModbusSelectDescription(
        key="comfort_mode",
        translation_key="comfort_mode",
        address=57,
        values={"schedule": 0, "day": 1, "night": 2},
        icon="mdi:theme-light-dark",
    ),
    OxygenModbusSelectDescription(
        key="ground_heat_exchanger_mode",
        translation_key="ground_heat_exchanger_mode",
        address=69,
        values={"off": 0, "on": 1, "automatic": 2},
        icon="mdi:heat-wave",
        entity_registry_enabled_default=False,
    ),
    OxygenModbusSelectDescription(
        key="bypass_mode",
        translation_key="bypass_mode",
        address=89,
        values={"off": 1, "on": 2, "automatic": 3},
        icon="mdi:valve",
    ),
    OxygenModbusSelectDescription(
        key="airflow_adjustment_mode",
        translation_key="airflow_adjustment_mode",
        address=100,
        values={"speed": 0, "constant_pressure": 1, "constant_airflow": 2},
        icon="mdi:tune-variant",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Oxygen select controls."""
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OxygenModbusSelect(coordinator, description) for description in SELECTS
    )


class OxygenModbusSelect(OxygenModbusWritableEntity, SelectEntity):
    """Control an enumerated Oxygen register."""

    entity_description: OxygenModbusSelectDescription

    def __init__(
        self,
        coordinator: OxygenModbusCoordinator,
        description: OxygenModbusSelectDescription,
    ) -> None:
        super().__init__(coordinator, description.address, description.key)
        self.entity_description = description
        self._attr_options = list(description.values)

    @property
    def current_option(self) -> str | None:
        """Return the option matching the register value."""
        current = self.coordinator.value(self.address)
        return next(
            (
                option
                for option, value in self.entity_description.values.items()
                if value == current
            ),
            None,
        )

    async def async_select_option(self, option: str) -> None:
        """Write an enumerated option."""
        try:
            value = self.entity_description.values[option]
            await self.coordinator.async_set_register(self.address, value)
        except (KeyError, OxygenModbusError) as err:
            raise HomeAssistantError(
                f"Unable to set {self.entity_description.translation_key}"
            ) from err
