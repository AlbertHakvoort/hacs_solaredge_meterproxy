"""Test configuration for SolarEdge MeterProxy integration."""
import pytest
from homeassistant.core import HomeAssistant

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture
async def hass_instance():
    """Return a Home Assistant instance for testing."""
    pass  # pytest-homeassistant-custom-component will provide this


# Example test configuration data
TEST_CONFIG = {
    "server_ip": "127.0.0.1",
    "server_port": 5502,
    "protocol": "tcp",
    "meter_type": "generic",
    "meter_host": "192.168.1.100",
    "meter_port": 502,
    "meter_address": 1,
    "meter_modbus_address": 2,
    "refresh_rate": 5,
    "log_level": "INFO",
}