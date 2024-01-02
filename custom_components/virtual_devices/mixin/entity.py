#  Copyright (c) Kuba Szczodrzyński 2023-12-28.

from typing import Type

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.entity import Entity


class EntityMixin(Entity):
    def __init__(self, config_entry: ConfigEntry, data: dict):
        self.config_entry = config_entry
        self.data = data
        self.hass_data = {}

    async def async_added_to_hass(self) -> None:
        self.hass_data = self.hass.data["virtual_devices"]

    @staticmethod
    def get_config_schema() -> vol.Schema:
        raise NotImplementedError()


class EntityModule:
    TITLE: str
    DESCRIPTION: str
    PLATFORMS: dict[Platform, Type[EntityMixin]]
