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
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SolarEdgeMeterProxyCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SolarEdge MeterProxy sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "energy_active",
            "Total Active Energy",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "import_energy_active",
            "Import Active Energy",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "export_energy_active",
            "Export Active Energy",
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "power_active",
            "Total Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l1_power_active",
            "L1 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l2_power_active",
            "L2 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l3_power_active",
            "L3 Active Power",
            UnitOfPower.WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "voltage_ln",
            "Line to Neutral Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l1n_voltage",
            "L1-N Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l2n_voltage",
            "L2-N Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l3n_voltage",
            "L3-N Voltage",
            UnitOfElectricPotential.VOLT,
            SensorDeviceClass.VOLTAGE,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l1_current",
            "L1 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l2_current",
            "L2 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l3_current",
            "L3 Current",
            UnitOfElectricCurrent.AMPERE,
            SensorDeviceClass.CURRENT,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "frequency",
            "Frequency",
            UnitOfFrequency.HERTZ,
            SensorDeviceClass.FREQUENCY,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "power_factor",
            "Power Factor",
            None,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l1_power_factor",
            "L1 Power Factor",
            None,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l2_power_factor",
            "L2 Power Factor",
            None,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
        ),
        SolarEdgeMeterProxySensor(
            coordinator,
            entry,
            "l3_power_factor",
            "L3 Power Factor",
            None,
            SensorDeviceClass.POWER_FACTOR,
            SensorStateClass.MEASUREMENT,
        ),
    ]

    async_add_entities(entities)


class SolarEdgeMeterProxySensor(CoordinatorEntity, SensorEntity):
    """Representation of a SolarEdge MeterProxy sensor."""

    def __init__(
        self,
        coordinator: SolarEdgeMeterProxyCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_key = sensor_key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"

    @property
    def device_info(self):
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "SolarEdge MeterProxy",
            "manufacturer": "SolarEdge MeterProxy",
            "model": "Meter Proxy",
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None