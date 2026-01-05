"""Config flow for SolarEdge MeterProxy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_SERVER_IP,
    CONF_SERVER_PORT,
    CONF_METER_TYPE,
    CONF_METER_HOST,
    CONF_METER_PORT,
    CONF_METER_ADDRESS,
    CONF_METER_MODBUS_ADDRESS,
    CONF_REFRESH_RATE,
    CONF_LOG_LEVEL,
    CONF_CT_CURRENT,
    CONF_CT_INVERTED,
    CONF_PHASE_OFFSET,
    CONF_SERIAL_NUMBER,
    CONF_PROTOCOL,
    DEFAULT_SERVER_IP,
    DEFAULT_SERVER_PORT,
    DEFAULT_METER_PORT,
    DEFAULT_METER_ADDRESS,
    DEFAULT_METER_MODBUS_ADDRESS,
    DEFAULT_REFRESH_RATE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_CT_CURRENT,
    DEFAULT_CT_INVERTED,
    DEFAULT_PHASE_OFFSET,
    DEFAULT_SERIAL_NUMBER,
    DEFAULT_PROTOCOL,
    METER_TYPES,
    PROTOCOL_TYPES,
    LOG_LEVELS,
)

_LOGGER = logging.getLogger(__name__)

"""Config flow for SolarEdge MeterProxy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_SERVER_IP,
    CONF_SERVER_PORT,
    CONF_METER_TYPE,
    CONF_METER_HOST,
    CONF_METER_PORT,
    CONF_METER_ADDRESS,
    CONF_METER_MODBUS_ADDRESS,
    CONF_REFRESH_RATE,
    CONF_LOG_LEVEL,
    CONF_CT_CURRENT,
    CONF_CT_INVERTED,
    CONF_PHASE_OFFSET,
    CONF_SERIAL_NUMBER,
    CONF_PROTOCOL,
    DEFAULT_SERVER_IP,
    DEFAULT_SERVER_PORT,
    DEFAULT_METER_PORT,
    DEFAULT_METER_ADDRESS,
    DEFAULT_METER_MODBUS_ADDRESS,
    DEFAULT_REFRESH_RATE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_CT_CURRENT,
    DEFAULT_CT_INVERTED,
    DEFAULT_PHASE_OFFSET,
    DEFAULT_SERIAL_NUMBER,
    DEFAULT_PROTOCOL,
    METER_TYPES,
    PROTOCOL_TYPES,
    LOG_LEVELS,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Basic validation - just return success for now
    return {"title": f"SolarEdge MeterProxy ({data[CONF_METER_HOST]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SolarEdge MeterProxy."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._server_config: dict[str, Any] = {}
        self._meter_config: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                self._server_config = user_input
                return await self.async_step_meter()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_SERVER_IP, default=DEFAULT_SERVER_IP): cv.string,
            vol.Required(CONF_SERVER_PORT, default=DEFAULT_SERVER_PORT): cv.port,
            vol.Required(CONF_PROTOCOL, default=DEFAULT_PROTOCOL): vol.In(PROTOCOL_TYPES),
            vol.Required(CONF_LOG_LEVEL, default=DEFAULT_LOG_LEVEL): vol.In(LOG_LEVELS),
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )

    async def async_step_meter(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the meter configuration step."""
        errors = {}

        if user_input is not None:
            try:
                self._meter_config = user_input
                
                # Combine server and meter config
                config_data = {**self._server_config, **self._meter_config}
                
                info = await validate_input(self.hass, config_data)
                
                return self.async_create_entry(title=info["title"], data=config_data)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_METER_TYPE, default="sdm120"): vol.In(METER_TYPES),
            vol.Required(CONF_METER_HOST): cv.string,
            vol.Required(CONF_METER_PORT, default=DEFAULT_METER_PORT): cv.port,
            vol.Required(CONF_METER_ADDRESS, default=DEFAULT_METER_ADDRESS): vol.Range(min=1, max=247),
            vol.Required(CONF_METER_MODBUS_ADDRESS, default=DEFAULT_METER_MODBUS_ADDRESS): vol.Range(min=1, max=247),
            vol.Required(CONF_REFRESH_RATE, default=DEFAULT_REFRESH_RATE): vol.Range(min=1, max=300),
            vol.Optional(CONF_CT_CURRENT, default=DEFAULT_CT_CURRENT): cv.positive_int,
            vol.Optional(CONF_CT_INVERTED, default=DEFAULT_CT_INVERTED): vol.In([0, 1]),
            vol.Optional(CONF_PHASE_OFFSET, default=DEFAULT_PHASE_OFFSET): vol.Range(min=0, max=360),
            vol.Optional(CONF_SERIAL_NUMBER, default=DEFAULT_SERIAL_NUMBER): cv.positive_int,
        })

        return self.async_show_form(
            step_id="meter", 
            data_schema=data_schema, 
            errors=errors
        )