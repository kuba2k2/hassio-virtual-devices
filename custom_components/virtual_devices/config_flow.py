# Copyright (c) Kuba Szczodrzyński 2023-12-27.

from copy import deepcopy
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.button import ButtonDeviceClass
from homeassistant.components.cover import CoverDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    FlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_COUNT,
    CONF_DEVICE_CLASS,
    CONF_ENTITIES,
    CONF_FRIENDLY_NAME,
    CONF_ID,
    CONF_MODEL,
    CONF_PLATFORM,
    Platform,
)
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorMode,
)
from homeassistant.util.uuid import random_uuid_hex
from voluptuous import default_factory

from .const import CONF_DATA, CONF_MANUFACTURER, CONF_MODULE, DOMAIN
from .mixin.reload import ReloadMixin
from .mixin.storage import StorageMixin

DEVICE_OPTIONS_MENU = [
    "entity_add",
    "entity_copy",
    "entity_edit",
    "entity_remove",
]


class DeviceConfigFlow(
    ConfigFlow,
    ReloadMixin,
    domain=DOMAIN,
):
    VERSION = 1
    MINOR_VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return DeviceOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if user_input:
            return self.async_create_entry(
                title=user_input[CONF_FRIENDLY_NAME],
                data={
                    CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                    CONF_MODEL: user_input[CONF_MODEL],
                    CONF_ENTITIES: [],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FRIENDLY_NAME,
                        default="My New Virtual Device",
                    ): cv.string,
                    vol.Required(
                        CONF_MANUFACTURER,
                        default="Virtual Device",
                    ): cv.string,
                    vol.Optional(
                        CONF_MODEL,
                        default="",
                    ): cv.string,
                }
            ),
        )


class DeviceOptionsFlow(
    OptionsFlow,
    StorageMixin,
    ReloadMixin,
):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self.entry_data = deepcopy(dict(self.config_entry.data))
        self.entity_data = None
        self.entity_index = 1
        self.entity_count = 1

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if not self.entry_data.get(CONF_ENTITIES, None):
            return await self.async_step_entity_add(user_input)

        return self.async_show_menu(
            step_id="init",
            menu_options=DEVICE_OPTIONS_MENU,
        )

    async def async_step_entity_add(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if user_input:
            module_name, _, platform = user_input[CONF_MODULE].partition(".")
            self.entity_data = {
                CONF_ID: random_uuid_hex(),
                CONF_DEVICE_CLASS: "-",
                CONF_FRIENDLY_NAME: "My New Virtual Entity",
                CONF_MODULE: module_name,
                CONF_PLATFORM: platform,
                CONF_DATA: {},
            }
            self.entity_index = 1
            self.entity_count = int(user_input[CONF_COUNT])
            return await self.async_step_entity_editor()

        modules = {}
        for module_name, module in self.list_entity_modules().items():
            for platform in module.PLATFORMS.keys():
                key = f"{module_name}.{platform.value}"
                modules[key] = f"{module.TITLE} ({platform.title()})"

        return self.async_show_form(
            step_id="entity_add",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODULE): vol.In(modules),
                    vol.Required(CONF_COUNT): NumberSelector(
                        dict(
                            min=1,
                            max=100,
                            mode=NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
        )

    async def async_step_entity_copy(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if user_input:
            entities = {
                entity[CONF_ID]: entity for entity in self.entry_data[CONF_ENTITIES]
            }
            self.entity_data = deepcopy(entities[user_input[CONF_ID]])
            self.entity_data[CONF_ID] = random_uuid_hex()
            self.entity_index = 1
            self.entity_count = int(user_input[CONF_COUNT])
            return await self.async_step_entity_editor()

        entities = {}
        for entity in self.entry_data[CONF_ENTITIES]:
            value = f"{entity[CONF_FRIENDLY_NAME]} ({entity[CONF_PLATFORM].title()})"
            entities[entity[CONF_ID]] = value

        return self.async_show_form(
            step_id="entity_copy",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID): vol.In(entities),
                    vol.Required(CONF_COUNT): NumberSelector(
                        dict(
                            min=1,
                            max=100,
                            mode=NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
        )

    async def async_step_entity_edit(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if user_input:
            entities = {
                entity[CONF_ID]: entity for entity in self.entry_data[CONF_ENTITIES]
            }
            self.entity_data = entities[user_input[CONF_ID]]
            self.entity_index = 1
            self.entity_count = 1
            return await self.async_step_entity_editor()

        entities = {}
        for entity in self.entry_data[CONF_ENTITIES]:
            value = f"{entity[CONF_FRIENDLY_NAME]} ({entity[CONF_PLATFORM].title()})"
            entities[entity[CONF_ID]] = value

        return self.async_show_form(
            step_id="entity_edit",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID): vol.In(entities),
                }
            ),
        )

    async def async_step_entity_remove(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if user_input:
            for entity in list(self.entry_data[CONF_ENTITIES]):
                if entity[CONF_ID] == user_input[CONF_ID]:
                    self.entry_data[CONF_ENTITIES].remove(entity)
            return await self._async_update_entry_data(self.entry_data)

        entities = {}
        for entity in self.entry_data[CONF_ENTITIES]:
            value = f"{entity[CONF_FRIENDLY_NAME]} ({entity[CONF_PLATFORM].title()})"
            entities[entity[CONF_ID]] = value

        return self.async_show_form(
            step_id="entity_remove",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID): vol.In(entities),
                }
            ),
        )

    async def async_step_entity_editor(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        if user_input:
            # self.entity_data[CONF_ID] = user_input.pop(CONF_ID)
            self.entity_data[CONF_DEVICE_CLASS] = user_input.pop(CONF_DEVICE_CLASS)
            self.entity_data[CONF_FRIENDLY_NAME] = user_input.pop(CONF_FRIENDLY_NAME)
            self.entity_data[CONF_DATA] |= user_input

            entities: list = self.entry_data[CONF_ENTITIES]
            if self.entity_data not in entities:
                entities.append(self.entity_data)

            if self.entity_index != self.entity_count:
                self.entity_data = deepcopy(self.entity_data)
                self.entity_data[CONF_ID] = random_uuid_hex()
                self.entity_index += 1
                return await self.async_step_entity_editor()

            return await self._async_update_entry_data(self.entry_data)

        data_schema = {
            # vol.Required(
            #     CONF_ID,
            #     default=self.entity_data[CONF_ID],
            # ): cv.string,
            vol.Required(
                CONF_FRIENDLY_NAME,
                default=self.entity_data[CONF_FRIENDLY_NAME],
            ): cv.string,
        }

        module_name = self.entity_data[CONF_MODULE]
        platform = self.entity_data[CONF_PLATFORM]
        data: dict = self.entity_data[CONF_DATA]

        device_classes = {
            Platform.SWITCH: SwitchDeviceClass,
            Platform.BUTTON: ButtonDeviceClass,
            Platform.COVER: CoverDeviceClass,
            Platform.NUMBER: NumberDeviceClass,
            Platform.SENSOR: SensorDeviceClass,
        }
        if platform in device_classes:
            key = vol.Required(
                CONF_DEVICE_CLASS,
                default=self.entity_data[CONF_DEVICE_CLASS],
            )
            data_schema[key] = SelectSelector(
                dict(
                    mode=SelectSelectorMode.DROPDOWN,
                    options=[dict(value="-", label="-")]
                    + [
                        {"value": str(cls), "label": cls.title()}
                        for cls in device_classes[platform]
                    ],
                ),
            )

            module = self.get_entity_module(module_name)
            entity_class = module.PLATFORMS[platform]
            cloned_schema: dict = entity_class.get_config_schema().extend({}).schema
            for key, value in cloned_schema.items():
                default = data.get(str(key), None)
                if default is not None and hasattr(key, "default"):
                    key.default = default_factory(default)
            data_schema |= cloned_schema

            return self.async_show_form(
                step_id="entity_editor",
                data_schema=vol.Schema(data_schema),
                description_placeholders=dict(
                    entity_index=str(self.entity_index),
                    entity_count=str(self.entity_count),
                    module=f"{module.TITLE} ({platform.title()})",
                ),
                last_step=self.entity_index == self.entity_count,
            )

    async def _async_update_entry_data(self, entry_data: dict) -> FlowResult:
        self.hass.config_entries.async_update_entry(
            entry=self.config_entry,
            data=entry_data,
        )
        await self.hass.config_entries.async_reload(
            entry_id=self.config_entry.entry_id,
        )
        return self.async_create_entry(
            title=self.config_entry.title,
            data=entry_data,
        )
