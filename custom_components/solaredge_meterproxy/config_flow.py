"""Config flow for SolarEdge MeterProxy integration."""
from __future__ import annotations

import logging
import socket
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def get_local_ip() -> str:
    """Get the local IP address of Home Assistant."""
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "192.168.1.100"  # Fallback


def get_power_entities(hass: HomeAssistant) -> dict[str, str]:
    """Get available power/energy entities from Home Assistant."""
    entities = {}
    registry = er.async_get(hass)
    
    for entity_id in hass.states.async_entity_ids():
        if any(keyword in entity_id.lower() for keyword in ["power", "energie", "energy", "watt"]):
            state = hass.states.get(entity_id)
            if state and state.state not in ["unknown", "unavailable"]:
                # Get friendly name from registry or state
                entity_entry = registry.async_get(entity_id)
                name = entity_entry.name if entity_entry and entity_entry.name else state.attributes.get("friendly_name", entity_id)
                unit = state.attributes.get("unit_of_measurement", "")
                entities[entity_id] = f"{name} ({unit})" if unit else name
    
    return entities


def get_voltage_entities(hass: HomeAssistant) -> dict[str, str]:
    """Get available voltage entities from Home Assistant."""
    entities = {}
    registry = er.async_get(hass)
    
    for entity_id in hass.states.async_entity_ids():
        if any(keyword in entity_id.lower() for keyword in ["voltage", "volt", "spanning"]):
            state = hass.states.get(entity_id)
            if state and state.state not in ["unknown", "unavailable"]:
                entity_entry = registry.async_get(entity_id)
                name = entity_entry.name if entity_entry and entity_entry.name else state.attributes.get("friendly_name", entity_id)
                unit = state.attributes.get("unit_of_measurement", "")
                entities[entity_id] = f"{name} ({unit})" if unit else name
    
    return entities


def get_current_entities(hass: HomeAssistant) -> dict[str, str]:
    """Get available current entities from Home Assistant."""
    entities = {}
    registry = er.async_get(hass)
    
    for entity_id in hass.states.async_entity_ids():
        if any(keyword in entity_id.lower() for keyword in ["current", "ampere", "stroom"]):
            state = hass.states.get(entity_id)
            if state and state.state not in ["unknown", "unavailable"]:
                entity_entry = registry.async_get(entity_id)
                name = entity_entry.name if entity_entry and entity_entry.name else state.attributes.get("friendly_name", entity_id)
                unit = state.attributes.get("unit_of_measurement", "")
                entities[entity_id] = f"{name} ({unit})" if unit else name
    
    return entities


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

        # Get available entities for dropdowns
        power_entities = get_power_entities(self.hass)
        voltage_entities = get_voltage_entities(self.hass)
        current_entities = get_current_entities(self.hass)
        
        # Get default server IP
        default_ip = get_local_ip()
        
        data_schema = vol.Schema({
            vol.Required("server_ip", default=default_ip): cv.string,
            vol.Required("server_port", default=5502): cv.port,
            vol.Required("protocol", default="tcp"): vol.In(["tcp", "rtu"]),
            vol.Optional("p1_power_entity"): vol.In(power_entities) if power_entities else cv.string,
            vol.Optional("p1_voltage_l1_entity"): vol.In(voltage_entities) if voltage_entities else cv.string,
            vol.Optional("p1_voltage_l2_entity"): vol.In(voltage_entities) if voltage_entities else cv.string,
            vol.Optional("p1_voltage_l3_entity"): vol.In(voltage_entities) if voltage_entities else cv.string,
            vol.Optional("p1_current_l1_entity"): vol.In(current_entities) if current_entities else cv.string,
            vol.Optional("p1_current_l2_entity"): vol.In(current_entities) if current_entities else cv.string,
            vol.Optional("p1_current_l3_entity"): vol.In(current_entities) if current_entities else cv.string,
            vol.Optional("p1_power_l1_entity"): vol.In(power_entities) if power_entities else cv.string,
            vol.Optional("p1_power_l2_entity"): vol.In(power_entities) if power_entities else cv.string,
            vol.Optional("p1_power_l3_entity"): vol.In(power_entities) if power_entities else cv.string,
            vol.Required("meter_modbus_address", default=2): vol.Range(min=1, max=247),
            vol.Required("refresh_rate", default=5): vol.Range(min=1, max=300),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "local_ip": default_ip,
                "entity_count": f"{len(power_entities)} power, {len(voltage_entities)} voltage, {len(current_entities)} current entities found"
            }
        )