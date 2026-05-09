import logging
from datetime import timedelta

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    FAN_AUTO,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.helpers.event import async_track_time_interval

from .api import PanasonicSmartDevice
from .const import CONF_SENSOR_ID, FAN_MUTE

_LOGGER = logging.getLogger(__name__)

POLLING_INTERVAL = timedelta(seconds=15)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up climate entity."""
    async_add_entities([PanasonicACEntity(hass, entry.data, entry.title)])


class PanasonicACEntity(ClimateEntity):
    def __init__(self, hass, config, name):
        self._hass = hass
        self._sensor_id = config[CONF_SENSOR_ID]
        self._device = PanasonicSmartDevice(hass, config, name)
        self._profile = self._device.profile
        self._attr_name = name
        self._attr_unique_id = f"panasonic_{self._device.device_id}"

        self._hvac_map = self._profile.get("hvac_mapping", {})
        self._fan_map = self._profile.get("fan_mapping", {})
        self._fan_overrides = self._profile.get("fan_payload_overrides", {})
        self._vertical_swing_map = self._profile.get("vertical_swing_mapping", {})
        self._horizontal_swing_map = self._profile.get("horizontal_swing_mapping", {})

        self._is_on = False
        self._hvac_mode = next(iter(self._hvac_map.keys()), HVACMode.COOL)
        self._target_temperature = 26.0
        self._fan_mode = FAN_AUTO
        self._swing_mode = self._first_mode(self._vertical_swing_map)
        self._swing_horizontal_mode = self._first_mode(self._horizontal_swing_map)
        self._unsub_polling = None

    @staticmethod
    def _first_mode(mode_map):
        return next(iter(mode_map.keys()), None)

    @staticmethod
    def _mode_from_value(mode_map, value, current_mode=None):
        for name, mapped_value in mode_map.items():
            if mapped_value == value:
                return name
        return current_mode or PanasonicACEntity._first_mode(mode_map)

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._unsub_polling = async_track_time_interval(
            self._hass,
            self._async_update_interval_wrapper,
            POLLING_INTERVAL,
        )
        await self.async_update()

    async def async_will_remove_from_hass(self):
        if self._unsub_polling:
            self._unsub_polling()
            self._unsub_polling = None
        await super().async_will_remove_from_hass()

    async def _async_update_interval_wrapper(self, now):
        await self.async_update()
        self.async_write_ha_state()

    @property
    def supported_features(self):
        features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.FAN_MODE
        )
        if self._vertical_swing_map:
            features |= ClimateEntityFeature.SWING_MODE

        horizontal_feature = getattr(ClimateEntityFeature, "SWING_HORIZONTAL_MODE", 0)
        if self._horizontal_swing_map and horizontal_feature:
            features |= horizontal_feature
        return features

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def min_temp(self):
        return 16.0

    @property
    def max_temp(self):
        return 30.0

    @property
    def target_temperature_step(self):
        return 1.0

    @property
    def hvac_modes(self):
        return [HVACMode.OFF, *self._hvac_map.keys()]

    @property
    def hvac_mode(self):
        if not self._is_on:
            return HVACMode.OFF
        return self._hvac_mode

    @property
    def fan_modes(self):
        modes = list(self._fan_map.keys())
        for mode in self._fan_overrides.keys():
            if mode not in modes:
                modes.append(mode)
        return modes

    @property
    def fan_mode(self):
        return self._fan_mode

    @property
    def swing_modes(self):
        return list(self._vertical_swing_map.keys())

    @property
    def swing_mode(self):
        return self._swing_mode

    @property
    def swing_horizontal_modes(self):
        return list(self._horizontal_swing_map.keys())

    @property
    def swing_horizontal_mode(self):
        return self._swing_horizontal_mode

    @property
    def current_temperature(self):
        state = self._hass.states.get(self._sensor_id)
        if state and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            try:
                return float(state.state)
            except ValueError:
                pass
        return None

    @property
    def target_temperature(self):
        return self._target_temperature

    async def async_update(self):
        res = await self._device.fetch_status()
        if res:
            self._update_local_state(res)

    def _update_local_state(self, res):
        self._is_on = self._device.is_on(res)
        self._target_temperature = self._device.read_target_temperature(
            res,
            self._target_temperature,
        )

        self._hvac_mode = self._mode_from_value(
            self._hvac_map,
            res.get("runMode"),
            self._hvac_mode,
        )

        if (
            res.get("windSet") == 10
            and res.get("muteMode") == 1
            and FAN_MUTE in self._fan_overrides
        ):
            self._fan_mode = FAN_MUTE
        else:
            self._fan_mode = self._mode_from_value(
                self._fan_map,
                res.get("windSet"),
                self._fan_mode,
            )

        self._swing_mode = self._mode_from_value(
            self._vertical_swing_map,
            res.get("portraitWindSet"),
            self._swing_mode,
        )
        self._swing_horizontal_mode = self._mode_from_value(
            self._horizontal_swing_map,
            res.get("orientationWindSet"),
            self._swing_horizontal_mode,
        )

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.OFF:
            await self._send_command({"runStatus": self._device.power_off_value})
            return

        p_mode = self._hvac_map.get(hvac_mode)
        if p_mode is None:
            _LOGGER.warning("Unsupported HVAC mode requested: %s", hvac_mode)
            return
        await self._send_command(
            {"runStatus": self._device.power_on_value, "runMode": p_mode}
        )

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        await self._send_command(self._device.build_temperature_payload(temp))

    async def async_set_fan_mode(self, fan_mode):
        if fan_mode in self._fan_overrides:
            changes = self._fan_overrides[fan_mode].copy()
        else:
            val = self._fan_map.get(fan_mode)
            if val is None:
                _LOGGER.warning("Unsupported fan mode requested: %s", fan_mode)
                return
            changes = {"windSet": val}
            if FAN_MUTE in self._fan_overrides:
                changes["muteMode"] = 0
        await self._send_command(changes)

    async def async_set_swing_mode(self, swing_mode):
        val = self._vertical_swing_map.get(swing_mode)
        if val is None:
            _LOGGER.warning("Unsupported vertical swing mode requested: %s", swing_mode)
            return
        await self._send_command({"portraitWindSet": val})

    async def async_set_swing_horizontal_mode(self, swing_horizontal_mode):
        val = self._horizontal_swing_map.get(swing_horizontal_mode)
        if val is None:
            _LOGGER.warning(
                "Unsupported horizontal swing mode requested: %s",
                swing_horizontal_mode,
            )
            return
        await self._send_command({"orientationWindSet": val})

    async def async_turn_on(self):
        await self._send_command({"runStatus": self._device.power_on_value})

    async def async_turn_off(self):
        await self._send_command({"runStatus": self._device.power_off_value})

    async def _send_command(self, changes):
        params = await self._device.send_command(changes)
        if params:
            self._update_local_state(params)
            self.async_write_ha_state()
