"""Constants for the SolarEdge MeterProxy integration."""

DOMAIN = "solaredge_meterproxy"

# Configuration constants
CONF_SERVER_IP = "server_ip"
CONF_SERVER_PORT = "server_port"
CONF_METER_TYPE = "meter_type"
CONF_METER_HOST = "meter_host" 
CONF_METER_PORT = "meter_port"
CONF_METER_ADDRESS = "meter_address"
CONF_METER_MODBUS_ADDRESS = "meter_modbus_address"
CONF_REFRESH_RATE = "refresh_rate"
CONF_LOG_LEVEL = "log_level"
CONF_CT_CURRENT = "ct_current"
CONF_CT_INVERTED = "ct_inverted"
CONF_PHASE_OFFSET = "phase_offset"
CONF_SERIAL_NUMBER = "serial_number"
CONF_PROTOCOL = "protocol"

# Default values
DEFAULT_SERVER_IP = "0.0.0.0"
DEFAULT_SERVER_PORT = 5502
DEFAULT_METER_PORT = 502
DEFAULT_METER_ADDRESS = 1
DEFAULT_METER_MODBUS_ADDRESS = 2
DEFAULT_REFRESH_RATE = 5
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_CT_CURRENT = 5
DEFAULT_CT_INVERTED = 0
DEFAULT_PHASE_OFFSET = 120
DEFAULT_SERIAL_NUMBER = 987654
DEFAULT_PROTOCOL = "tcp"

# Meter types
METER_TYPES = [
    "sdm120",
    "sdm230", 
    "sdm630",
    "influxdb",
    "mqtt",
    "mqttP1",
    "generic"
]

# Protocol types
PROTOCOL_TYPES = ["tcp", "rtu"]

# Log levels
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]

# Attributes
ATTR_ENERGY_ACTIVE = "energy_active"
ATTR_POWER_ACTIVE = "power_active"
ATTR_VOLTAGE = "voltage"
ATTR_CURRENT = "current"
ATTR_FREQUENCY = "frequency"
ATTR_POWER_FACTOR = "power_factor"