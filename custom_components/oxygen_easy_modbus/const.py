"""Constants for Oxygen Easy Modbus."""

from homeassistant.const import Platform

DOMAIN = "oxygen_easy_modbus"
CONF_DEVICE_ID = "device_id"
CONF_MESSAGE_WAIT_MS = "message_wait_ms"

DEFAULT_NAME = "Oxygen ventilation"
DEFAULT_PORT = 502
DEFAULT_DEVICE_ID = 1
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_TIMEOUT = 5
DEFAULT_MESSAGE_WAIT_MS = 100
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300
MIN_MESSAGE_WAIT_MS = 0
MAX_MESSAGE_WAIT_MS = 1000

MANUFACTURER = "Oxygen"
MODEL = "ecoVENT ventilation controller"

PLATFORMS: tuple[Platform, ...] = (
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
)

# Contiguous requests keep polling efficient while excluding serial registers 122-126.
POLL_BLOCKS: tuple[tuple[int, int], ...] = (
    (0, 13),
    (17, 30),
    (48, 9),
    (57, 3),
    (67, 4),
    (76, 25),
)

REGISTER_PROGRAM_VERSION = 0
REGISTER_SUPPLY_FILTER_USAGE = 86
REGISTER_EXTRACT_FILTER_USAGE = 87
REGISTER_FILTER_RESET = 88
REGISTER_SETTINGS_WRITABLE = 76
REGISTER_POWER_WRITABLE = 77
