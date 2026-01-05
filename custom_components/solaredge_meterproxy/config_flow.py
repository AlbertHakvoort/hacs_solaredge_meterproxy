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

def get_p1_entities(hass: HomeAssistant) -> dict[str, str]:
    """Get available P1 meter entities from Home Assistant."""
    entities = {}
    for entity_id in hass.states.async_entity_ids():
        if "power" in entity_id.lower() or "voltage" in entity_id.lower() or "current" in entity_id.lower():
            state = hass.states.get(entity_id)
            if state and state.state not in ["unknown", "unavailable"]:
                entities[entity_id] = f"{entity_id} ({state.state} {state.attributes.get('unit_of_measurement', '')})"
    return entities

DATA_SCHEMA = vol.Schema({
    vol.Required("server_ip", default="0.0.0.0"): cv.string,
    vol.Required("server_port", default=5502): cv.port,
    vol.Required("protocol", default="tcp"): vol.In(["tcp", "rtu"]),
    vol.Optional("p1_power_entity"): cv.string,
    vol.Optional("p1_voltage_l1_entity"): cv.string,
    vol.Optional("p1_voltage_l2_entity"): cv.string,
    vol.Optional("p1_voltage_l3_entity"): cv.string,
    vol.Optional("p1_current_l1_entity"): cv.string,
    vol.Optional("p1_current_l2_entity"): cv.string,
    vol.Optional("p1_current_l3_entity"): cv.string,
    vol.Optional("p1_power_l1_entity"): cv.string,
    vol.Optional("p1_power_l2_entity"): cv.string,
    vol.Optional("p1_power_l3_entity"): cv.string,
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
                title = f"SolarEdge MeterProxy (Port {user_input['server_port']})"
                return self.async_create_entry(title=title, data=user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Get available P1 entities for dropdown suggestions
        p1_entities = get_p1_entities(self.hass)
        _LOGGER.info(f"Found P1 entities: {list(p1_entities.keys())}")

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "p1_entities": "\n".join([f"• {entity_id}" for entity_id in list(p1_entities.keys())[:10]])
            },
        )