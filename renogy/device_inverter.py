"""Defines the Renogy inverter device class and its data parsing logic.

This module provides:
- InverterDevice: a class for Renogy inverter devices
- Data parsing methods for inverter statistics, device ID, model, and load info
"""

import logging

from .device import RenogyDevice, RenogyDeviceData, RenogyDeviceType
from .utils import bytes_to_int

_LOGGER = logging.getLogger(__name__)

FUNCTION = {3: "READ", 6: "WRITE"}

CHARGING_STATE = {
    0: "deactivated",
    1: "constant current",
    2: "constant voltage",
    4: "floating",
    6: "battery activation",
    7: "battery disconnecting",
}


class InverterDevice(RenogyDevice):
    """Renogy Inverter device implementation."""

    def __init__(self, mac: str, device_name: str, name: str) -> None:
        """Initialise."""
        super().__init__(mac, device_name, name, device_type="Inverter")
        self.NOTIFY_SERVICE_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
        self.WRITE_SERVICE_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"
        self.ha_device_name = "Renogy Inverter"
        self.model = "Unknown"

        self.sections = [
            {"register": 4311, "words": 8},
            {"register": 4109, "words": 1},
            {"register": 4000, "words": 10},
            {"register": 4408, "words": 6},
            # {'register': 4327, 'words': 7},
        ]

    def parse_section(self, bs: bytearray, section_index: int) -> dict:
        """Parse a section of data from the device."""
        if section_index == 0:
            return self.parse_inverter_model(bs)
        if section_index == 1:
            return self.parse_device_id(bs)
        if section_index == 2:
            return self.parse_inverter_stats(bs)
        if section_index == 3:
            return self.parse_load_info(bs)
        # if section_index == 4:
        #     return self.parse_charging_info(bs)

        return {"valid": False, "entities": []}

    def parse_inverter_model(self, bs):
        """Parse the inverter model from the device."""
        self.model = (bs[3:19]).decode("utf-8").rstrip("\x00")

        return {"valid": True, "entities": []}

    def parse_device_id(self, bs):
        """Parse the device ID from the device."""
        ret_dev = []
        entity_id = 2
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.INT_DATA,
            name="Device ID",
            state=bytes_to_int(bs, 3, 2),
            attributes={},
        )
        ret_dev.append(dev)
        return {"valid": True, "entities": ret_dev}

    def parse_inverter_stats(self, bs):
        """Parse inverter statistics from the device."""
        ret_dev = []
        entity_id = 3
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Input Voltage",
            state=bytes_to_int(bs, 3, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 4
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Input Current",
            state=bytes_to_int(bs, 5, 2, scale=0.01),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 5
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Output Voltage",
            state=bytes_to_int(bs, 7, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 6
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Output Current",
            state=bytes_to_int(bs, 9, 2, scale=0.01),
            is_main=True,
            attributes={"model": self.model},
        )
        ret_dev.append(dev)

        entity_id = 7
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.INT_DATA,
            name="Output Frequency",
            state=bytes_to_int(bs, 11, 2, scale=0.01),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 8
        dev = RenogyDeviceData(
            device_id=2,
            device_name="Main Battery",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Battery Voltage",
            state=bytes_to_int(bs, 13, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 9
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.TEMPERATURE_SENSOR,
            name="Inverter Temperature",
            state=bytes_to_int(bs, 15, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 10
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.INT_DATA,
            name="Input Frequency",
            state=bytes_to_int(bs, 21, 2, scale=0.01),
            attributes={},
        )
        ret_dev.append(dev)

        return {"valid": True, "entities": ret_dev}

    # def parse_charging_info(self, bs):
    #     ret_dev = []
    #     entity_id = 11
    #     dev = RenogyDeviceData(
    #             device_id=2,
    #             device_name="Main Battery",
    #             device_unique_id=self.device_unique_id + f"_{entity_id}",
    #             device_type=RenogyDeviceType.PERCENTAGE,
    #             name='Battery Percentage',
    #             state=bytes_to_int(bs, 3, 2)
    #         )
    #     ret_dev.append(dev)

    #     entity_id = 12
    #     dev = RenogyDeviceData(
    #             device_id=1,
    #             device_name=self.ha_device_name,
    #             device_unique_id=self.device_unique_id + f"_{entity_id}",
    #             device_type=RenogyDeviceType.CURRENT_SENSOR,
    #             name='Charging Current',
    #             state=bytes_to_int(bs, 5, 2, scale=0.1, signed=True)
    #         )
    #     ret_dev.append(dev)

    #     entity_id = 13
    #     dev = RenogyDeviceData(
    #             device_id=1,
    #             device_name=self.ha_device_name,
    #             device_unique_id=self.device_unique_id + f"_{entity_id}",
    #             device_type=RenogyDeviceType.VOLTAGE_SENSOR,
    #             name='Solar Voltage',
    #             state=bytes_to_int(bs, 7, 2, scale=0.1)
    #         )
    #     ret_dev.append(dev)

    #     entity_id = 14
    #     dev = RenogyDeviceData(
    #             device_id=1,
    #             device_name=self.ha_device_name,
    #             device_unique_id=self.device_unique_id + f"_{entity_id}",
    #             device_type=RenogyDeviceType.CURRENT_SENSOR,
    #             name='Solar Current',
    #             state=bytes_to_int(bs, 9, 2, scale=0.1)
    #         )
    #     ret_dev.append(dev)

    #     entity_id = 15
    #     dev = RenogyDeviceData(
    #             device_id=1,
    #             device_name=self.ha_device_name,
    #             device_unique_id=self.device_unique_id + f"_{entity_id}",
    #             device_type=RenogyDeviceType.POWER_SENSOR,
    #             name='Solar Power',
    #             state=bytes_to_int(bs, 11, 2)
    #         )
    #     ret_dev.append(dev)

    #     entity_id = 16
    #     dev = RenogyDeviceData(
    #             device_id=1,
    #             device_name=self.ha_device_name,
    #             device_unique_id=self.device_unique_id + f"_{entity_id}",
    #             device_type=RenogyDeviceType.STRING_DATA,
    #             name='Charging Status',
    #             state=CHARGING_STATE.get(bytes_to_int(bs, 13, 2))
    #         )
    #     ret_dev.append(dev)

    #     entity_id = 17
    #     dev = RenogyDeviceData(
    #             device_id=1,
    #             device_name=self.ha_device_name,
    #             device_unique_id=self.device_unique_id + f"_{entity_id}",
    #             device_type=RenogyDeviceType.POWER_SENSOR,
    #             name='Charge Power',
    #             state=bytes_to_int(bs, 15, 2)
    #         )
    #     ret_dev.append(dev)

    #     return {"valid": True, "entities": ret_dev}

    def parse_load_info(self, bs):
        """Parse load information from the device."""
        ret_dev = []
        entity_id = 18
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Load Current",
            state=bytes_to_int(bs, 3, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 19
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.POWER_SENSOR,
            name="Load Active Power",
            state=bytes_to_int(bs, 5, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 20
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.POWER_SENSOR,
            name="Load Apparent Power",
            state=bytes_to_int(bs, 7, 2),
            attributes={},
        )
        ret_dev.append(dev)

        # entity_id = 21
        # dev = RenogyDeviceData(
        #         device_id=1,
        #         device_name=self.ha_device_name,
        #         device_unique_id=self.device_unique_id + f"_{entity_id}",
        #         device_type=RenogyDeviceType.CURRENT_SENSOR,
        #         name='Line Charging Current',
        #         state=bytes_to_int(bs, 11, 2, scale=0.1)
        #     )
        # ret_dev.append(dev)

        entity_id = 22
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.PERCENTAGE,
            name="Load Percentage",
            state=bytes_to_int(bs, 13, 2),
            attributes={},
        )
        ret_dev.append(dev)

        return {"valid": True, "entities": ret_dev}
