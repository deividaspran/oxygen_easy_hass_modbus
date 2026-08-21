"""Shared entities for Oxygen Easy Modbus."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, REGISTER_PROGRAM_VERSION
from .coordinator import OxygenModbusCoordinator
from .registers import firmware_version


class OxygenModbusEntity(CoordinatorEntity[OxygenModbusCoordinator]):
    """Base entity backed by a documented Modbus register."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: OxygenModbusCoordinator, address: int, key: str
    ) -> None:
        super().__init__(coordinator, context=address)
        self.address = address
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{key}_{address}"

    @property
    def device_info(self) -> DeviceInfo:
        """Describe the controller without publishing its endpoint."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.config_entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=firmware_version(
                self.coordinator.value(REGISTER_PROGRAM_VERSION)
            ),
        )


class OxygenModbusWritableEntity(OxygenModbusEntity):
    """Entity that respects the controller's Modbus write permission."""

    requires_power_permission = False

    @property
    def available(self) -> bool:
        """Return whether polling and the applicable permission are ready."""
        permitted = (
            self.coordinator.power_writable
            if self.requires_power_permission
            else self.coordinator.settings_writable
        )
        return super().available and permitted
