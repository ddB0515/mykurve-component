"""Config Flow for MyKurve Energy integration"""

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from homeassistant.exceptions import HomeAssistantError
from mykurve import MyKurveApi

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class MyKurveConfigFlow(ConfigFlow, domain=DOMAIN):
    """MyKurve Energy config flow."""

    VERSION = 1

    async def _validate_input(self, user_input):
        api = MyKurveApi()

        try:
            async with asyncio.timeout(30):
                token = await api.get_token(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
        except TimeoutError as err:
            raise CannotConnect from err
        except Exception:
            raise ValueError

        return token is not None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle gathering login info"""
        errors = {}
        if user_input is not None:
            try:
                await self._validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{DOMAIN}_{user_input[CONF_USERNAME]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"MyKurve Energy: {user_input[CONF_USERNAME]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""