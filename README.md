# Oxygen Easy Modbus for Home Assistant

A local, UI-configurable Home Assistant integration for Oxygen / ecoVENT
ventilation controllers over Modbus RTU carried through a transparent TCP
converter. It does not use the Oxygen cloud.

## Requirements

- A compatible Oxygen ventilation controller with its isolated COM3 RS485 port.
- An RS485-to-Ethernet converter configured for transparent TCP / Modbus
  RTU-over-TCP, with serial settings matching the controller.
- Correct COM3 +5V, GND, D+, and D- wiring according to Oxygen's documentation.
- Modbus setting writes and start/stop writes enabled in the controller when
  controls are required.

The existing Oxygen internet module can remain on its normal controller bus;
this integration uses the dedicated COM3 connection. Never attach two masters
to the same RS485 pair.

## Installation

### HACS

1. Open HACS, then Integrations.
2. Add this repository as a custom repository with category Integration.
3. Install Oxygen Easy Modbus.
4. Restart Home Assistant.
5. Open Settings > Devices & services > Add integration.
6. Search for Oxygen Easy Modbus and enter the converter host, TCP port, and
   Modbus device address.

The default port is 502 and the default device address is 1. Connection timing
can be changed later from the integration's Configure dialog.

### Manual

Copy custom_components/oxygen_easy_modbus into the matching directory under
your Home Assistant configuration, then restart Home Assistant.

## Included entities

The initial release reads controller firmware, operating/fault/bypass state,
temperatures, humidity, CO2, fan output, heater/cooler/bypass output, filter
interval and usage, and measured airflow.

It controls power, automatic/schedule/airing/away/party/fireplace/boost modes,
fan level, comfort/season/bypass modes, comfort temperatures, and party
duration. Advanced fan-speed, airflow, and equipment-specific controls are
disabled by default and can be enabled from the entity registry.

Controls become unavailable if the controller reports that the corresponding
Modbus writes are disabled. Every write is read back and verified before Home
Assistant treats it as successful.

## Filter reminder

When either filter reaches 100% usage, Home Assistant receives a persistent
notification. It is dismissed automatically after both reported usages fall
below 100%. The destructive filter-reset command is deliberately not exposed.

## Safety and scope

Factory reset, filter reset, serial-number registers, and undocumented alarm
registers are excluded. The integration polls in contiguous blocks and never
reads the documented serial-number register range. Diagnostics redact the
configured host and unique ID.

This is an independent community integration. Test control changes while it is
safe to alter ventilation and retain access to the manufacturer's controls.

## Acknowledgements

Much love and thanks to [Oxygen](https://oxygen.lt/) for directly providing the
COM3 pinout, connection guidance, and Modbus register information that made
this local integration possible.

Oxygen, ecoVENT, and related marks belong to their respective owners. Vendor
material informed this implementation but is not redistributed by this
repository.

## License

MIT
