"""Async Modbus RTU-over-TCP client for Oxygen controllers."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from time import monotonic
from typing import Any

from pymodbus import FramerType
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .exceptions import (
    OxygenModbusConnectionError,
    OxygenModbusResponseError,
    OxygenModbusWriteError,
)


class OxygenModbusClient:
    """Serialize and verify traffic through a transparent TCP converter."""

    def __init__(
        self,
        host: str,
        port: int,
        device_id: int,
        timeout: int,
        message_wait_ms: int,
    ) -> None:
        self._device_id = device_id
        self._message_wait = message_wait_ms / 1000
        self._lock = asyncio.Lock()
        self._last_transaction = 0.0
        self._client = AsyncModbusTcpClient(
            host,
            port=port,
            timeout=timeout,
            retries=3,
            framer=FramerType.RTU,
        )

    async def async_read_blocks(
        self, blocks: Iterable[tuple[int, int]]
    ) -> dict[int, int]:
        """Read register blocks with RTU-safe spacing between requests."""
        async with self._lock:
            await self._async_connect()
            values: dict[int, int] = {}
            for address, count in blocks:
                await self._async_wait_between_transactions()
                response = await self._async_read(address, count)
                values.update(
                    {address + offset: value for offset, value in enumerate(response)}
                )
            return values

    async def async_read_register(self, address: int) -> int:
        """Read one register."""
        async with self._lock:
            await self._async_connect()
            await self._async_wait_between_transactions()
            return (await self._async_read(address, 1))[0]

    async def async_write_register(self, address: int, value: int) -> None:
        """Write one register and verify it by reading it back."""
        async with self._lock:
            await self._async_connect()
            await self._async_wait_between_transactions()
            try:
                response = await self._client.write_register(
                    address, value=value, device_id=self._device_id
                )
            except (ModbusException, OSError, TimeoutError) as err:
                self._client.close()
                raise OxygenModbusConnectionError(
                    f"Unable to write register {address}"
                ) from err
            finally:
                self._last_transaction = monotonic()

            if response is None or response.isError():
                raise OxygenModbusResponseError(
                    f"Controller rejected register {address}: {response}"
                )

            await self._async_wait_between_transactions()
            actual = (await self._async_read(address, 1))[0]
            if actual != value:
                raise OxygenModbusWriteError(
                    f"Register {address} read back as {actual}, expected {value}"
                )

    async def async_test_connection(self) -> None:
        """Connect and read the documented firmware register."""
        await self.async_read_register(0)

    async def async_close(self) -> None:
        """Close the TCP connection."""
        self._client.close()

    async def _async_connect(self) -> None:
        if self._client.connected:
            return
        try:
            connected = await self._client.connect()
        except (ModbusException, OSError, TimeoutError) as err:
            raise OxygenModbusConnectionError(
                "Unable to connect to the Modbus converter"
            ) from err
        if not connected:
            raise OxygenModbusConnectionError(
                "Unable to connect to the Modbus converter"
            )

    async def _async_read(self, address: int, count: int) -> list[int]:
        try:
            response: Any = await self._client.read_holding_registers(
                address, count=count, device_id=self._device_id
            )
        except (ModbusException, OSError, TimeoutError) as err:
            self._client.close()
            raise OxygenModbusConnectionError(
                f"Unable to read registers starting at {address}"
            ) from err
        finally:
            self._last_transaction = monotonic()

        if response is None or response.isError():
            raise OxygenModbusResponseError(
                f"Controller rejected register read at {address}: {response}"
            )
        registers = getattr(response, "registers", None)
        if not isinstance(registers, list) or len(registers) != count:
            raise OxygenModbusResponseError(f"Invalid register response at {address}")
        return registers

    async def _async_wait_between_transactions(self) -> None:
        remaining = self._message_wait - (monotonic() - self._last_transaction)
        if remaining > 0:
            await asyncio.sleep(remaining)
