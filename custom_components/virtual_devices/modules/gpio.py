#  Copyright (c) Kuba Szczodrzyński 2023-12-30.

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from custom_components.virtual_devices import VirtualEntity
from custom_components.virtual_devices.mixin.gpio import GpioMixin

TITLE = "Linux GPIO Access"
DESCRIPTION = ""


class GpioSwitch(SwitchEntity, VirtualEntity, GpioMixin):
    def __init__(self, config_entry: ConfigEntry, data: dict):
        super().__init__(config_entry, data)
        self._attr_is_on = False

    @staticmethod
    def get_config_schema() -> vol.Schema:
        return GpioMixin.get_config_schema()

    async def async_will_remove_from_hass(self) -> None:
        if self._gpio_key in self.hass_data:
            gpio, lock = self.hass_data[self._gpio_key]
            gpio.close()
            del self.hass_data[self._gpio_key]

    def turn_on(self, **kwargs) -> None:
        self._gpio_write(True)
        self._attr_is_on = True

    def turn_off(self, **kwargs) -> None:
        self._gpio_write(False)
        self._attr_is_on = False


PLATFORMS = {
    Platform.SWITCH: GpioSwitch,
}
