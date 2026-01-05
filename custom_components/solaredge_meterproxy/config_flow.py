"""Config flow for SolarEdge MeterProxy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required("server_ip", default="0.0.0.0"): cv.string,
    vol.Required("server_port", default=5502): cv.port,
    vol.Required("protocol", default="tcp"): vol.In(["tcp", "rtu"]),
    vol.Required("meter_type", default="generic"): vol.In(["generic", "sdm120", "sdm230"]),
    vol.Required("meter_host", default="192.168.1.100"): cv.string,
    vol.Required("meter_port", default=502): cv.port,
    vol.Required("meter_address", default=1): vol.Range(min=1, max=247),
    vol.Required("meter_modbus_address", default=2): vol.Range(min=1, max=247),
    vol.Required("refresh_rate", default=5): vol.Range(min=1, max=300),
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SolarEdge MeterProxy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                title = f"SolarEdge MeterProxy ({user_input['meter_host']})"
                return self.async_create_entry(title=title, data=user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )