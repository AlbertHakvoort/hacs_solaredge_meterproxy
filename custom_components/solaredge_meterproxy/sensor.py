"""Sensor platform for SolarEdge MeterProxy integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


class P1MeterProxySensor(SensorEntity):
    """Representation of a P1 meter proxy sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        sensor_key: str,
        name: str,
        unit: str,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry
        self._sensor_key = sensor_key
        self._name = name
        self._unit = unit
        self._device_class = device_class
        self._state_class = state_class
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"SolarEdge MeterProxy {self._name}"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the device class."""
        return self._device_class

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class."""
        return self._state_class

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self._get_p1_value()

    def _get_p1_value(self) -> float:
        """Get value from P1 entity based on sensor key."""
        config = self._entry.data
        
        # Map sensor keys to P1 entity config keys
        entity_mapping = {
            "power_active": "p1_power_entity",
            "l1_power_active": "p1_power_l1_entity", 
            "l2_power_active": "p1_power_l2_entity",
            "l3_power_active": "p1_power_l3_entity",
            "l1n_voltage": "p1_voltage_l1_entity",
            "l2n_voltage": "p1_voltage_l2_entity",
            "l3n_voltage": "p1_voltage_l3_entity",
            "l1_current": "p1_current_l1_entity",
            "l2_current": "p1_current_l2_entity", 
            "l3_current": "p1_current_l3_entity",
        }
        
        entity_config_key = entity_mapping.get(self._sensor_key)
        if not entity_config_key:
            # For unmapped sensors, return calculated or default values
            if self._sensor_key == "voltage_ln":
                # Return average voltage
                v1 = self._get_entity_value(config.get("p1_voltage_l1_entity"))
                v2 = self._get_entity_value(config.get("p1_voltage_l2_entity"))  
                v3 = self._get_entity_value(config.get("p1_voltage_l3_entity"))
                voltages = [v for v in [v1, v2, v3] if v > 0]
                return sum(voltages) / len(voltages) if voltages else 230.0
            elif self._sensor_key == "frequency":
                return 50.0  # Standard EU frequency
            return 0.0
            
        entity_id = config.get(entity_config_key)
        return self._get_entity_value(entity_id)

    def _get_entity_value(self, entity_id: str | None) -> float:
        """Get numeric value from Home Assistant entity."""
        if not entity_id:
            return 0.0
            
        try:
            state = self.hass.states.get(entity_id)
            if state and state.state not in ["unknown", "unavailable"]:
                return float(state.state)
        except (ValueError, TypeError):
            pass
        
        return 0.0

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "SolarEdge MeterProxy",
            "manufacturer": "SolarEdge MeterProxy",
            "model": "P1 Virtual Meter",
            "sw_version": "1.0.2",
        }


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SolarEdge MeterProxy sensors from a config entry."""
    
    entities = [
        P1MeterProxySensor(
            hass,
            entry,
            "power_active",
            "Total Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l1_power_active",
            "L1 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l2_power_active",
            "L2 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l3_power_active",
            "L3 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "voltage_ln",
            "Line to Neutral Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l1n_voltage",
            "L1-N Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l2n_voltage",
            "L2-N Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l3n_voltage",
            "L3-N Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l1_current",
            "L1 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l2_current",
            "L2 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "l3_current",
            "L3 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        P1MeterProxySensor(
            hass,
            entry,
            "frequency",
            "Line Frequency",
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            SensorStateClass.MEASUREMENT,
        ),
    ]

    async_add_entities(entities)