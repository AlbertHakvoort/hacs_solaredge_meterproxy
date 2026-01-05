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

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SolarEdge MeterProxy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Try to start the Modbus proxy server
    modbus_server = None
    try:
        from .modbus_server import ModbusProxyServer
        modbus_server = ModbusProxyServer(hass, entry, None)  # No coordinator needed
        await modbus_server.async_start()
        _LOGGER.info("Modbus proxy server started successfully")
    except Exception as ex:
        _LOGGER.warning("Failed to start Modbus server: %s", ex)
        _LOGGER.info("Continuing without Modbus server - sensors will still work")

    hass.data[DOMAIN][entry.entry_id] = {
        "modbus_server": modbus_server,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        
        # Stop the Modbus server if it was running
        if data.get("modbus_server"):
            try:
                await data["modbus_server"].async_stop()
                _LOGGER.info("Modbus proxy server stopped")
            except Exception as ex:
                _LOGGER.error("Error stopping Modbus server: %s", ex)

    return unload_ok


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