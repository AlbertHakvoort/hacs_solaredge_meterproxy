"""Data coordinator for SolarEdge MeterProxy."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_REFRESH_RATE,
    DEFAULT_REFRESH_RATE,
)
from .meter_devices import MeterDeviceFactory

_LOGGER = logging.getLogger(__name__)


class SolarEdgeMeterProxyCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from meter device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.meter_device = None
        
        refresh_rate = entry.data.get(CONF_REFRESH_RATE, DEFAULT_REFRESH_RATE)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=refresh_rate),
        )

    async def _async_setup(self) -> None:
        """Set up the meter device."""
        try:
            self.meter_device = await MeterDeviceFactory.create_device(
                self.hass, self.entry.data
            )
        except Exception as ex:
            _LOGGER.error("Failed to set up meter device: %s", ex)
            raise UpdateFailed(f"Failed to set up meter device: {ex}") from ex

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        if self.meter_device is None:
            await self._async_setup()

        try:
            return await self.meter_device.async_read_values()
        except Exception as ex:
            raise UpdateFailed(f"Error communicating with meter: {ex}") from ex