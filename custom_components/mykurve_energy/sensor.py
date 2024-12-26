"""Support for MyKurve Energy Pricing data"""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from mykurve import MyKurveApi

from . import MyKurveAuth
from .const import DOMAIN, CONF_ACC_NUMBER

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=2)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """MyKurve Energy Sensor Setup."""
    myKurveAuth: MyKurveAuth = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([MyKurveSensor(myKurveAuth, entry)], True)


class MyKurveSensor(SensorEntity):
    """Entity object for MyKurve Energy sensor"""

    _attr_attribution = "Data provided by MyKurve Energy"
    _attr_native_unit_of_measurement = f"£/{UnitOfEnergy.KILO_WATT_HOUR}"
    _attr_has_entity_name = True
    _attr_translation_key = "power_price"
    _attributes: dict[str, Any] = {}

    def __init__(self, mykurveauth: MyKurveAuth, entry: ConfigEntry) -> None:
        """Entity object for MyKurve Energy sensor"""
        self._api = MyKurveApi()
        self._mykurve_auth = mykurveauth
        self._entry = entry
        self._price = 0.0

    @property
    def native_value(self):
        """Return the state of the sensor"""
        return self._price

    @property
    def extra_state_attributes(self):
        """Return the state attributes"""
        return self._attributes

    async def async_update(self) -> None:
        """Get the MyKurve Energy data from the web service"""
        # if self._price and self._price.end_at >= utcnow():
        #     return  # Power price data is still valid

        async with asyncio.timeout(30):
            await self._mykurve_auth.async_get_access_token()
            token = self._entry.data[CONF_API_TOKEN]
            acc_number = self._entry.data[CONF_ACC_NUMBER]
            _LOGGER.debug("token: %s - acc_no", token, acc_number)
            dashboard = await self._api.get_dashboard(token, acc_number)
            self._price = dashboard.tariffHistory.tariffInForceNow.rate

        _LOGGER.debug("Pricing data: %s", self._price)