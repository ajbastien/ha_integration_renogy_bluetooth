"""Renogy Bluetooth device abstraction and BLE communication.

This module defines the base classes and utilities for Renogy Bluetooth devices,
including BLE communication logic, device data models, and abstract parsing methods.
"""

import abc
import asyncio
from dataclasses import dataclass
from enum import StrEnum
import logging
import traceback

from bleak import BleakClient, BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection

from .utils import bytes_to_int, crc16_modbus, int_to_bytes

_LOGGER = logging.getLogger(__name__)


class RenogyDeviceType(StrEnum):
    """Device types."""

    TEMPERATURE_SENSOR = "temperature_sensor"
    DOOR_SENSOR = "door_sensor"
    VOLTAGE_SENSOR = "voltage_sensor"
    CURRENT_SENSOR = "current_sensor"
    AMP_HOURS_SENSOR = "amp_hours_sensor"
    POWER_SENSOR = "power_sensor"
    ENERGY_STORAGE = "energy_storage"
    PERCENTAGE = "percentage"
    STRING_DATA = "string_data"
    INT_DATA = "int_data"


@dataclass
class RenogyDeviceData:
    """API device."""

    device_id: int
    device_name: str
    device_unique_id: str
    device_type: RenogyDeviceType
    name: str
    state: str | float | int | bool
    is_main: bool = False  # True if this is the main entity for the device
    attributes: dict = None  # Additional attributes for the entity


class RenogyDevice(abc.ABC):
    """Abstract base class for Renogy Bluetooth devices.

    Handles BLE communication, data parsing, and device metadata for Renogy sensors.
    Child classes must implement the parse_section method to extract device-specific data.
    """

    def __init__(self, mac: str, device_name: str, name: str, device_type: str) -> None:
        """Initialise."""
        self.mac = mac
        self.device_name = device_name
        self.ha_device_name = "Default Device Name"
        self.name = name
        self.device_type = device_type
        self.function = 3
        self.device_id = 255
        self.sections = []
        self.section_index = 0
        self._notification_event = asyncio.Event()  # Add event
        self.ret_dev_data = []
        self.NOTIFY_SERVICE_UUID = None
        self.WRITE_SERVICE_UUID = None
        self.READ_OPERATION = 3
        self.client = None

    def add_devices(self) -> None:
        """Add basic device information entities to the device data list.

        This method appends entities for MAC address, device name, and friendly name
        to the ret_dev_data list for Home Assistant entity creation.
        """

        for dev in self.ret_dev_data:
            if dev.is_main:
                dev.attributes["mac"] = self.mac
                dev.attributes["device_name"] = self.device_name.strip()
                dev.attributes["config_name"] = self.name

    # If you want to change this value, also change the controller_name in api.py
    @property
    def device_unique_id(self) -> str:
        """Return the name of the controller."""
        return "renogy_" + self.mac.lower().replace(":", "_") + "_id"

    async def notification_callback(
        self, characteristic: BleakGATTCharacteristic, data: bytearray
    ):
        """Handle notifications from the BLE device."""
        operation = bytes_to_int(data, 1, 1)
        _LOGGER.debug(
            "%s - notification_callback %d - %d l:%d - %s", self.name,
            operation,
            self.section_index,
            len(data),
            data.hex(),
        )

        if operation == self.READ_OPERATION:
            items = self.parse_section(data, self.section_index)
            if items["valid"]:
                self.ret_dev_data.extend(items["entities"])
                # _LOGGER.debug("%s - ret_dev_data: %s", self.name, self.ret_dev_data)
                self._notification_event.set()  # Trigger event
        else:
            _LOGGER.warning(
                "%s - Unknown operation response received, ignoring for now.  Looking for %d %d", self.name,
                self.READ_OPERATION,
                len(self.sections),
            )

    def create_generic_read_request(self, device_id, function, regAddr, readWrd):
        """Create a generic read request payload."""
        data = None
        if regAddr is not None and readWrd is not None:
            data = []
            data.append(device_id)
            data.append(function)
            data.append(int_to_bytes(regAddr, 0))
            data.append(int_to_bytes(regAddr, 1))
            data.append(int_to_bytes(readWrd, 0))
            data.append(int_to_bytes(readWrd, 1))

            crc = crc16_modbus(bytes(data))
            data.append(crc[0])
            data.append(crc[1])
            _LOGGER.debug("%s - create_request_payload %s => %s", self.name, regAddr, data)
        return data

    async def read_section(self, client: BleakClient):
        """Read a section of data from the BLE device."""
        index = self.section_index
        if len(self.sections) == 0:
            _LOGGER.error("RenogyDevice cannot be used directly")

        self._notification_event.clear()  # Reset event before sending request

        request = self.create_generic_read_request(
            self.device_id,
            self.function,
            self.sections[index]["register"],
            self.sections[index]["words"],
        )
        await client.write_gatt_char(
            self.WRITE_SERVICE_UUID, bytearray(request), response=False
        )

    async def printServices(self, client: BleakClient):
        """Print all services, characteristics, and descriptors of the BLE device."""
        services = client.services
        for service in services:
            _LOGGER.debug("Service: %s", service)
            for char in service.characteristics:
                _LOGGER.debug("  -> Characteristic: %s", char)
                for desc in char.descriptors:
                    _LOGGER.debug("    -> Descriptor: %s", desc)

    async def execute(self, ble_device: BLEDevice) -> list[RenogyDeviceData]:
        """Execute the BLE communication."""
        self.client = None

        try:
            if self.WRITE_SERVICE_UUID != "TEST":
                if self.NOTIFY_SERVICE_UUID is None:
                    _LOGGER.error("%s - No NOTIFY_SERVICE_UUID defined", self.name)
                    return []

                # _LOGGER.debug("%s - Connecting to device %s", self.name, ble_device.address)
                self.client = await establish_connection(
                    BleakClient, ble_device, ble_device.address
                )

                if not self.client.is_connected:
                    _LOGGER.error("%s - Failed to connect to device %s", self.name, ble_device.address)
                    self._raise_connection_error(ble_device.address)

                # await self.printServices(self.client)

                _LOGGER.debug("%s - Starting Notification for %s", self.name, self.NOTIFY_SERVICE_UUID)
                await self.client.start_notify(
                    self.NOTIFY_SERVICE_UUID, self.notification_callback
                )

                countsent = 0
                recieved = 0
                while self.section_index < len(self.sections):
                    while countsent < 2 and recieved == 0:
                        if self.WRITE_SERVICE_UUID is not None:
                            await self.read_section(self.client)

                        countwait = 0
                        while countwait < 25 and not self._notification_event.is_set():
                            await asyncio.sleep(.2)
                            countwait = countwait + 1

                        _LOGGER.debug("%s - Event: %d", self.name, self._notification_event.is_set())
                        countsent = countsent + 1
                        if self._notification_event.is_set():
                            recieved = 1

                    if recieved == 1:
                        self.section_index += 1
                        countsent = 0
                        recieved = 0
                    else:
                        self._raise_communication_error(self.name)

                await self.client.disconnect()
            else:
                _LOGGER.warning("Simulated device - no BLE actions")
                items = self.parse_section(b"ab232", self.section_index)

                if items["valid"]:
                    self.ret_dev_data.extend(items["entities"])
                    self._notification_event.set()  # Trigger event
                # _LOGGER.debug("ret_dev_data: %s", self.ret_dev_data)

        except Exception as e:  # noqa: BLE001
            _LOGGER.error("%s - Error processing device: %s", self.name, e)
            traceback.print_exc()
            if self.client is not None:
                await self.client.disconnect()
            return []

        self.add_devices()
        return self.ret_dev_data

    def validateLimits(self, value, min, max) -> bool:
        if value < min or value > max:
            return False
        return True

    @abc.abstractmethod
    def parse_section(self, bs: bytearray, section_index: int) -> dict:
        """Parse the section data. Must be implemented in child classes."""

    def _raise_connection_error(self, address: str) -> None:
        raise DeviceConnectionError(f"Failed to connect to device {address}")

    def _raise_communication_error(self, address: str) -> None:
        raise DeviceCommunicationError(f"Failed to communicate to device {address}")

class DeviceConnectionError(Exception):
    """Exception class for connection error."""

class DeviceCommunicationError(Exception):
    """Exception class for communication error."""
