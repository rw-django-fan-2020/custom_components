import json
import logging
import random

from homeassistant.components import mqtt
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)


class BeatModeSwitchMqttEntity(SwitchEntity):
    """Representation of a Beat Mode Switch MQTT Entity."""

    def __init__(self, hass: HomeAssistant, subscription: str, entity_id: str):
        self._hass = hass
        self._attr_name = f"Beat Mode MQTT {entity_id.split('.')[-1]}"
        self._attr_unique_id = f"beat_mode_mqtt_{entity_id}"
        self._is_on = False
        self._subscription = subscription
        self._light_entity_id = entity_id
        self._unsub = None

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on and start listening to MQTT."""
        if self._attr_is_on:
            return

        self._attr_is_on = True

        @callback
        def message_received(msg):
            try:
                data = json.loads(msg.payload)
                volume = data.get("volume")
                _LOGGER.debug(f"Received volume: {volume}")
                if volume is not None:
                    rgb = [random.randint(0, 255) for _ in range(3)]
                    brightness = max(30, int(volume * 255))  # Mindesthelligkeit 30
                    self._hass.async_create_task(
                        self._hass.services.async_call(
                            "light",
                            "turn_on",
                            {
                                "entity_id": self._light_entity_id,
                                "rgb_color": rgb,
                                "brightness": brightness,
                            },
                        )
                    )
            except (json.JSONDecodeError, ValueError) as e:
                _LOGGER.error(
                    f"Invalid payload on beat_mode topic: {msg.payload} ({e})"
                )

        self._unsub = await mqtt.async_subscribe(
            self._hass, self._subscription, message_received
        )

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off and unsubscribe from MQTT."""
        if not self._attr_is_on:
            return

        self._attr_is_on = False

        if self._unsub:
            self._unsub()
            self._unsub = None

        self.async_write_ha_state()
