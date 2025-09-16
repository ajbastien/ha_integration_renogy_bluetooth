"""Test implementation for Renogy Smart Shunt 300 device.

This module defines a test device class for simulating Renogy Smart Shunt 300 data parsing.
"""

import logging

from .device import RenogyDevice, RenogyDeviceData, RenogyDeviceType

_LOGGER = logging.getLogger(__name__)

# Read and parse Smart Shunt 300 specific data


class TestDevice(RenogyDevice):
    """Renogy Smart Shunt 300 device implementation."""

    def __init__(self, mac: str, device_name: str, name: str) -> None:
        """Initialise."""
        super().__init__(mac, device_name, name, device_type="SmartShunt300")
        self.NOTIFY_SERVICE_UUID = "TEST"
        self.WRITE_SERVICE_UUID = "TEST"
        self.ha_device_name = "Renogy Battery"

        self.first_parse = True

        self.sections = [{"register": 256, "words": 110}]

    def parse_section(self, bs: bytearray, section_index: int) -> dict:
        """Parse a section of data from the device."""
        _LOGGER.debug(
            "parse_section called with section_index: %d and data: (%d) %s",
            section_index,
            len(bs),
            bs.hex(),
        )
        if (
            section_index != 0 or not self.first_parse
        ):  # The shunt sends many notifications in a row, we only need the first one
            return {"valid": False, "entities": []}

        self.first_parse = False

        ret_dev = []
        entity_id = 1
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.PERCENTAGE,
            name="Main Battery Percent",
            state=85.2,
            is_main=True,
            attributes={"model": "SmartShunt300"},
        )

        ret_dev.append(dev)

        volts = 13.6
        entity_id = 2
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Main Battery Voltage",
            state=volts,
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 3
        dev = RenogyDeviceData(
            device_id=2,
            device_name="Starter Battery",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Starter Battery Voltage",
            state=12.6,
            attributes={},
        )
        ret_dev.append(dev)

        amps = 3.15
        entity_id = 4
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Charge Amps",
            state=amps,
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 5
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.POWER_SENSOR,
            name="Charge Watts",
            state=volts * amps,
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 6
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.TEMPERATURE_SENSOR,
            name="Main Battery Temperature",
            state=12.1,
            attributes={},
        )
        ret_dev.append(dev)

        volts = 12.45
        entity_id = 7
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Main Battery Voltage (Test)",
            state=volts,
            attributes={"test_attribute": "test_value"},
        )
        ret_dev.append(dev)

        return {"valid": True, "entities": ret_dev}
