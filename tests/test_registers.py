"""Tests for pure register conversion helpers."""

import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "oxygen_easy_modbus"
    / "registers.py"
)
SPEC = spec_from_file_location("oxygen_modbus_registers", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
registers = module_from_spec(SPEC)
SPEC.loader.exec_module(registers)


class RegisterConversionTests(unittest.TestCase):
    """Verify documented register encodings."""

    def test_signed_register(self) -> None:
        self.assertEqual(registers.signed_register(250), 250)
        self.assertEqual(registers.signed_register(0xFFF6), -10)

    def test_temperature_scale_and_sentinel(self) -> None:
        self.assertEqual(registers.temperature(248), 24.8)
        self.assertEqual(registers.temperature(0xFFF6), -1.0)
        self.assertIsNone(registers.temperature(999))
        self.assertIsNone(registers.temperature(None))

    def test_firmware_version(self) -> None:
        self.assertEqual(registers.firmware_version(0x012C), "S001.44")
        self.assertIsNone(registers.firmware_version(None))


if __name__ == "__main__":
    unittest.main()
