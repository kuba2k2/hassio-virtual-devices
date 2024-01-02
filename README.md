# Virtual Devices

Create virtual devices in Home Assistant, add programmable custom entities

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kuba2k2&repository=hassio-virtual-devices&category=integration)

## Introduction

This is a custom integration for Home Assistant, that allows you to create virtual, software-defined devices.

Each device you create can have its own set of entities. The entities that can be added are Python classes
(called *modules* in this project), extending HA's base entity classes, as usual. Each entity class can execute
different code upon interaction, for example:

- a `button` entity can light up an LED or play a sound
- a `switch` entity can send ON/OFF signals to a 433 MHz-controllable plug
- ...more examples to come (hopefully).

The major advantage of this integration is that it's fully GUI-configurable - no need to work with YAML files OR
*ever* restart Home Assistant (well, at least once upon installation). Modules are also reloaded whenever the
integration starts (or a device is added), so they can be easily tested by just reloading the device entry.

## Usage

1. Install the integration, either via HACS (custom repository) or by copying directly to HA config.
2. Restart Home Assistant to load the integration (it is needed the first time).
3. Add the integration in Settings - this will create a virtual device.
4. Write an entity module - examples are below.
5. Click `Configure` next to the newly added device entry - from there you can add or edit virtual entities.

## Modules

*Entity modules* are just Python files that consist of a few mandatory parts:

- `TITLE` (`str`) - a friendly name of the module, visible in GUI
- `DESCRIPTION` (`str`) - a longer description of the module, not used yet
- `PLATFORMS` (`dict[Platform, Type[Entity]]`) - a dictionary of all entity types provided by the module.

Modules are stored in the **`virtual_devices`** directory, which lies alongside the `configuration.yaml` file
(that is, `/usr/share/hassio/homeassistant/virtual_devices/` on Supervised installations).

Each module may provide one or more *entity types* (sometimes called "platforms" in HA). This should be
self-explanatory: common types are for example `button`, `switch`, `light`, `sensor`, etc.

The `PLATFORMS` dictionary maps an entity type to a Python class. This class must extend one of Home Assistant base
entity classes, such as `SwitchEntity`, `ButtonEntity`, `LightEntity`, etc. It must also extend `EntityMixin` from
this integration.

**More info on writing entity classes: [Home Assistant Developer Docs](https://developers.home-assistant.io/docs/core/entity)**

A simple module would look like this:

```python
import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from custom_components.virtual_devices import VirtualEntity

TITLE = "Linux GPIO Access"
DESCRIPTION = ""


class ExampleSwitch(SwitchEntity, VirtualEntity):
	def __init__(self, config_entry: ConfigEntry, data: dict):
        super().__init__(config_entry, data)
		# initialize the entity, e.g. set default state
        self._attr_is_on = False

	@staticmethod
    def get_config_schema() -> vol.Schema:
		# get a schema for the GUI config flow - see below
        return vol.Schema({})

	def turn_on(self, **kwargs) -> None:
        # do something when switch turns ON
        self._attr_is_on = True

    def turn_off(self, **kwargs) -> None:
        # do something when switch turns OFF
        self._attr_is_on = False


PLATFORMS = {
    Platform.SWITCH: ExampleSwitch,
}
```

## Schema & configuration

An entity class must also have a configuration schema (even if it's empty). This will be used in the GUI config flow.

The schema may define form fields or [selectors](https://next.home-assistant.io/docs/blueprint/selectors/#constant-selector) that will be shown in the [config flow](https://developers.home-assistant.io/docs/config_entries_config_flow_handler). Currently, all form fields are visible in one step only.

Adding a virtual entity to HA will then present a dialog with the defined form fields. Values entered by the user will
be available in the `self.config_entry.data` property within the entity class (this works just like in any other
integration with a config flow).

## Examples

Finally, a [complete working example](custom/components/modules/gpio.py) is built into the integration - it provides
a simple switch entity, that controls a GPIO. **It will only work if your Home Assistant host supports GPIO.**
**Be careful when dealing with GPIOs, improper usage might break your hardware.**
