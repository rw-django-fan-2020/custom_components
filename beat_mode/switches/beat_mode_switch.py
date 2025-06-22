from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant

import asyncio
import random
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

class BeatModeSwitchEntity(SwitchEntity):
    """Representation of a Beat Mode Switch Entity."""

    def __init__(self, hass: HomeAssistant, addon_url: str, entity_id: str):
        self.hass = hass
        self._attr_name = f"Beat Mode {entity_id.split('.')[-1]}"
        self._attr_unique_id = f"beat_mode_http_{entity_id}"
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
