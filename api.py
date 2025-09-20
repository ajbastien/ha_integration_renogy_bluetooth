"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

import logging

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .renogy.device import RenogyDeviceData
from .renogy.device_dc_charger import DCChargerDevice
from .renogy.device_inverter import InverterDevice
from .renogy.device_shunt import ShuntDevice
from .renogy.device_test import TestDevice

_LOGGER = logging.getLogger(__name__)


class API:
    """Class for example API."""

    def __init__(self, mac: str, name: str, device_type: str) -> None:
        """Initialise."""
        self.mac = mac
        self.name = name
        self.device_name = None
        self.device_type = device_type
        self.lastUpdateValid: bool = False

    # If you want to change this value, also change the device_unique_id in renogy/device.py
    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return "renogy_" + self.mac.replace(":", "_")

    # def connect(self) -> bool:
    #     """Connect to api."""
    #     _LOGGER.debug("Connecting to api with MAC %s", self.mac)
    #     self.device_name = "RGT_S39E5"

    #     if self.name != "" and self.device_type != "":
    #         self.connected = True
    #         return True
    #     raise APIAuthError("Error connecting to api. Invalid name or device_type.")

    # def disconnect(self) -> bool:
    #     """Disconnect from api."""
    #     self.connected = False
    #     return True

    async def get_devices(self, hass: HomeAssistant) -> list[RenogyDeviceData]:
        """Get devices on api."""
        self.lastUpdateValid = False

        ble_device = None
        if self.device_type != "TestDevice":
            #service_info = bluetooth.async_last_service_info(hass, self.mac, connectable=True)
            #_LOGGER.debug("%s - Service Info: %s", self.name, service_info)
            ble_device = bluetooth.async_ble_device_from_address(hass, self.mac)
            if not ble_device:
                raise ConfigEntryNotReady(
                    f"Could not find Renogy device with address {self.mac}"
                )
            self.device_name = ble_device.name
        else:
            self.device_name = "Test_A1234"

        devicesRet = []
        if self.device_type == "Inverter":
            device_instance = InverterDevice(
                mac=self.mac, device_name=self.device_name, name=self.name
            )
            devicesRet = await device_instance.execute(ble_device)
        elif self.device_type == "DcDcCharger":
            device_instance = DCChargerDevice(
                mac=self.mac, device_name=self.device_name, name=self.name
            )
            devicesRet = await device_instance.execute(ble_device)
        elif self.device_type == "SmartShunt300":
            device_instance = ShuntDevice(
                mac=self.mac, device_name=self.device_name, name=self.name
            )
            devicesRet = await device_instance.execute(ble_device)
        elif self.device_type == "TestDevice":
            device_instance = TestDevice(
                mac=self.mac, device_name=self.device_name, name=self.name
            )
            devicesRet = await device_instance.execute(None)

        if len(devicesRet) == 0:
            _LOGGER.error("%s - Getting 0 devices from api: %s", self.name, self.mac)
            raise APIConnectionError(
                f"Could get entities from Renogy device with address {self.mac}"
            )

        _LOGGER.debug("%s - api.get_devices: %s", self.name, devicesRet)
        self.lastUpdateValid = True

        return devicesRet


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
