#  Copyright (c) Kuba Szczodrzyński 2023-12-28.

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity_class import IntegrationEntityClass


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await IntegrationEntityClass(hass, config_entry).setup(
        platform=Platform.BUTTON,
        async_add_entities=async_add_entities,
    )
