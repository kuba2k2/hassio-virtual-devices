#  Copyright (c) Kuba Szczodrzyński 2023-12-28.

import logging
import sys
from importlib import reload

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ENTITIES,
    CONF_FRIENDLY_NAME,
    CONF_ID,
    CONF_MODEL,
    CONF_PLATFORM,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_DATA, CONF_MANUFACTURER, CONF_MODULE, DOMAIN
from .mixin.reload import ReloadMixin
from .mixin.storage import StorageMixin

_LOGGER = logging.getLogger(__name__)


class IntegrationEntityClass(StorageMixin, ReloadMixin):
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ):
        self.hass = hass
        self.config_entry = config_entry
        if DOMAIN not in self.hass.data:
            self.hass.data[DOMAIN] = {}

    async def setup(
        self,
        platform: Platform,
        async_add_entities: AddEntitiesCallback,
    ) -> None:
        data = self.config_entry.data

        device_info = DeviceInfo(
            name=self.config_entry.title,
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            manufacturer=data.get(CONF_MANUFACTURER, None),
            model=data.get(CONF_MODEL, None),
        )

        entities = []
        for entity_data in data.get(CONF_ENTITIES, []):
            if platform != entity_data[CONF_PLATFORM]:
                continue
            entity_id = entity_data[CONF_ID]
            device_class = entity_data[CONF_DEVICE_CLASS]
            friendly_name = entity_data[CONF_FRIENDLY_NAME]
            module_name = entity_data[CONF_MODULE]
            data = entity_data[CONF_DATA]

            try:
                module = self.get_entity_module(module_name)
                entity_class = module.PLATFORMS[platform]
                for base in entity_class.__bases__:
                    if "virtual_devices" in base.__module__:
                        reload(sys.modules[base.__module__])
                entity = entity_class(
                    config_entry=self.config_entry,
                    data=data,
                )
            except Exception as e:
                _LOGGER.error(
                    f"Couldn't load entity module '{module_name}' "
                    f"for device '{self.config_entry.title}': {type(e).__name__}: {e}"
                )
                continue

            entity._attr_name = friendly_name or self.config_entry.title
            entity._attr_unique_id = f"{platform}.{entity_id or friendly_name}"
            entity._attr_device_class = device_class if device_class != "-" else None
            entity._attr_device_info = device_info

            entities.append(entity)

        async_add_entities(entities, True)
