"""Binary sensors for Oxygen Easy Modbus."""

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import OxygenModbusCoordinator
from .entity import OxygenModbusEntity


@dataclass(frozen=True, kw_only=True)
class OxygenModbusBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a binary register."""

    address: int


BINARY_SENSORS: tuple[OxygenModbusBinarySensorDescription, ...] = (
    OxygenModbusBinarySensorDescription(
        key="running",
        translation_key="running",
        address=2,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    OxygenModbusBinarySensorDescription(
        key="fault",
        translation_key="fault",
        address=3,
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OxygenModbusBinarySensorDescription(
        key="bypass_active",
        translation_key="bypass_active",
        address=17,
        icon="mdi:valve",
    ),
    OxygenModbusBinarySensorDescription(
        key="alarm_input",
        translation_key="alarm_input",
        address=21,
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    OxygenModbusBinarySensorDescription(
        key="settings_writable",
        translation_key="settings_writable",
        address=76,
        icon="mdi:pencil",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OxygenModbusBinarySensorDescription(
        key="power_writable",
        translation_key="power_writable",
        address=77,
        icon="mdi:power-plug",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Oxygen binary sensors."""
    coordinator: OxygenModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OxygenModbusBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    )


class OxygenModbusBinarySensor(OxygenModbusEntity, BinarySensorEntity):
    """Represent a binary Oxygen register."""

    entity_description: OxygenModbusBinarySensorDescription

    def __init__(
        self,
        coordinator: OxygenModbusCoordinator,
        description: OxygenModbusBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, description.address, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return the boolean register value."""
        value = self.coordinator.value(self.address)
        return None if value is None else value == 1
