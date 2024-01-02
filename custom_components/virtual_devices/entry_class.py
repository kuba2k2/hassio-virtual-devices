# Copyright (c) Kuba Szczodrzyński 2023-12-27.

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .mixin.reload import ReloadMixin
from .mixin.storage import StorageMixin


class IntegrationEntryClass(StorageMixin, ReloadMixin):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        self.hass = hass
        self.config_entry = config_entry

    async def setup(self) -> bool:
        await self.hass.config_entries.async_forward_entry_setups(
            entry=self.config_entry,
            platforms=[
                Platform.SWITCH,
                Platform.BUTTON,
            ],
        )

        return True

    async def unload(self) -> bool:
        return await self.hass.config_entries.async_unload_platforms(
            entry=self.config_entry,
            platforms=[
                Platform.SWITCH,
                Platform.BUTTON,
            ],
        )

    async def remove(self) -> None:
        pass
