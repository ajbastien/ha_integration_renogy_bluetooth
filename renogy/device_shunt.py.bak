"""SmartShunt 300 device parsing for Renogy Bluetooth integration.

This module defines the ShuntDevice class for parsing battery and sensor data
from Renogy SmartShunt 300 devices via Bluetooth.
"""

import logging

from .device import RenogyDevice, RenogyDeviceData, RenogyDeviceType
from .utils import bytes_to_int

_LOGGER = logging.getLogger(__name__)

# Read and parse Smart Shunt 300 specific data


class ShuntDevice(RenogyDevice):
    """Renogy Smart Shunt 300 device implementation."""

    def __init__(self, mac: str, device_name: str, name: str) -> None:
        """Initialise."""
        super().__init__(mac, device_name, name, device_type="SmartShunt300")
        self.NOTIFY_SERVICE_UUID = "0000c411-0000-1000-8000-00805f9b34fb"
        self.READ_OPERATION = 87
        self.ha_device_name = "Renogy Battery"

        self.sections = [{"register": 256, "words": 110}]

        self.first_parse = True

    def parse_section(self, bs: bytearray, section_index: int) -> dict:
        """Parse a section of data from the device."""
        if (
            section_index != 0 or not self.first_parse or len(bs) < 110
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
            state=bytes_to_int(bs, 34, 2, scale=0.1),  # 0xA6 (#1),
            is_main=True,
            attributes={},
        )
        ret_dev.append(dev)

        volts = bytes_to_int(bs, 25, 3, scale=0.001)  # 0xA6 (#1)
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
            state=bytes_to_int(bs, 30, 2, scale=0.001),  # 0xA6 (#2)
            attributes={},
        )
        ret_dev.append(dev)

        amps = bytes_to_int(bs, 21, 3, scale=0.001, signed=True)  # 0xA4 (#1)
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
            state=bytes_to_int(bs, 66, 2, scale=0.1),  # 0xAD (#3
            attributes={},
        )
        ret_dev.append(dev)

        # data['temperature_2'] = 0.00 if bytes_to_int(bs, 71, 1) == 0 else bytes_to_int(bs, 70, 3, scale = 0.001) # 0xAD (#4)
        # unknown values:
        # - time_remaining
        # - discharge_duration
        # - consumed_amp_hours

        return {"valid": True, "entities": ret_dev}
