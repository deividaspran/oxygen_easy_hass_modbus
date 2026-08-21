"""Number controls for Oxygen Easy Modbus."""

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import OxygenModbusCoordinator
from .entity import OxygenModbusWritableEntity
from .exceptions import OxygenModbusError
from .registers import signed_register


@dataclass(frozen=True, kw_only=True)
class OxygenModbusNumberDescription(NumberEntityDescription):
    """Describe a numeric register."""

    address: int
    register_scale: int = 1


NUMBERS: tuple[OxygenModbusNumberDescription, ...] = (
    OxygenModbusNumberDescription(
        key="party_duration",
        translation_key="party_duration",
        address=67,
        native_min_value=1,
        native_max_value=15,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.HOURS,
        icon="mdi:timer-cog-outline",
    ),
    OxygenModbusNumberDescription(
        key="day_comfort_temperature",
        translation_key="day_comfort_temperature",
        address=78,
        register_scale=10,
        native_min_value=8,
        native_max_value=30,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:white-balance-sunny",
    ),
    OxygenModbusNumberDescription(
        key="night_comfort_temperature",
        translation_key="night_comfort_temperature",
        address=79,
        register_scale=10,
        native_min_value=8,
        native_max_value=30,
        native_step=0.1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:weather-night",
    ),
    *(
        OxygenModbusNumberDescription(
            key=key,
            translation_key=key,
            address=address,
            native_min_value=25,
            native_max_value=100,
            native_step=1,
            native_unit_of_measurement=PERCENTAGE,
            icon="mdi:fan-cog",
            entity_registry_enabled_default=False,
        )
        for key, address in (
            ("supply_low_speed", 48),
            ("supply_medium_speed", 49),
            ("supply_high_speed", 50),
            ("extract_low_speed", 54),
            ("extract_medium_speed", 55),
            ("extract_high_speed", 56),
        )
    ),
    OxygenModbusNumberDescription(
        key="supply_airflow_setpoint",
        translation_key="supply_airflow_setpoint",
        address=98,
        native_min_value=0,
        native_max_value=4000,
        native_step=1,
        native_unit_of_measurement="m³/h",
        icon="mdi:weather-windy",
        entity_registry_enabled_default=False,
    ),
    OxygenModbusNumberDescription(
        key="extract_airflow_setpoint",
        translation_key="extract_airflow_setpoint",
        address=99,
        native_min_value=0,
        native_max_value=4000,
        native_step=1,
        native_unit_of_measurement="m³/h",
        icon="mdi:weather-windy",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Oxygen number controls."""
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OxygenModbusNumber(coordinator, description) for description in NUMBERS
    )


class OxygenModbusNumber(OxygenModbusWritableEntity, NumberEntity):
    """Control a numeric Oxygen register."""

    entity_description: OxygenModbusNumberDescription

    def __init__(
        self,
        coordinator: OxygenModbusCoordinator,
        description: OxygenModbusNumberDescription,
    ) -> None:
        super().__init__(coordinator, description.address, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return the scaled register value."""
        value = self.coordinator.value(self.address)
        if value is None:
            return None
        return signed_register(value) / self.entity_description.register_scale

    async def async_set_native_value(self, value: float) -> None:
        """Scale and write a number."""
        raw = round(value * self.entity_description.register_scale)
        try:
            await self.coordinator.async_set_register(self.address, raw)
        except OxygenModbusError as err:
            raise HomeAssistantError(str(err)) from err
