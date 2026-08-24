"""Oxygen Modbus register conversion helpers."""


def signed_register(value: int) -> int:
    """Decode a 16-bit two's-complement register."""
    return value - 0x10000 if value & 0x8000 else value


def temperature(value: int | None) -> float | None:
    """Decode a temperature register, including its invalid sentinel."""
    if value is None or value == 999:
        return None
    return signed_register(value) / 10


def firmware_version(value: int | None) -> str | None:
    """Decode the controller software version stored as two bytes."""
    if value is None:
        return None
    return f"S{value >> 8:03d}.{value & 0xFF:02d}"


def filter_reset_confirmed(before: int | None, after: int | None) -> bool:
    """Return whether a filter usage counter reflects a successful reset."""
    if after is None:
        return False
    return after <= 5 or before is not None and after < before
