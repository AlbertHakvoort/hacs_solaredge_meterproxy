"""The SolarEdge MeterProxy integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import SolarEdgeMeterProxyCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SolarEdge MeterProxy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = SolarEdgeMeterProxyCoordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        raise ConfigEntryNotReady(f"Unable to connect: {ex}") from ex

    # Try to start the Modbus proxy server
    modbus_server = None
    try:
        from .modbus_server import ModbusProxyServer
        modbus_server = ModbusProxyServer(hass, entry, coordinator)
        await modbus_server.async_start()
        _LOGGER.info("Modbus proxy server started successfully")
    except Exception as ex:
        _LOGGER.warning("Failed to start Modbus server: %s", ex)
        _LOGGER.info("Continuing without Modbus server - sensors will still work")

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "modbus_server": modbus_server,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Stop the Modbus server if it exists
        data = hass.data[DOMAIN][entry.entry_id]
        modbus_server = data.get("modbus_server")
        if modbus_server:
            try:
                await modbus_server.async_stop()
            except Exception as ex:
                _LOGGER.warning("Error stopping Modbus server: %s", ex)
        
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)