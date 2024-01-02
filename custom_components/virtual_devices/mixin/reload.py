# Copyright (c) Kuba Szczodrzyński 2023-12-27.

import sys
from importlib import reload


class ReloadMixin:
    def __new__(cls, *args, **kwargs):
        for base in cls.__bases__:
            if "virtual_devices" in base.__module__:
                reload(sys.modules[base.__module__])
        reload(sys.modules[cls.__module__])

        cls = getattr(sys.modules[cls.__module__], cls.__name__)
        obj = object.__new__(cls)
        # noinspection PyArgumentList
        obj.__init__(*args, **kwargs)
        return obj
