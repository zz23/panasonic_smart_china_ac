from homeassistant.components.climate.const import (
    HVACMode,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
)

DOMAIN = "panasonic_smart_china_zy"

CONF_USR_ID = "usrId"
CONF_DEVICE_ID = "deviceId"
CONF_TOKEN = "token"
CONF_SSID = "SSID"
CONF_SENSOR_ID = "sensor_entity_id"
CONF_CONTROLLER_MODEL = "controller_model"

URL_SET = "https://app.psmartcloud.com/App/ACDevSetStatusInfoAW"
URL_GET = "https://app.psmartcloud.com/App/ACDevGetStatusInfoAW"

FAN_MIN = "Min"
FAN_MAX = "Max"
FAN_MUTE = "Quiet"

SWING_AUTO = "Auto"
SWING_UP = "Up"
SWING_UP_MIDDLE = "Up Middle"
SWING_MIDDLE = "Middle"
SWING_DOWN_MIDDLE = "Down Middle"
SWING_DOWN = "Down"
SWING_LEFT = "Left"
SWING_LEFT_MIDDLE = "Left Middle"
SWING_CENTER = "Center"
SWING_RIGHT_MIDDLE = "Right Middle"
SWING_RIGHT = "Right"

SAFE_KEYS = [
    "runMode",
    "forceRunning",
    "runStatus",
    "remoteForbidMode",
    "remoteMode",
    "setTemperature",
    "setHumidity",
    "windSet",
    "exchangeWindSet",
    "portraitWindSet",
    "orientationWindSet",
    "nanoeG",
    "nanoe",
    "ecoMode",
    "muteMode",
    "filterReset",
    "powerful",
    "powerfulMode",
    "thermoMode",
    "buzzer",
    "autoRunMode",
    "unusualPresent",
    "runForbidden",
    "inhaleTemperature",
    "outsideTemperature",
    "insideHumidity",
    "alarmCode",
    "nanoeModule",
    "TDWindModule",
    "airSupply",
    "autoAi",
    "cleanMode",
    "debugMode",
    "defrost",
    "detectMode",
    "displaySet",
    "douleTemperature",
    "errorStatus",
    "eClean",
    "eeconfirm",
    "electricCurrent",
    "energySaving",
    "enventSet",
    "errorCode",
    "errorCodeW",
    "feelMode",
    "functionMode",
    "gasValue",
    "hcount",
    "heatExchange",
    "heatPump",
    "heatup",
    "humidClean",
    "humiditySet",
    "insideTemperature",
    "ionMode",
    "lamp",
    "mcount",
    "mildew",
    "newair",
    "notice",
    "pm2p5Clean",
    "preMode",
    "preTemperature",
    "quickMode",
    "rader",
    "ratedPower",
    "selfClean",
    "selfNanoe",
    "selfNanoeMode",
    "selfcleanReset",
    "showMode",
    "sleep",
    "sleepCurve",
    "sleepMode",
    "temperature",
    "temperatureSet",
    "temperatureUnit",
    "tempMode",
    "timerSetting",
    "totalElectricity",
    "waterClean",
    "windDirection",
    "windMethod",
    "windMode",
    "windSwing",
]

SUPPORTED_CONTROLLERS = {
    "CZ-RD501DW2": {
        "name": "Panasonic ducted controller CZ-RD501DW2",
        "temp_scale": 2,
        "temperature_keys": ["setTemperature"],
        "power_on_value": 1,
        "power_off_value": 0,
        "hvac_mapping": {
            HVACMode.COOL: 3,
            HVACMode.HEAT: 4,
            HVACMode.DRY: 2,
            HVACMode.AUTO: 0,
        },
        "fan_mapping": {
            FAN_AUTO: 10,
            FAN_MIN: 3,
            FAN_LOW: 4,
            FAN_MEDIUM: 5,
            FAN_HIGH: 6,
            FAN_MAX: 7,
        },
        "fan_payload_overrides": {
            FAN_MUTE: {"windSet": 10, "muteMode": 1}
        },
        "vertical_swing_mapping": {
            SWING_AUTO: 15,
        },
        "horizontal_swing_mapping": {
            SWING_AUTO: 13,
        },
        "remote_switches": [
            {"key": "runStatus", "name": "Power", "on": 1, "off": 0},
            {"key": "muteMode", "name": "Quiet", "on": 1, "off": 0},
            {"key": "powerful", "name": "Powerful", "on": 1, "off": 0},
            {"key": "ecoMode", "name": "Eco", "on": 1, "off": 0},
            {"key": "nanoe", "name": "Nanoe", "on": 1, "off": 0},
            {"key": "nanoeG", "name": "Nanoe-G", "on": 1, "off": 0},
            {"key": "buzzer", "name": "Buzzer", "on": 1, "off": 0},
        ],
        "remote_buttons": [
            {"key": "runStatus", "name": "Power Toggle", "toggle": True},
            {"key": "filterReset", "name": "Filter Reset", "press": 1},
        ],
    },
    "CS-ZY35K410": {
        "name": "Panasonic CS-ZY35K410",
        "set_url": "https://app.psmartcloud.com/App/ACDevSetStatusNewProtocol",
        "temp_scale": 1,
        "temperature_keys": ["setTemperature", "temperatureSet", "temperature"],
        "power_on_value": 48,
        "power_off_value": 49,
        "hvac_mapping": {
            HVACMode.COOL: 66,
            HVACMode.HEAT: 67,
            HVACMode.DRY: 68,
        },
        "fan_mapping": {
            FAN_AUTO: 65,
            FAN_MIN: 49,
            FAN_LOW: 50,
            FAN_MEDIUM: 52,
            FAN_HIGH: 54,
            FAN_MAX: 55,
        },
        "fan_payload_overrides": {},
        "horizontal_swing_mapping": {
            SWING_AUTO: 64,
            SWING_LEFT: 66,
            SWING_LEFT_MIDDLE: 108,
            SWING_CENTER: 67,
            SWING_RIGHT_MIDDLE: 87,
            SWING_RIGHT: 65,
        },
        "vertical_swing_mapping": {
            SWING_AUTO: 70,
            SWING_UP: 65,
            SWING_UP_MIDDLE: 68,
            SWING_MIDDLE: 67,
            SWING_DOWN_MIDDLE: 69,
            SWING_DOWN: 66,
        },
        "remote_switches": [
            {"key": "runStatus", "name": "Power", "on": 48, "off": 49},
            {"key": "powerful", "name": "Powerful", "on": 1, "off": 0},
            {"key": "ecoMode", "name": "Eco", "on": 1, "off": 0},
            {"key": "nanoe", "name": "Nanoe", "on": 1, "off": 0},
            {"key": "nanoeG", "name": "Nanoe-G", "on": 1, "off": 0},
            {"key": "selfClean", "name": "Self Clean", "on": 1, "off": 0},
            {"key": "eClean", "name": "E-Clean", "on": 1, "off": 0},
            {"key": "mildew", "name": "Mildew Proof", "on": 1, "off": 0},
            {"key": "waterClean", "name": "Water Clean", "on": 1, "off": 0},
            {"key": "pm2p5Clean", "name": "PM2.5 Clean", "on": 1, "off": 0},
            {"key": "newair", "name": "Fresh Air", "on": 1, "off": 0},
            {"key": "sleep", "name": "Sleep", "on": 1, "off": 0},
            {"key": "buzzer", "name": "Buzzer", "on": 1, "off": 0},
            {"key": "lamp", "name": "Display Light", "on": 1, "off": 0},
        ],
        "remote_buttons": [
            {"key": "runStatus", "name": "Power Toggle", "toggle": True},
            {"key": "filterReset", "name": "Filter Reset", "press": 1},
            {"key": "selfcleanReset", "name": "Self Clean Reset", "press": 1},
        ],
        "remote_selects": [
            {
                "key": "displaySet",
                "name": "Display",
                "options": {"Off": 0, "On": 1},
            },
            {
                "key": "sleepMode",
                "name": "Sleep Mode",
                "options": {"Off": 0, "Mode 1": 1, "Mode 2": 2, "Mode 3": 3},
            },
            {
                "key": "powerfulMode",
                "name": "Powerful Mode",
                "options": {"Off": 0, "Mode 1": 1, "Mode 2": 2},
            },
            {
                "key": "cleanMode",
                "name": "Clean Mode",
                "options": {"Off": 0, "Mode 1": 1, "Mode 2": 2, "Mode 3": 3},
            },
        ],
    },
}
