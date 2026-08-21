"""Sensors for Oxygen Easy Modbus."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import OxygenModbusCoordinator
from .entity import OxygenModbusEntity
from .registers import firmware_version, temperature


@dataclass(frozen=True, kw_only=True)
class OxygenModbusSensorDescription(SensorEntityDescription):
    """Describe a readable register."""

    address: int
    transform: Callable[[int | None], object] | None = None


def _temperature(key: str, address: int, *, enabled: bool = True):
    return OxygenModbusSensorDescription(
        key=key,
        translation_key=key,
        address=address,
        transform=temperature,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=enabled,
    )


def _percentage(key: str, address: int, icon: str, *, diagnostic: bool = False):
    return OxygenModbusSensorDescription(
        key=key,
        translation_key=key,
        address=address,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon=icon,
        entity_category=EntityCategory.DIAGNOSTIC if diagnostic else None,
    )


SENSORS: tuple[OxygenModbusSensorDescription, ...] = (
    OxygenModbusSensorDescription(
        key="firmware",
        translation_key="firmware",
        address=0,
        transform=firmware_version,
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    _temperature("supply_temperature", 6),
    _temperature("extract_temperature", 7),
    _temperature("outdoor_temperature", 8),
    _temperature("exhaust_temperature", 9),
    _temperature("ground_heat_exchanger_temperature", 10, enabled=False),
    _temperature("secondary_heater_temperature", 11, enabled=False),
    _temperature("panel_temperature", 12, enabled=False),
    _percentage("heater_output", 24, "mdi:radiator"),
    _percentage("cooler_output", 25, "mdi:snowflake"),
    _percentage("bypass_opening", 27, "mdi:valve"),
    OxygenModbusSensorDescription(
        key="humidity",
        translation_key="humidity",
        address=41,
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OxygenModbusSensorDescription(
        key="co2",
        translation_key="co2",
        address=42,
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    _percentage("supply_fan", 43, "mdi:fan"),
    _percentage("extract_fan", 44, "mdi:fan"),
    OxygenModbusSensorDescription(
        key="supply_filter_days",
        translation_key="supply_filter_days",
        address=84,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:calendar-clock",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OxygenModbusSensorDescription(
        key="extract_filter_days",
        translation_key="extract_filter_days",
        address=85,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:calendar-clock",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    _percentage("supply_filter_usage", 86, "mdi:air-filter", diagnostic=True),
    _percentage("extract_filter_usage", 87, "mdi:air-filter", diagnostic=True),
    OxygenModbusSensorDescription(
        key="supply_airflow",
        translation_key="supply_airflow",
        address=94,
        native_unit_of_measurement="m³/h",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
    ),
    OxygenModbusSensorDescription(
        key="extract_airflow",
        translation_key="extract_airflow",
        address=95,
        native_unit_of_measurement="m³/h",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Oxygen register sensors."""
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OxygenModbusSensor(coordinator, description) for description in SENSORS
    )


class OxygenModbusSensor(OxygenModbusEntity, SensorEntity):
    """Represent a readable Oxygen register."""

    entity_description: OxygenModbusSensorDescription

    def __init__(
        self,
        coordinator: OxygenModbusCoordinator,
        description: OxygenModbusSensorDescription,
    ) -> None:
        super().__init__(coordinator, description.address, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> object:
        """Return the decoded register value."""
        value = self.coordinator.value(self.address)
        if self.entity_description.transform is not None:
            return self.entity_description.transform(value)
        return value
