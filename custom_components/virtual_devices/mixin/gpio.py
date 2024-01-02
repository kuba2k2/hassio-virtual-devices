#  Copyright (c) Kuba Szczodrzyński 2023-12-30.

import logging
from pathlib import Path
from threading import Lock
from time import time

import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    ConstantSelector,
    SelectSelector,
    SelectSelectorMode,
)
from periphery import GPIO

_LOGGER = logging.getLogger(__name__)


class GpioMixin:
    data: dict
    hass_data: dict

    @staticmethod
    def get_config_schema():
        return vol.Schema(
            {
                vol.Optional("label_gpiochip"): ConstantSelector(
                    dict(
                        label="GPIO chip",
                        value=True,
                    ),
                ),
                vol.Required("gpiochip"): SelectSelector(
                    dict(
                        mode=SelectSelectorMode.DROPDOWN,
                        options=[str(path) for path in Path("/dev").glob("gpiochip*")],
                    ),
                ),
                vol.Optional("label_gpioline"): ConstantSelector(
                    dict(
                        label="GPIO line",
                        value=True,
                    ),
                ),
                vol.Required("gpioline"): SelectSelector(
                    dict(
                        mode=SelectSelectorMode.DROPDOWN,
                        options=[
                            dict(value=str(i), label=f"{i}") for i in range(0, 512)
                        ],
                    ),
                ),
            }
        )

    @property
    def _gpio_key(self) -> str:
        return f"{self.data['gpiochip']}/{self.data['gpioline']}"

    def _gpio_get(self) -> tuple[GPIO, Lock]:
        if self._gpio_key in self.hass_data:
            gpio, lock = self.hass_data[self._gpio_key]
        else:
            gpio = GPIO(self.data["gpiochip"], int(self.data["gpioline"]), "out")
            lock = Lock()
            self.hass_data[self._gpio_key] = gpio, lock
        return gpio, lock

    def _gpio_write(self, value: bool) -> None:
        gpio, lock = self._gpio_get()
        if not lock.acquire(timeout=2.0):
            raise HomeAssistantError("Timeout while acquiring lock")
        try:
            gpio.write(value)
        finally:
            lock.release()

    def _gpio_write_timed(self, timing: list[int]) -> None:
        gpio, lock = self._gpio_get()
        if not lock.acquire(timeout=2.0):
            raise HomeAssistantError("Timeout while acquiring lock")
        timing_data = [
            (
                micros >= 0,
                (abs(micros) / 1e6) - (15 / 1e6),
                (abs(micros) / 1e6),
            )
            for micros in timing
        ]
        try:
            # time_start = time()
            tm = time()
            for level, duration, _ in timing_data:
                end = tm + duration
                gpio.write(value=level)
                while end > (tm := time()):
                    pass
            # time_end = time()
            # _LOGGER.error(
            #     f"GPIO write timing: "
            #     f"elapsed={(time_end - time_start) * 1e3:.03f} ms, "
            #     f"expected={sum(d for _, _, d in timing_data) * 1e3:.03f} ms"
            # )
        finally:
            lock.release()
