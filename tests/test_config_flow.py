"""Test the SolarEdge MeterProxy config flow."""
import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.solaredge_meterproxy.const import DOMAIN
from tests.conftest import TEST_CONFIG


async def test_config_flow_user_step(hass: HomeAssistant):
    """Test the user step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_config_flow_complete(hass: HomeAssistant):
    """Test completing the config flow."""
    # Start the flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Complete user step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "server_ip": TEST_CONFIG["server_ip"],
            "server_port": TEST_CONFIG["server_port"],
            "protocol": TEST_CONFIG["protocol"],
            "log_level": TEST_CONFIG["log_level"],
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "meter"
    assert result["errors"] == {}

    # Complete meter step
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "meter_type": TEST_CONFIG["meter_type"],
            "meter_host": TEST_CONFIG["meter_host"],
            "meter_port": TEST_CONFIG["meter_port"],
            "meter_address": TEST_CONFIG["meter_address"],
            "meter_modbus_address": TEST_CONFIG["meter_modbus_address"],
            "refresh_rate": TEST_CONFIG["refresh_rate"],
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"].startswith("SolarEdge MeterProxy")
    assert result["data"] == TEST_CONFIG