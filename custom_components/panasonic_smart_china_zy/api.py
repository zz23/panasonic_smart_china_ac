import logging

import async_timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_CONTROLLER_MODEL,
    CONF_DEVICE_ID,
    CONF_SSID,
    CONF_TOKEN,
    CONF_USR_ID,
    SAFE_KEYS,
    SUPPORTED_CONTROLLERS,
    URL_GET,
    URL_SET,
)

_LOGGER = logging.getLogger(__name__)


class PanasonicSmartDevice:
    def __init__(self, hass, config, name):
        self.hass = hass
        self.usr_id = config[CONF_USR_ID]
        self.device_id = config[CONF_DEVICE_ID]
        self.token = config[CONF_TOKEN]
        self.ssid = config[CONF_SSID]
        self.name = name

        model = config.get(CONF_CONTROLLER_MODEL, "CZ-RD501DW2")
        if model == "CZ-RD501DW2" and "CS-ZY35K410" in name.upper():
            model = "CS-ZY35K410"

        self.model = model
        self.profile = SUPPORTED_CONTROLLERS.get(model)
        if not self.profile:
            _LOGGER.error("Controller model %s not found, using default.", model)
            self.profile = SUPPORTED_CONTROLLERS["CZ-RD501DW2"]

        self.url_get = self.profile.get("get_url", URL_GET)
        self.url_set = self.profile.get("set_url", URL_SET)
        self.last_params = {}

    @property
    def power_on_value(self):
        return self.profile.get("power_on_value", 1)

    @property
    def power_off_value(self):
        return self.profile.get("power_off_value", 0)

    @property
    def temp_scale(self):
        return self.profile.get("temp_scale", 2)

    @property
    def temperature_keys(self):
        return self.profile.get("temperature_keys", ["setTemperature"])

    @property
    def current_temperature_keys(self):
        return self.profile.get(
            "current_temperature_keys",
            ["inhaleTemperature", "insideTemperature", "preTemperature"],
        )

    def is_on(self, params):
        return params.get("runStatus") == self.power_on_value

    def read_target_temperature(self, params, fallback=26.0):
        for key in self.temperature_keys:
            value = params.get(key)
            if value is None:
                continue
            try:
                return float(value) / self.temp_scale
            except (TypeError, ValueError):
                continue
        return fallback

    def build_temperature_payload(self, temperature):
        return {self.temperature_keys[0]: int(temperature * self.temp_scale)}

    def read_current_temperature(self, params):
        for key in self.current_temperature_keys:
            value = params.get(key)
            if value is None:
                continue
            try:
                temperature = float(value)
            except (TypeError, ValueError):
                continue
            if temperature > 80:
                temperature = temperature / self.temp_scale
            return temperature
        return None

    async def fetch_status(self):
        headers = self._get_headers()
        payload = {
            "id": 100,
            "usrId": self.usr_id,
            "deviceId": self.device_id,
            "token": self.token,
        }

        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(5):
                response = await session.post(
                    self.url_get,
                    json=payload,
                    headers=headers,
                    ssl=False,
                )
                json_data = await response.json()

                if json_data.get("errorCode") in ["3003", "3004"]:
                    _LOGGER.error("SSID expired.")
                    return None

                results = json_data.get("results")
                if isinstance(results, dict) and "runStatus" in results:
                    self.last_params = results
                    return results
        except Exception as err:
            _LOGGER.debug("Fetch status failed: %s", err)
        return None

    async def send_command(self, changes):
        latest_params = await self.fetch_status()

        if latest_params:
            current_params = latest_params.copy()
        else:
            _LOGGER.warning("Could not fetch latest status, using cached params.")
            current_params = self.last_params.copy()

        current_params.update(changes)
        params = {key: value for key, value in current_params.items() if key in SAFE_KEYS}

        headers = self._get_headers()
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(10):
                await session.post(
                    self.url_set,
                    json={
                        "id": 200,
                        "usrId": self.usr_id,
                        "deviceId": self.device_id,
                        "token": self.token,
                        "params": params,
                    },
                    headers=headers,
                    ssl=False,
                )

                self.last_params = current_params
                return current_params
        except Exception as err:
            _LOGGER.error("Set failed: %s", err)
        return None

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X)",
            "xtoken": f"SSID={self.ssid}",
            "DNT": "1",
            "Origin": "https://app.psmartcloud.com",
            "X-Requested-With": "XMLHttpRequest",
        }
