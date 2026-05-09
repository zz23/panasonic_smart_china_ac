from homeassistant.components.button import ButtonEntity

from .api import PanasonicSmartDevice


async def async_setup_entry(hass, entry, async_add_entities):
    device = PanasonicSmartDevice(hass, entry.data, entry.title)
    entities = [
        PanasonicRemoteButton(hass, entry, description)
        for description in device.profile.get("remote_buttons", [])
    ]
    async_add_entities(entities)


class PanasonicRemoteButton(ButtonEntity):
    def __init__(self, hass, entry, description):
        self._device = PanasonicSmartDevice(hass, entry.data, entry.title)
        self._key = description["key"]
        self._press_value = description.get("press", 1)
        self._toggle = description.get("toggle", False)
        self._attr_name = f"{entry.title} {description['name']}"
        self._attr_unique_id = (
            f"panasonic_{self._device.device_id}_{self._key}_button"
        )

    async def async_press(self):
        if not self._toggle:
            await self._device.send_command({self._key: self._press_value})
            return

        params = await self._device.fetch_status()
        if params and self._device.is_on(params):
            await self._device.send_command({self._key: self._device.power_off_value})
        else:
            await self._device.send_command({self._key: self._device.power_on_value})
