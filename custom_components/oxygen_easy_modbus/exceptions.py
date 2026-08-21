"""Exceptions for Oxygen Easy Modbus."""


class OxygenModbusError(Exception):
    """Base integration error."""


class OxygenModbusConnectionError(OxygenModbusError):
    """The converter or controller could not be reached."""


class OxygenModbusResponseError(OxygenModbusError):
    """The controller returned an invalid or error response."""


class OxygenModbusWriteError(OxygenModbusError):
    """A register write could not be verified."""
