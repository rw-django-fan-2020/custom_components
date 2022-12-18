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
import json
import aubio

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "mqtt_music_viz"
_LOGGER = logging.getLogger(__name__)

CONF_TOPIC = "topic"
DEFAULT_TOPIC = "hermes/tts/say"

BUFFER_SIZE = 1024
CHANNELS = 1
#FORMAT = pyaudio.paFloat32
METHOD = "default"
SAMPLE_RATE = 44100
HOP_SIZE = BUFFER_SIZE // 2
PERIOD_SIZE_IN_FRAME = HOP_SIZE

# Schema to validate the configured MQTT topic
CONFIG_SCHEMA = vol.Schema(
    {vol.Optional(CONF_TOPIC, default=DEFAULT_TOPIC): mqtt.valid_subscribe_topic},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    try:        
        """Set up the MQTT async example component."""
        topic = config[DOMAIN][CONF_TOPIC]
        entity_id = DOMAIN + ".state"
        _LOGGER.warning("topic: " + topic)

        tempo_detect = aubio.tempo(METHOD, BUFFER_SIZE, HOP_SIZE, SAMPLE_RATE)

        pitch_detect = aubio.pitch(METHOD, BUFFER_SIZE, HOP_SIZE, SAMPLE_RATE)
        pitch_detect.set_unit("Hz")
        pitch_detect.set_silence(-40)

        # Listen to a message on MQTT.
        @callback
        async def message_received(topic: str, payload: str, qos: int) -> None:
            try:                
                """A new MQTT message has been received."""
                await hass.states.async_set(entity_id, payload)
            except Exception as ex:
                _LOGGER.error(ex)

        await hass.components.mqtt.async_subscribe(topic, message_received)

        hass.states.async_set(entity_id, "off")

        # Service to publish a message on MQTT.
        @callback
        async def publish_service(call: ServiceCall) -> None:
            try:
                http_source_url = call.data.get("http_source_url")
                friendly_name = call.data.get("friendly_name")
                colour = call.data.get("colour")

                src = aubio.source(http_source_url, hop_size=512)

                samples, read = src()

                # Detect a beat
                is_beat = tempo_detect(samples)

                # Get the pitch
                pitch = pitch_detect(samples)[0]

                # Get the volume
                #volume = np.sum(samples ** 2) / len(samples)

                _LOGGER.warning("is_beat: " + str(is_beat[0]))
                if is_beat[0]:
                    """Service to send a message."""
                    mqtt_data = mqtt.get_mqtt_data(hass, True)
                    topic = "zigbee2mqtt/" + friendly_name + "/set"
                    payload = json.dumps(
                        {
                            "state": "ON",
                            "brightness": 255,
                            "transition": 0.001,
                            "color": {"rgb": colour}
                        }
                    )
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
