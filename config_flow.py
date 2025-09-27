"""Config flow for Renogy Bluetooth Integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothServiceInfo,
    async_discovered_service_info,
)
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_SCAN_INTERVAL, CONF_TYPE
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector
from homeassistant.data_entry_flow import FlowResult

from .api import APIAuthError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MIN_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

# data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC, description={"suggested_value": ""}): str,
        vol.Required(CONF_NAME, description={"suggested_value": ""}): str,
        vol.Required(
            CONF_TYPE,
            description={"suggested_value": ""},  # ): str,
        ): selector(
            {
                "select": {
                    "options": [
                        "Inverter",
                        "SmartShunt300",
                        "DcDcCharger",
                        "TestDevice",
                    ],
                }
            }
        ),
    }
)

class RenogyBluetoothDeviceUpdateError(Exception):
    """Custom error class for device updates."""


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_NAME], data[CONF_TYPE]
    # )

    # api = API(data[CONF_MAC], data[CONF_NAME], data[CONF_TYPE])
    if (
        len(data[CONF_MAC]) != 17
        or len(data[CONF_NAME]) == 0
        or len(data[CONF_TYPE]) == 0
    ):
        _LOGGER.error("Error connecting to api. Invalid name or device_type")
        raise APIAuthError("Error connecting to api. Invalid name or device_type.")

    # try:
    #     await hass.async_add_executor_job(api.connect)
    #     # If you cannot connect, raise CannotConnect
    #     # If the authentication is wrong, raise InvalidAuth
    # except APIAuthError as err:
    #     raise InvalidAuth from err
    # except APIConnectionError as err:
    #     raise CannotConnect from err

    return {"title": f"Renogy Bluetooth Integration - {data[CONF_MAC]}"}


class RBConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renogy Bluetooth Integration."""

    VERSION = 1
    _input_data: dict[str, Any]

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_device: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RBOptionsFlowHandler()

    async def discovery_get_data(
        self, discovery_info: BluetoothServiceInfo
    ) -> dict[str, Any]:
        retData = {}
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, discovery_info.address
        )
        if ble_device is None:
            _LOGGER.error("no ble_device in discovery_get_data")
            raise RenogyBluetoothDeviceUpdateError("No ble_device for %s", discovery_info.address)

        retData[CONF_NAME] = ble_device.name
        retData[CONF_MAC] = ble_device.address

        if ble_device.name.startswith("RTMShunt"):
            retData[CONF_TYPE] = "SmartShunt300"
        elif ble_device.name.startswith("BT-TH-"):
            retData[CONF_TYPE] = "DcDcCharger"
        elif ble_device.name.startswith("RNGRIU"):
            retData[CONF_TYPE] = "Inverter"
        else:
            retData[CONF_TYPE] = "Unknown"

        return retData

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfo
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.info("Discovered BT device: %s", discovery_info)
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        _LOGGER.debug("async_step_bluetooth unique id - %s", discovery_info.address)

        deviceData = await self.discovery_get_data(discovery_info)
        _LOGGER.info("Discovered discovery_get_data: %s", deviceData)

        self._discovered_device = deviceData
        self.context["title_placeholders"] = {CONF_NAME: deviceData[CONF_NAME]}

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        _LOGGER.debug("async_step_bluetooth_confirm - %s", user_input)
        _LOGGER.debug("async_step_bluetooth_confirm curr ids - %s", self._async_current_ids())
        _LOGGER.debug("async_step_bluetooth_confirm discov - %s", self._discovered_device)

        if user_input is not None:
            return self.async_create_entry(
                title=self.context["title_placeholders"][CONF_NAME], data=user_input
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders=self.context["title_placeholders"],
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAC, default=self._discovered_device[CONF_MAC]): str,
                    vol.Required(CONF_NAME, default=self._discovered_device[CONF_NAME]): str,
                    vol.Required(
                        CONF_TYPE,
                        default=self._discovered_device[CONF_TYPE],  # ): str,
                    ): selector(
                        {
                            "select": {
                                "options": [
                                    "Inverter",
                                    "SmartShunt300",
                                    "DcDcCharger",
                                    "TestDevice",
                                ],
                            }
                        }
                    ),
                }
            ),
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        # Called when you initiate adding an integration via the UI
        errors: dict[str, str] = {}

        _LOGGER.debug("async_step_user - %s", user_input)
        _LOGGER.debug("async_step_user current ids - %s", self._async_current_ids())

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.
            try:
                # Validate that the setup data is valid and if not handle errors.
                # The errors["base"] values match the values in your strings.json and translation files.
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                # Validation was successful, so create a unique id for this instance of your integration
                # and create the config entry.
                _LOGGER.debug("async_step_user unique id - before - %s", user_input[CONF_MAC])
                await self.async_set_unique_id(user_input[CONF_MAC])
                self._abort_if_unique_id_configured()
                _LOGGER.debug("async_step_user unique id - %s", user_input[CONF_MAC])
                return self.async_create_entry(title=info["title"], data=user_input)

        # Show initial form.
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add reconfigure step to allow to reconfigure a config entry."""
        # This methid displays a reconfigure option in the integration and is
        # different to options.
        # It can be used to reconfigure any of the data submitted when first installed.
        # This is optional and can be removed if you do not want to allow reconfiguration.
        errors: dict[str, str] = {}
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        if user_input is not None:
            try:
                user_input[CONF_MAC] = config_entry.data[CONF_MAC]
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    config_entry,
                    unique_id=config_entry.unique_id,
                    data={**config_entry.data, **user_input},
                    reason="reconfigure_successful",
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=config_entry.data[CONF_NAME]): str,
                    vol.Required(
                        CONF_TYPE,
                        default=config_entry.data[CONF_TYPE],  # ): str,
                    ): selector(
                        {
                            "select": {
                                "options": [
                                    "Inverter",
                                    "SmartShunt300",
                                    "DcDcCharger",
                                    "TestDevice",
                                ],
                            }
                        }
                    ),
                }
            ),
            errors=errors,
        )


class RBOptionsFlowHandler(OptionsFlow):
    """Handles the options flow."""

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        # It is recommended to prepopulate options fields with default values if available.
        # These will be the same default values you use on your coordinator for setting variable values
        # if the option has not been set.
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): (vol.All(vol.Coerce(int), vol.Clamp(min=MIN_SCAN_INTERVAL))),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
