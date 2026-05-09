# Panasonic Smart China ZY Custom for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.1.0-blue.svg)]()

Panasonic Smart China custom integration for Home Assistant, with additional support for CS-ZY35K410 and extra remote-control entities.

## HACS

1. Open HACS -> Integrations.
2. Add this repository as a custom repository, category `Integration`.
3. Search for `Panasonic Smart China ZY Custom`.
4. Download and restart Home Assistant.

HACS should install this custom build to:

```text
/config/custom_components/panasonic_smart_china_zy
```

## Manual Install

Copy this folder:

```text
custom_components/panasonic_smart_china_zy
```

to:

```text
/config/custom_components/panasonic_smart_china_zy
```

Then restart Home Assistant and add the integration named `Panasonic Smart China ZY Custom`.

## Notes

- This custom build uses domain `panasonic_smart_china_zy`, so it does not conflict with the original `panasonic_smart_china` integration.
- CS-ZY35K410 has a dedicated profile with temperature, fan speed, vertical swing, horizontal swing, power, and extra remote-control entities.
- Some extra switch/select/button entities only become available if the device status response includes the corresponding Panasonic field.
