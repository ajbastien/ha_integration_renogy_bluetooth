"""Interfaces with the Renogy Bluetooth Integration api sensors."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MyConfigEntry
from .const import DOMAIN
from .coordinator import RenogyCoordinator
from .renogy.device import RenogyDeviceData, RenogyDeviceType

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Sensors."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: RenogyCoordinator = config_entry.runtime_data.coordinator

    # Enumerate all the sensors in your data value from your DataUpdateCoordinator and add an instance of your sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured
    sensors = []

    for device in coordinator.data.devices:
        if device.device_type == RenogyDeviceType.TEMPERATURE_SENSOR:
            ts = TemperatureSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.PERCENTAGE:
            ts = PercentageSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.VOLTAGE_SENSOR:
            ts = VoltageSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.CURRENT_SENSOR:
            ts = CurrentSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.POWER_SENSOR:
            ts = PowerSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.ENERGY_STORAGE:
            ts = EnergyStorageSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.AMP_HOURS_SENSOR:
            ts = AmpHourSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.INT_DATA:
            ts = IntSensor(coordinator, device)
            sensors.append(ts)
        if device.device_type == RenogyDeviceType.STRING_DATA:
            ts = StringSensor(coordinator, device)
            sensors.append(ts)

    # Create the sensors.
    async_add_entities(sensors)


def get_renogy_device_info(
    coordinator: RenogyCoordinator, device: RenogyDeviceData
) -> DeviceInfo:
    """Return device information."""
    # Identifiers are what group entities into the same device.
    # If your device is created elsewhere, you can just specify the indentifiers parameter.
    # If your device connects via another device, add via_device parameter with the indentifiers of that device.
    return DeviceInfo(
        name=device.device_name,
        manufacturer="Renogy",
        model=coordinator.data.device_type,
        sw_version="1.0",
        identifiers={
            (
                DOMAIN,
                f"{coordinator.data.controller_name}-{device.device_id}",
            )
        },
    )


class PowerSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.POWER

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfPower.WATT

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class EnergyStorageSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.ENERGY_STORAGE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfEnergy.WATT_HOUR

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class AmpHourSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    # @property
    # def device_class(self) -> str:
    #     """Return device class."""
    #     # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
    #     return SensorDeviceClass.ENERGY_STORAGE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return "Ah"

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class CurrentSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.CURRENT

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfElectricCurrent.AMPERE

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class VoltageSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.VOLTAGE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfElectricPotential.VOLT

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class PercentageSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.BATTERY

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return PERCENTAGE

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class TemperatureSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)
        # Device(device_id=1, device_unique_id='C4_D3_6A_93_B2_3B_T1', device_type=<DeviceType.TEMPERATURE_SENSOR: 'TEMPERATURE_SENSOR'>, name='Temp Sensor 1', state=17)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_class(self) -> str:
        """Return device class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-device-classes
        return SensorDeviceClass.TEMPERATURE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int | float:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return float(self.device.state)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of temperature."""
        return UnitOfTemperature.CELSIUS

    @property
    def state_class(self) -> str | None:
        """Return state class."""
        # https://developers.home-assistant.io/docs/core/entity/sensor/#available-state-classes
        return SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class IntSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)
        # Device(device_id=1, device_unique_id='C4_D3_6A_93_B2_3B_T1', device_type=<DeviceType.TEMPERATURE_SENSOR: 'TEMPERATURE_SENSOR'>, name='Temp Sensor 1', state=17)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> int:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return int(self.device.state)

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes


class StringSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a sensor."""

    def __init__(
        self, coordinator: RenogyCoordinator, device: RenogyDeviceData
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self.device = device
        self.device_id = device.device_id
        # _LOGGER.debug("Init Device: %s", self.device)
        # Device(device_id=1, device_unique_id='C4_D3_6A_93_B2_3B_T1', device_type=<DeviceType.TEMPERATURE_SENSOR: 'TEMPERATURE_SENSOR'>, name='Temp Sensor 1', state=17)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update sensor with latest data from coordinator."""
        # This method is called by your DataUpdateCoordinator when a successful update runs.
        self.device = self.coordinator.get_device_by_unique_id(
            self.device.device_unique_id
        )
        # _LOGGER.debug("Update Device: %s", self.device)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""

        return get_renogy_device_info(self.coordinator, self.device)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device.name

    @property
    def native_value(self) -> str:
        """Return the state of the entity."""
        # Using native value and native unit of measurement, allows you to change units
        # in Lovelace and HA will automatically calculate the correct value.
        return self.device.state

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.device.device_unique_id}"

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        # Add any additional attributes you want on your sensor.
        return self.device.attributes
