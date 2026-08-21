# Contributing

Bug reports and focused pull requests are welcome.

## Before opening an issue

- Update to the latest release and restart Home Assistant.
- Check the converter uses transparent TCP / Modbus RTU-over-TCP mode.
- Remove credentials, network endpoints, serial numbers, and tokens from logs.
- State the controller model and firmware without its serial number.

## Development

Run:

    python -m compileall custom_components
    ruff check .

Test writes on hardware only when it is safe to alter ventilation. Register
additions should include the address, direction, raw range, scale, sentinel
values, and firmware tested. Destructive operations are intentionally excluded.
Do not copy vendor documents here without permission to redistribute them.
