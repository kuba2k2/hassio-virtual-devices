# Copyright (c) Kuba Szczodrzyński 2023-12-27.

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .entry_class import IntegrationEntryClass
from .mixin.entity import EntityMixin

PLATFORMS = [
    Platform.SWITCH,
    Platform.BUTTON,
]

VirtualEntity = EntityMixin


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    return await IntegrationEntryClass(hass, config_entry).setup()


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    return await IntegrationEntryClass(hass, config_entry).unload()


async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    return await IntegrationEntryClass(hass, config_entry).remove()
