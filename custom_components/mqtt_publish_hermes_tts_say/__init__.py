"""
Example of a custom MQTT component.

Shows how to communicate with MQTT. Follows a topic on MQTT and updates the
state of an entity to the last message received on that topic.

Also offers a service 'set_state' that will publish a message on the topic that
will be passed via MQTT to our message received listener. Call the service with
example payload {"new_state": "some new state"}.

Configuration:

To use the mqtt_example component you will need to add the following to your
configuration.yaml file.

mqtt_basic_async:
  topic: "home-assistant/mqtt_example"
"""
from __future__ import annotations
import logging
import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "mqtt_publish_hermes_tts_say"
_LOGGER = logging.getLogger(__name__)

CONF_TOPIC = "topic"
DEFAULT_TOPIC = "hermes/tts/say"

# Schema to validate the configured MQTT topic
CONFIG_SCHEMA = vol.Schema(
    {vol.Optional(CONF_TOPIC, default=DEFAULT_TOPIC): mqtt.valid_subscribe_topic},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    try:        
        """Set up the MQTT async example component."""
        topic = config[DOMAIN][CONF_TOPIC]
        entity_id = "mqtt_example.last_message"
        _LOGGER.warning("topic: " + topic)

        # Listen to a message on MQTT.
        @callback
        async def message_received(topic: str, payload: str, qos: int) -> None:
            try:                
                """A new MQTT message has been received."""
                await hass.states.async_set(entity_id, payload)
            except Exception as ex:
                _LOGGER.error(ex)

        await hass.components.mqtt.async_subscribe(topic, message_received)

        hass.states.async_set(entity_id, "No messages")

        # Service to publish a message on MQTT.
        @callback
        async def publish_service(call: ServiceCall) -> None:
            try:
                payload = "{" + ", ".join("\"" + key + "\": " + "\"" + str(value) + "\"" for key, value in call.data.items() if key != "topic") + "}"

                """Service to send a message."""
                mqtt_data = mqtt.get_mqtt_data(hass, True)
                assert mqtt_data is not None and topic is not None
                await mqtt_data.client.async_publish(topic, payload, 0, False)
            except Exception as ex:
                _LOGGER.error(ex)
                _LOGGER.error("call.data: " + str(call.data))

        # Register our service with Home Assistant.
        hass.services.async_register(DOMAIN, "publish", publish_service, schema = CONFIG_SCHEMA)

        # Return boolean to indicate that initialization was successfully.
        return True
    except Exception as ex:
        _LOGGER.error(ex)
        return False
