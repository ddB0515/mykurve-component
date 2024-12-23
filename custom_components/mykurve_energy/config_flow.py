"""Config flow for MyKurve Energy integration."""

from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN
from mykurve import MyKurveApi

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

async def validate_auth(username: str, password: str) -> None:
    """Validates a auth token.

    Raises a ValueError if the auth token is invalid.
    """
    try:
        api = MyKurveApi()
        await api.get_token(username, password).
    except Exception:
        raise ValueError

class MyKurveEnergyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyKurve Energy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup"""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            try:
                await validate_auth(userName, password)
            except ValueError:
                errors["base"] = "auth"

            data = {
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                }
            # User is done adding repos, create the config entry.
            return self.async_create_entry(title=DOMAIN, data=data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )