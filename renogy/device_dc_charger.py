"""Device class for Renogy DC-DC Charger integration.

This module defines the DCChargerDevice class and related constants for parsing
and representing data from Renogy DC-DC Charger devices.
"""

import logging

from .device import RenogyDevice, RenogyDeviceData, RenogyDeviceType
from .utils import bytes_to_int

_LOGGER = logging.getLogger(__name__)

FUNCTION = {3: "READ", 6: "WRITE"}

CHARGING_STATE = {
    0: "deactivated",
    1: "activated",
    2: "mppt",
    3: "equalizing",
    4: "boost",
    5: "floating",
    6: "current limiting",
    8: "alternator direct",
}

BATTERY_TYPE = {1: "open", 2: "sealed", 3: "gel", 4: "lithium", 5: "custom"}


class DCChargerDevice(RenogyDevice):
    """Renogy DC-DC Charger device implementation."""

    def __init__(self, mac: str, device_name: str, name: str) -> None:
        """Initialise."""
        super().__init__(mac, device_name, name, device_type="DcDcCharger")
        self.NOTIFY_SERVICE_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
        self.WRITE_SERVICE_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"
        self.ha_device_name = "Renogy DC-DC Charger"
        self.model = "Unknown"
        self.battery_type = "Unknown"

        self.sections = [
            {"register": 12, "words": 8},
            {"register": 26, "words": 1},
            {"register": 288, "words": 3},
            {"register": 57348, "words": 1},
            {"register": 256, "words": 30},
        ]

    def parse_section(self, bs: bytearray, section_index: int) -> dict:
        """Parse a section of data from the device."""
        if section_index == 0:
            return self.parse_device_info(bs)
        if section_index == 1:
            return self.parse_device_address(bs)
        if section_index == 2:
            return self.parse_state(bs)
        if section_index == 3:
            return self.parse_battery_type(bs)
        if section_index == 4:
            return self.parse_charging_info(bs)

        return {"valid": False, "entities": []}

    def parse_device_info(self, bs):
        """Parse device information from the device."""
        self.model = (bs[3:19]).decode("utf-8").strip()
        return {"valid": True, "entities": []}

    def parse_device_address(self, bs):
        """Parse the device address from the device."""
        ret_dev = []
        entity_id = 2
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.INT_DATA,
            name="Device ID",
            state=bytes_to_int(bs, 4, 1),
            attributes={},
        )
        ret_dev.append(dev)
        return {"valid": True, "entities": ret_dev}

    def parse_charging_info(self, bs):
        """Parse charging information from the device."""
        ret_dev = []
        entity_id = 3
        dev = RenogyDeviceData(
            device_id=2,
            device_name="Main Battery",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.PERCENTAGE,
            name="Battery Percent",
            state=bytes_to_int(bs, 3, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 4
        dev = RenogyDeviceData(
            device_id=2,
            device_name="Main Battery",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Battery Voltage",
            state=bytes_to_int(bs, 5, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 5
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Combined Charge Current",
            state=bytes_to_int(bs, 7, 2, scale=0.01),
            is_main=True,
            attributes={
                "model": self.model,
                "battery_type": self.battery_type,
            },
        )
        ret_dev.append(dev)

        entity_id = 6
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.TEMPERATURE_SENSOR,
            name="Controller Temperature",
            state=bytes_to_int(bs, 9, 1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 7
        dev = RenogyDeviceData(
            device_id=2,
            device_name="Main Battery",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.TEMPERATURE_SENSOR,
            name="Battery Temperature",
            state=bytes_to_int(bs, 10, 1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 8
        dev = RenogyDeviceData(
            device_id=3,
            device_name="Alternator",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Alternator Voltage",
            state=bytes_to_int(bs, 11, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 9
        dev = RenogyDeviceData(
            device_id=3,
            device_name="Alternator",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Alternator Current",
            state=bytes_to_int(bs, 13, 2, scale=0.01),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 10
        dev = RenogyDeviceData(
            device_id=3,
            device_name="Alternator",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.POWER_SENSOR,
            name="Alternator Power",
            state=bytes_to_int(bs, 15, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 11
        dev = RenogyDeviceData(
            device_id=4,
            device_name="Solar",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Solar Voltage",
            state=bytes_to_int(bs, 17, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 12
        dev = RenogyDeviceData(
            device_id=4,
            device_name="Solar",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Solar Current",
            state=bytes_to_int(bs, 19, 2, scale=0.01),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 13
        dev = RenogyDeviceData(
            device_id=4,
            device_name="Solar",
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.POWER_SENSOR,
            name="Solar Power",
            state=bytes_to_int(bs, 21, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 14
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Batt Min Voltage Today",
            state=bytes_to_int(bs, 25, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 15
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.VOLTAGE_SENSOR,
            name="Batt Max Voltage Today",
            state=bytes_to_int(bs, 27, 2, scale=0.1),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 16
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.CURRENT_SENSOR,
            name="Batt Max Current Today",
            state=bytes_to_int(bs, 29, 2, scale=0.01),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 17
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.POWER_SENSOR,
            name="Batt Charging Power Today",
            state=bytes_to_int(bs, 33, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 18
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.AMP_HOURS_SENSOR,
            name="Charging Amp Hours Today",
            state=bytes_to_int(bs, 37, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 19
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.ENERGY_STORAGE,
            name="Power Generation Today",
            state=bytes_to_int(bs, 41, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 20
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.INT_DATA,
            name="Total Working Days",
            state=bytes_to_int(bs, 45, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 21
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.INT_DATA,
            name="Count Battery Overdischarged",
            state=bytes_to_int(bs, 47, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 22
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.INT_DATA,
            name="Count Battery Fully Charged",
            state=bytes_to_int(bs, 49, 2),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 23
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.AMP_HOURS_SENSOR,
            name="Total Battery AH Accumulated",
            state=bytes_to_int(bs, 51, 4),
            attributes={},
        )
        ret_dev.append(dev)

        entity_id = 24
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.ENERGY_STORAGE,
            name="Power Generation Total",
            state=bytes_to_int(bs, 59, 4),
            attributes={},
        )
        ret_dev.append(dev)

        return {"valid": True, "entities": ret_dev}

    def parse_battery_type(self, bs):
        """Parse battery type from the device."""
        self.battery_type = BATTERY_TYPE.get(bytes_to_int(bs, 3, 2))
        return {"valid": True, "entities": []}

    def parse_state(self, bs):
        """Parse device state from the device."""
        ret_dev = []

        entity_id = 25
        dev = RenogyDeviceData(
            device_id=1,
            device_name=self.ha_device_name,
            device_unique_id=self.device_unique_id + f"_{entity_id}",
            device_type=RenogyDeviceType.STRING_DATA,
            name="Charge State",
            state=CHARGING_STATE.get(bytes_to_int(bs, 2, 1)),
            attributes={},
        )
        ret_dev.append(dev)

        # alarms = {}

        # byte = bytes_to_int(bs, 4, 1)
        # alarms['low_temp_shutdown'] = (byte >> 11) & 1
        # alarms['bms_overcharge_protection'] = (byte >> 10) & 1
        # alarms['starter_reverse_polarity'] = (byte >> 9) & 1
        # alarms['alternator_over_voltage'] = (byte >> 8) & 1
        # alarms['alternator_over_current'] = (byte >> 4) & 1
        # alarms['controller_over_temp_2'] = (byte >> 3) & 1

        # byte = bytes_to_int(bs, 6, 1)
        # alarms['solar_reverse_polarity'] = (byte >> 12) & 1
        # alarms['solar_over_voltage'] = (byte >> 9) & 1
        # alarms['solar_over_current'] = (byte >> 7) & 1
        # alarms['battery_over_temperature'] = (byte >> 6) & 1
        # alarms['controller_over_temp'] = (byte >> 5) & 1
        # alarms['battery_low_voltage'] = (byte >> 2) &  1
        # alarms['battery_over_voltage'] = (byte >> 1) &  1
        # alarms['battery_over_discharge'] = byte &  1

        # key = next((key for key, value in alarms.items() if value > 0), None)
        # if (key != None): data['error'] = key

        return {"valid": True, "entities": ret_dev}
