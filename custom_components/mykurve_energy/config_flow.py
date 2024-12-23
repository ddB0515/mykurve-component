"""Config flow for MyKurve Energy integration."""

from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN
from mykurve import MyKurveApi

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class MyKurveEnergyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyKurve Energy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            api = MyKurveApi()
            try:
                auth = api.get_token(username, password)
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                username = user_input[CONF_USERNAME]
                await self.async_set_unique_id(username)
                self._abort_if_unique_id_configured()
                data = {
                    CONF_EMAIL: password,
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                }
                self._async_abort_entries_match(data)
                return self.async_create_entry(title=email, data=data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )