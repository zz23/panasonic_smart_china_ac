from homeassistant.components.switch import SwitchEntity

from .api import PanasonicSmartDevice


async def async_setup_entry(hass, entry, async_add_entities):
    device = PanasonicSmartDevice(hass, entry.data, entry.title)
    entities = [
        PanasonicRemoteSwitch(hass, entry, description)
        for description in device.profile.get("remote_switches", [])
    ]
    async_add_entities(entities, True)


class PanasonicRemoteSwitch(SwitchEntity):
    def __init__(self, hass, entry, description):
        self._device = PanasonicSmartDevice(hass, entry.data, entry.title)
        self._key = description["key"]
        self._on_value = description.get("on", 1)
        self._off_value = description.get("off", 0)
        self._attr_name = f"{entry.title} {description['name']}"
        self._attr_unique_id = (
            f"panasonic_{self._device.device_id}_{self._key}_switch"
        )
        self._attr_available = False
        self._is_on = None

    @property
    def is_on(self):
        return self._is_on

    async def async_update(self):
        params = await self._device.fetch_status()
        if not params:
            self._attr_available = False
            return
        self._update_from_params(params)

    async def async_turn_on(self, **kwargs):
        params = await self._device.send_command({self._key: self._on_value})
        if params:
            self._update_from_params(params)

    async def async_turn_off(self, **kwargs):
        params = await self._device.send_command({self._key: self._off_value})
        if params:
            self._update_from_params(params)

    def _update_from_params(self, params):
        self._attr_available = self._key in params
        value = params.get(self._key)
        self._is_on = value == self._on_value
