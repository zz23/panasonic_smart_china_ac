from homeassistant.components.select import SelectEntity

from .api import PanasonicSmartDevice


async def async_setup_entry(hass, entry, async_add_entities):
    device = PanasonicSmartDevice(hass, entry.data, entry.title)
    entities = [
        PanasonicRemoteSelect(hass, entry, description)
        for description in device.profile.get("remote_selects", [])
    ]
    async_add_entities(entities, True)


class PanasonicRemoteSelect(SelectEntity):
    def __init__(self, hass, entry, description):
        self._device = PanasonicSmartDevice(hass, entry.data, entry.title)
        self._key = description["key"]
        self._options_map = description["options"]
        self._value_to_option = {
            value: option for option, value in self._options_map.items()
        }
        self._attr_name = f"{entry.title} {description['name']}"
        self._attr_unique_id = (
            f"panasonic_{self._device.device_id}_{self._key}_select"
        )
        self._attr_options = list(self._options_map.keys())
        self._attr_available = False
        self._attr_current_option = None

    async def async_update(self):
        params = await self._device.fetch_status()
        if not params:
            self._attr_available = False
            return
        self._update_from_params(params)

    async def async_select_option(self, option):
        value = self._options_map.get(option)
        if value is None:
            return
        params = await self._device.send_command({self._key: value})
        if params:
            self._update_from_params(params)

    def _update_from_params(self, params):
        self._attr_available = self._key in params
        self._attr_current_option = self._value_to_option.get(params.get(self._key))
