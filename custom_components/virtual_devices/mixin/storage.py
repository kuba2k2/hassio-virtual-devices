# Copyright (c) Kuba Szczodrzyński 2023-12-27.

from pathlib import Path
from types import ModuleType

from homeassistant.core import HomeAssistant

from .entity import EntityModule


class StorageMixin:
    hass: HomeAssistant

    @property
    def modules_internal_path(self) -> Path:
        path = Path(__file__).parents[1] / "modules"
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def modules_external_path(self) -> Path:
        path = Path(self.hass.config.path("virtual_devices"))
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _load_entity_module(path: Path) -> EntityModule:
        module: EntityModule
        # noinspection PyTypeChecker
        module = ModuleType(path.stem)
        code = compile(
            source=path.read_text(),
            filename=path,
            mode="exec",
        )
        exec(code, module.__dict__)
        return module

    def get_entity_module(self, name: str) -> EntityModule:
        try:
            return self._load_entity_module(self.modules_external_path / f"{name}.py")
        except FileNotFoundError:
            return self._load_entity_module(self.modules_internal_path / f"{name}.py")

    def list_entity_modules(self) -> dict[str, EntityModule]:
        result = {}
        modules_external = list(self.modules_external_path.glob("*.py"))
        modules_internal = list(self.modules_internal_path.glob("*.py"))
        for path in modules_external + modules_internal:
            module = self._load_entity_module(path)
            if not getattr(module, "PLATFORMS", None):
                continue
            result[path.stem] = module
        return result
