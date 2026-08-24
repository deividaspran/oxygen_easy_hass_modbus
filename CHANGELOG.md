# Changelog

## 0.2.0

- Add supply, extract, and combined filter-counter reset buttons using Oxygen's
  documented register 88 commands.
- Include current filter usage percentages in persistent replacement reminders.

## 0.1.0

- Add UI setup for local Modbus RTU-over-TCP connections.
- Add batched polling for documented controller registers.
- Add environmental, operating, airflow, filter, and diagnostic sensors.
- Add permission-aware switches, selects, and number controls.
- Verify every register write by reading it back.
- Add persistent filter replacement notifications.
- Redact connection identity from diagnostics.
