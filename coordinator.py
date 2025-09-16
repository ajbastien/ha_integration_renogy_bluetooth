"""Renogy Bluetooth Integration using DataUpdateCoordinator."""

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_SCAN_INTERVAL, CONF_TYPE
from homeassistant.core import DOMAIN as HOMEASSISTANT_DOMAIN, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import API, APIAuthError
from .const import DEFAULT_SCAN_INTERVAL
from .renogy.device import RenogyDeviceData, RenogyDeviceType

_LOGGER = logging.getLogger(__name__)


@dataclass
class RenBtApiData:
    """Class to hold api data."""

    controller_name: str
    device_type: str
    devices: list[RenogyDeviceData]


class RenogyCoordinator(DataUpdateCoordinator):
    """My example coordinator."""

    data: RenBtApiData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.mac = config_entry.data[CONF_MAC]
        self.name2 = config_entry.data[CONF_NAME]
        self.device_name = None
        self.device_type = config_entry.data[CONF_TYPE]

        # set variables from options.  You need a default here incase options have not been set
        self.poll_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{HOMEASSISTANT_DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            # Using config option here but you can just use a value.
            update_interval=timedelta(seconds=self.poll_interval),
        )

        # Initialise your api here
        self.api = API(mac=self.mac, name=self.name2, device_type=self.device_type)

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # if not self.api.connected:
            #     await self.hass.async_add_executor_job(self.api.connect)
            # devices = await self.hass.async_add_executor_job(self.api.get_devices)
            devices = await self.api.get_devices(self.hass)
            self.device_name = self.api.device_name
        except APIAuthError as err:
            _LOGGER.error(err)
            raise UpdateFailed(err) from err
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # What is returned here is stored in self.data by the DataUpdateCoordinator
        return RenBtApiData(self.api.controller_name, self.device_type, devices)

    def get_device_by_unique_id(self, unique_id: str) -> RenogyDeviceData | None:
        """Return device by device id."""
        # Called by the sensors and sensors to get their updated data from self.data
        try:
            return [
                device
                for device in self.data.devices
                if device.device_unique_id == unique_id
            ][0]
        except IndexError as err:
            _LOGGER.error(err)
            return None
