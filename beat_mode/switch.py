"""Platform for switch integration."""

from __future__ import annotations

import asyncio
import logging
import random

import aiohttp

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data.get("host")
    selected_light = entry.data.get("selected_light")

    switches = [
        BeatModeSwitchEntity(hass, host, selected_light),
    ]
    async_add_entities(switches)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    # Beispielhafte Lampenauswahl (später dynamisch machen)
    # lamps = hass.states.async_all("light")
    # switches = [
    #    BeatModeSwitchEntity(
    #        hass, "http://homeassistant.crunk.dedyn.io:5000", lamp.entity_id
    #    )
    #    for lamp in lamps
    # if "color" in lamp.attributes.get("supported_color_modes", [])
    # ]
    switches = [
        BeatModeSwitchEntity(
            hass, "http://homeassistant.crunk.dedyn.io:5000", "light.flair_viyu"
        ),
    ]
    async_add_entities(switches)


class BeatModeSwitchEntity(SwitchEntity):
    """Representation of a Beat Mode Switch Entity."""

    def __init__(self, hass, addon_url, entity_id):
        self.hass = hass
        self._attr_name = f"Beat Mode {entity_id.split('.')[-1]}"
        self._attr_unique_id = f"{entity_id}_beat_mode"
        self._entity_id = entity_id
        self._is_on = False
        self._addon_url = addon_url
        self._light_entity_id = entity_id
        self._task = None

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self._task = self.hass.loop.create_task(self._beat_loop())
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        if self._task:
            self._task.cancel()
            self._task = None
        self.async_write_ha_state()

    async def _beat_loop(self):
        try:
            async with aiohttp.ClientSession() as session:
                while self._is_on:
                    async with session.get(
                        f"{self._addon_url}/beat", timeout=2
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            volume = data.get("volume", 0)
                            # if volume > 0.05:  # Beat erkannt
                            await self._change_light_color(volume)
                    await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.warning("Error in beat loop: %s", e)

    async def _change_light_color(self, volume: float):
        """Change the color and brightness of the light based on beat volume."""
        rgb = [random.randint(0, 255) for _ in range(3)]
        brightness = max(30, int(volume * 255))  # Mindesthelligkeit 30
        _LOGGER.debug(f"Sending command to light {self._light_entity_id}")
        await self.hass.services.async_call(
            "light",
            "turn_on",
            {
                "entity_id": self._light_entity_id,
                "rgb_color": rgb,
                "brightness": brightness,
            },
            blocking=False,
        )
