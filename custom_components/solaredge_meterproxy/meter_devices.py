"""Meter device implementations for SolarEdge MeterProxy."""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BaseMeterDevice(ABC):
    """Base class for meter devices."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the meter device."""
        self.hass = hass
        self.config = config

    @abstractmethod
    async def async_read_values(self) -> dict[str, Any]:
        """Read values from the meter device."""
        pass

    @abstractmethod
    async def async_connect(self) -> None:
        """Connect to the meter device."""
        pass

    @abstractmethod
    async def async_disconnect(self) -> None:
        """Disconnect from the meter device."""
        pass


class GenericMeterDevice(BaseMeterDevice):
    """Generic meter device that returns default values."""

    async def async_read_values(self) -> dict[str, Any]:
        """Read values from the meter device."""
        return {
            "energy_active": 1000.0,
            "import_energy_active": 800.0,
            "export_energy_active": 200.0,
            "power_active": 500.0,
            "l1_power_active": 166.7,
            "l2_power_active": 166.7,
            "l3_power_active": 166.6,
            "voltage_ln": 230.0,
            "l1n_voltage": 230.0,
            "l2n_voltage": 230.0,
            "l3n_voltage": 230.0,
            "voltage_ll": 400.0,
            "l12_voltage": 400.0,
            "l23_voltage": 400.0,
            "l31_voltage": 400.0,
            "frequency": 50.0,
            "l1_current": 0.72,
            "l2_current": 0.72,
            "l3_current": 0.72,
            "power_factor": 0.95,
            "l1_power_factor": 0.95,
            "l2_power_factor": 0.95,
            "l3_power_factor": 0.95,
        }

    async def async_connect(self) -> None:
        """Connect to the meter device."""
        pass

    async def async_disconnect(self) -> None:
        """Disconnect from the meter device."""
        pass


class SDM120MeterDevice(BaseMeterDevice):
    """SDM120 meter device implementation."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the SDM120 meter device."""
        super().__init__(hass, config)
        self._client = None

    async def async_connect(self) -> None:
        """Connect to the SDM120 meter via Modbus."""
        try:
            try:
                from pymodbus.client import ModbusTcpClient
            except ImportError:
                _LOGGER.error("pymodbus is required for SDM120 meter support")
                raise ConnectionError("pymodbus is not installed")
            
            host = self.config["meter_host"]
            port = self.config["meter_port"]
            
            self._client = ModbusTcpClient(host, port=port)
            connection = await self.hass.async_add_executor_job(self._client.connect)
            
            if not connection:
                raise ConnectionError(f"Failed to connect to SDM120 at {host}:{port}")
                
            _LOGGER.info("Connected to SDM120 meter at %s:%s", host, port)
            
        except Exception as ex:
            _LOGGER.error("Failed to connect to SDM120 meter: %s", ex)
            raise

    async def async_disconnect(self) -> None:
        """Disconnect from the SDM120 meter."""
        if self._client:
            await self.hass.async_add_executor_job(self._client.close)

    async def async_read_values(self) -> dict[str, Any]:
        """Read values from the SDM120 meter."""
        if not self._client or not self._client.connected:
            await self.async_connect()

        try:
            meter_address = self.config["meter_address"]
            
            # Read basic values from SDM120 registers
            # These are the standard SDM120 Modbus registers
            voltage_result = await self.hass.async_add_executor_job(
                self._client.read_input_registers, 0, 2, meter_address
            )
            current_result = await self.hass.async_add_executor_job(
                self._client.read_input_registers, 6, 2, meter_address
            )
            power_result = await self.hass.async_add_executor_job(
                self._client.read_input_registers, 12, 2, meter_address
            )
            energy_result = await self.hass.async_add_executor_job(
                self._client.read_input_registers, 72, 2, meter_address
            )
            frequency_result = await self.hass.async_add_executor_job(
                self._client.read_input_registers, 70, 2, meter_address
            )
            
            # Convert register values to float (SDM120 uses 32-bit floats)
            voltage = self._registers_to_float(voltage_result.registers) if not voltage_result.isError() else 230.0
            current = self._registers_to_float(current_result.registers) if not current_result.isError() else 0.0
            power = self._registers_to_float(power_result.registers) if not power_result.isError() else 0.0
            energy = self._registers_to_float(energy_result.registers) if not energy_result.isError() else 0.0
            frequency = self._registers_to_float(frequency_result.registers) if not frequency_result.isError() else 50.0
            
            return {
                "energy_active": energy,
                "import_energy_active": energy,
                "power_active": power,
                "l1_power_active": power,
                "voltage_ln": voltage,
                "l1n_voltage": voltage,
                "frequency": frequency,
                "l1_current": current,
                "power_factor": 0.95,  # SDM120 doesn't always provide this
                "l1_power_factor": 0.95,
                "l1_energy_active": energy,
            }
            
        except Exception as ex:
            _LOGGER.error("Failed to read SDM120 values: %s", ex)
            # Return default values on error
            return await GenericMeterDevice(self.hass, self.config).async_read_values()

    def _registers_to_float(self, registers: list[int]) -> float:
        """Convert two Modbus registers to a 32-bit float."""
        if len(registers) != 2:
            return 0.0
        
        import struct
        # Combine two 16-bit registers into one 32-bit value
        combined = (registers[0] << 16) | registers[1]
        # Convert to float using IEEE 754 format
        return struct.unpack('>f', struct.pack('>I', combined))[0]


class MeterDeviceFactory:
    """Factory class for creating meter devices."""

    @staticmethod
    async def create_device(hass: HomeAssistant, config: dict[str, Any]) -> BaseMeterDevice:
        """Create a meter device based on configuration."""
        meter_type = config.get("meter_type", "generic")
        
        if meter_type == "sdm120":
            device = SDM120MeterDevice(hass, config)
        elif meter_type == "generic":
            device = GenericMeterDevice(hass, config)
        else:
            _LOGGER.warning("Unsupported meter type %s, using generic", meter_type)
            device = GenericMeterDevice(hass, config)
        
        await device.async_connect()
        return device