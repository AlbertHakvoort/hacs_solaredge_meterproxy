"""Modbus proxy server for SolarEdge MeterProxy."""
from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

from pymodbus.constants import Endian
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.server import StartTcpServer
from pymodbus.transaction import ModbusRtuFramer, ModbusSocketFramer

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_SERVER_IP,
    CONF_SERVER_PORT,
    CONF_METER_MODBUS_ADDRESS,
    CONF_PROTOCOL,
    CONF_CT_CURRENT,
    CONF_CT_INVERTED,
    CONF_PHASE_OFFSET,
    CONF_SERIAL_NUMBER,
    DEFAULT_SERVER_IP,
    DEFAULT_SERVER_PORT,
    DEFAULT_METER_MODBUS_ADDRESS,
    DEFAULT_PROTOCOL,
    DEFAULT_CT_CURRENT,
    DEFAULT_CT_INVERTED,
    DEFAULT_PHASE_OFFSET,
    DEFAULT_SERIAL_NUMBER,
)

_LOGGER = logging.getLogger(__name__)


class ModbusProxyServer:
    """Modbus proxy server that simulates a WattNode meter."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, coordinator
    ) -> None:
        """Initialize the Modbus proxy server."""
        self.hass = hass
        self.entry = entry
        self.coordinator = coordinator
        self._server = None
        self._server_task = None
        self._update_task = None
        self._stop_event = asyncio.Event()
        self._slave_context = None

    async def async_start(self) -> None:
        """Start the Modbus server."""
        try:
            await self._setup_server()
            self._update_task = self.hass.async_create_task(self._update_loop())
            _LOGGER.info("Modbus proxy server started successfully")
        except Exception as ex:
            _LOGGER.error("Failed to start Modbus server: %s", ex)
            raise

    async def async_stop(self) -> None:
        """Stop the Modbus server."""
        self._stop_event.set()
        
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

        if self._server:
            self._server.shutdown()
            
        _LOGGER.info("Modbus proxy server stopped")

    async def _setup_server(self) -> None:
        """Set up the Modbus server with WattNode meter simulation."""
        server_ip = self.entry.data.get(CONF_SERVER_IP, DEFAULT_SERVER_IP)
        server_port = self.entry.data.get(CONF_SERVER_PORT, DEFAULT_SERVER_PORT)
        meter_address = self.entry.data.get(CONF_METER_MODBUS_ADDRESS, DEFAULT_METER_MODBUS_ADDRESS)
        protocol = self.entry.data.get(CONF_PROTOCOL, DEFAULT_PROTOCOL)

        # Create slave context for the meter
        self._slave_context = ModbusSlaveContext()
        
        # Initialize meter configuration registers
        await self._initialize_meter_registers()

        # Create server context with the slave
        slaves = {meter_address: self._slave_context}
        server_context = ModbusServerContext(slaves=slaves, single=False)

        # Configure framer based on protocol
        framer = ModbusSocketFramer if protocol == "tcp" else ModbusRtuFramer

        # Create device identification
        identity = ModbusDeviceIdentification()
        identity.VendorName = "SolarEdge MeterProxy"
        identity.ProductCode = "SEMP"
        identity.VendorUrl = "https://github.com/AlbertHakvoort/hacs_solaredge_meterproxy"
        identity.ProductName = "SolarEdge MeterProxy"
        identity.ModelName = "WattNode Emulator"
        identity.MajorMinorRevision = "1.0.0"

        # Start the server in a separate thread
        def run_server():
            asyncio.set_event_loop(asyncio.new_event_loop())
            self._server = StartTcpServer(
                context=server_context,
                identity=identity,
                framer=framer,
                address=(server_ip, server_port),
            )

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Give the server time to start
        await asyncio.sleep(1)

    async def _initialize_meter_registers(self) -> None:
        """Initialize the WattNode meter registers with default values."""
        ct_current = self.entry.data.get(CONF_CT_CURRENT, DEFAULT_CT_CURRENT)
        ct_inverted = self.entry.data.get(CONF_CT_INVERTED, DEFAULT_CT_INVERTED)
        phase_offset = self.entry.data.get(CONF_PHASE_OFFSET, DEFAULT_PHASE_OFFSET)
        serial_number = self.entry.data.get(CONF_SERIAL_NUMBER, DEFAULT_SERIAL_NUMBER)

        # Configuration registers (1600-1699)
        block_1601 = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        block_1601.add_32bit_int(1234)  # config passcode
        block_1601.add_16bit_int(ct_current)  # ct rated current
        block_1601.add_16bit_int(ct_current)  # ct rated current l1
        block_1601.add_16bit_int(ct_current)  # ct rated current l2
        block_1601.add_16bit_int(ct_current)  # ct rated current l3
        block_1601.add_16bit_int(ct_inverted)  # ct direction inversion
        block_1601.add_16bit_int(0)  # measurement averaging
        block_1601.add_16bit_int(0)  # power scale
        block_1601.add_16bit_int(15)  # demand period
        block_1601.add_16bit_int(1)  # demand subintervals
        block_1601.add_16bit_int(10000)  # power/energy adjustment l1
        block_1601.add_16bit_int(10000)  # power/energy adjustment l2
        block_1601.add_16bit_int(10000)  # power/energy adjustment l3
        block_1601.add_16bit_int(-1000)  # ct phase angle adjustment l1
        block_1601.add_16bit_int(-1000)  # ct phase angle adjustment l2
        block_1601.add_16bit_int(-1000)  # ct phase angle adjustment l3
        block_1601.add_16bit_int(1500)  # minimum power reading
        block_1601.add_16bit_int(phase_offset)  # phase offset
        block_1601.add_16bit_int(0)  # reset energy
        block_1601.add_16bit_int(0)  # reset demand
        block_1601.add_16bit_int(20000)  # voltage scale
        block_1601.add_16bit_int(20000)  # current scale
        block_1601.add_16bit_int(0)  # io pin mode

        self._slave_context.setValues(3, 1600, block_1601.to_registers())

        # Communication settings (1650-1699)
        block_1651 = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        block_1651.add_16bit_int(0)  # apply config
        block_1651.add_16bit_int(2)  # modbus address
        block_1651.add_16bit_int(4)  # baud rate
        block_1651.add_16bit_int(0)  # parity mode
        block_1651.add_16bit_int(0)  # modbus mode
        block_1651.add_16bit_int(5)  # message delay

        self._slave_context.setValues(3, 1650, block_1651.to_registers())

        # Device information (1700-1799)
        block_1701 = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        block_1701.add_32bit_int(serial_number)  # serial number
        block_1701.add_32bit_int(0)  # uptime (s)
        block_1701.add_32bit_int(0)  # total uptime (s)
        block_1701.add_16bit_int(202)  # wattnode model
        block_1701.add_16bit_int(31)  # firmware version
        block_1701.add_16bit_int(0)  # wattnode options
        block_1701.add_16bit_int(0)  # error status
        block_1701.add_16bit_int(0)  # power fail count
        block_1701.add_16bit_int(0)  # crc error count
        block_1701.add_16bit_int(0)  # frame error count
        block_1701.add_16bit_int(0)  # packet error count
        block_1701.add_16bit_int(0)  # overrun count
        
        # Add error status registers (8 more registers)
        for _ in range(8):
            block_1701.add_16bit_int(0)

        self._slave_context.setValues(3, 1700, block_1701.to_registers())

    async def _update_loop(self) -> None:
        """Update meter data continuously."""
        while not self._stop_event.is_set():
            try:
                if self.coordinator.data:
                    await self._update_meter_values(self.coordinator.data)
                await asyncio.sleep(1)  # Update every second
            except asyncio.CancelledError:
                break
            except Exception as ex:
                _LOGGER.error("Error in update loop: %s", ex)
                await asyncio.sleep(5)  # Wait before retrying

    async def _update_meter_values(self, values: dict[str, Any]) -> None:
        """Update the Modbus registers with meter values."""
        try:
            # Primary registers (1000-1099)
            block_1001 = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
            
            # Energy values
            block_1001.add_32bit_float(values.get("energy_active", 0))  # total active energy
            block_1001.add_32bit_float(values.get("import_energy_active", 0))  # imported active energy
            block_1001.add_32bit_float(values.get("energy_active", 0))  # total active energy non-reset
            block_1001.add_32bit_float(values.get("import_energy_active", 0))  # imported active energy non-reset
            
            # Power values
            block_1001.add_32bit_float(values.get("power_active", 0))  # total power
            block_1001.add_32bit_float(values.get("l1_power_active", 0))  # power l1
            block_1001.add_32bit_float(values.get("l2_power_active", 0))  # power l2
            block_1001.add_32bit_float(values.get("l3_power_active", 0))  # power l3
            
            # Voltage values
            block_1001.add_32bit_float(values.get("voltage_ln", 0))  # l-n voltage
            block_1001.add_32bit_float(values.get("l1n_voltage", 0))  # l1-n voltage
            block_1001.add_32bit_float(values.get("l2n_voltage", 0))  # l2-n voltage
            block_1001.add_32bit_float(values.get("l3n_voltage", 0))  # l3-n voltage
            block_1001.add_32bit_float(values.get("voltage_ll", 0))  # l-l voltage
            block_1001.add_32bit_float(values.get("l12_voltage", 0))  # l1-l2 voltage
            block_1001.add_32bit_float(values.get("l23_voltage", 0))  # l2-l3 voltage
            block_1001.add_32bit_float(values.get("l31_voltage", 0))  # l3-l1 voltage
            block_1001.add_32bit_float(values.get("frequency", 0))  # line frequency

            self._slave_context.setValues(3, 1000, block_1001.to_registers())

            # Extended registers (1100-1199)
            block_1101 = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
            
            # Energy per phase
            block_1101.add_32bit_float(values.get("l1_energy_active", 0))  # total active energy l1
            block_1101.add_32bit_float(values.get("l2_energy_active", 0))  # total active energy l2
            block_1101.add_32bit_float(values.get("l3_energy_active", 0))  # total active energy l3
            
            # Import/export energy
            block_1101.add_32bit_float(values.get("l1_import_energy_active", 0))  # import energy l1
            block_1101.add_32bit_float(values.get("l2_import_energy_active", 0))  # import energy l2
            block_1101.add_32bit_float(values.get("l3_import_energy_active", 0))  # import energy l3
            block_1101.add_32bit_float(values.get("export_energy_active", 0))  # export energy
            block_1101.add_32bit_float(values.get("l1_export_energy_active", 0))  # export energy l1
            block_1101.add_32bit_float(values.get("l2_export_energy_active", 0))  # export energy l2
            block_1101.add_32bit_float(values.get("l3_export_energy_active", 0))  # export energy l3
            
            # Reactive and apparent energy
            block_1101.add_32bit_float(values.get("energy_reactive", 0))  # total reactive energy
            block_1101.add_32bit_float(values.get("l1_energy_reactive", 0))  # reactive energy l1
            block_1101.add_32bit_float(values.get("l2_energy_reactive", 0))  # reactive energy l2
            block_1101.add_32bit_float(values.get("l3_energy_reactive", 0))  # reactive energy l3
            block_1101.add_32bit_float(values.get("energy_apparent", 0))  # total apparent energy
            block_1101.add_32bit_float(values.get("l1_energy_apparent", 0))  # apparent energy l1
            block_1101.add_32bit_float(values.get("l2_energy_apparent", 0))  # apparent energy l2
            block_1101.add_32bit_float(values.get("l3_energy_apparent", 0))  # apparent energy l3
            
            # Power factor
            block_1101.add_32bit_float(values.get("power_factor", 0))  # power factor
            block_1101.add_32bit_float(values.get("l1_power_factor", 0))  # power factor l1
            block_1101.add_32bit_float(values.get("l2_power_factor", 0))  # power factor l2
            block_1101.add_32bit_float(values.get("l3_power_factor", 0))  # power factor l3
            
            # Reactive and apparent power
            block_1101.add_32bit_float(values.get("power_reactive", 0))  # total reactive power
            block_1101.add_32bit_float(values.get("l1_power_reactive", 0))  # reactive power l1
            block_1101.add_32bit_float(values.get("l2_power_reactive", 0))  # reactive power l2
            block_1101.add_32bit_float(values.get("l3_power_reactive", 0))  # reactive power l3
            block_1101.add_32bit_float(values.get("power_apparent", 0))  # total apparent power
            block_1101.add_32bit_float(values.get("l1_power_apparent", 0))  # apparent power l1
            block_1101.add_32bit_float(values.get("l2_power_apparent", 0))  # apparent power l2
            block_1101.add_32bit_float(values.get("l3_power_apparent", 0))  # apparent power l3
            
            # Current values
            block_1101.add_32bit_float(values.get("l1_current", 0))  # current l1
            block_1101.add_32bit_float(values.get("l2_current", 0))  # current l2
            block_1101.add_32bit_float(values.get("l3_current", 0))  # current l3
            
            # Demand power
            block_1101.add_32bit_float(values.get("demand_power_active", 0))  # demand power
            block_1101.add_32bit_float(values.get("minimum_demand_power_active", 0))  # minimum demand power
            block_1101.add_32bit_float(values.get("maximum_demand_power_active", 0))  # maximum demand power
            block_1101.add_32bit_float(values.get("demand_power_apparent", 0))  # apparent demand power
            block_1101.add_32bit_float(values.get("l1_demand_power_active", 0))  # demand power l1
            block_1101.add_32bit_float(values.get("l2_demand_power_active", 0))  # demand power l2
            block_1101.add_32bit_float(values.get("l3_demand_power_active", 0))  # demand power l3

            self._slave_context.setValues(3, 1100, block_1101.to_registers())

        except Exception as ex:
            _LOGGER.error("Failed to update meter values: %s", ex)