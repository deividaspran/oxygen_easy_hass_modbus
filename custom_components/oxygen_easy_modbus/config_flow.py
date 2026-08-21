"""Config flow for Oxygen Easy Modbus."""

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_TIMEOUT

from .api import OxygenModbusClient
from .const import (
    CONF_DEVICE_ID,
    CONF_MESSAGE_WAIT_MS,
    DEFAULT_DEVICE_ID,
    DEFAULT_MESSAGE_WAIT_MS,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    MAX_MESSAGE_WAIT_MS,
    MAX_SCAN_INTERVAL,
    MIN_MESSAGE_WAIT_MS,
    MIN_SCAN_INTERVAL,
)
from .exceptions import OxygenModbusError


class OxygenEasyModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a local Oxygen Modbus connection."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the connection form."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            client = OxygenModbusClient(
                host=host,
                port=user_input[CONF_PORT],
                device_id=user_input[CONF_DEVICE_ID],
                timeout=DEFAULT_TIMEOUT,
                message_wait_ms=DEFAULT_MESSAGE_WAIT_MS,
            )
            try:
                await client.async_test_connection()
            except OxygenModbusError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{host.casefold()}:{user_input[CONF_PORT]}:"
                    f"{user_input[CONF_DEVICE_ID]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                    },
                )
            finally:
                await client.async_close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=65535)
                    ),
                    vol.Required(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=247)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return OxygenEasyModbusOptionsFlow(config_entry)


class OxygenEasyModbusOptionsFlow(OptionsFlow):
    """Configure polling and transport timing."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage connection timing options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self._config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                    vol.Required(
                        CONF_TIMEOUT,
                        default=options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
                    vol.Required(
                        CONF_MESSAGE_WAIT_MS,
                        default=options.get(
                            CONF_MESSAGE_WAIT_MS, DEFAULT_MESSAGE_WAIT_MS
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_MESSAGE_WAIT_MS, max=MAX_MESSAGE_WAIT_MS),
                    ),
                }
            ),
        )
