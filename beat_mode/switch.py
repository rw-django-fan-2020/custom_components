"""Platform for switch integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .switches.beat_mode_switch import BeatModeSwitchEntity
from .switches.beat_mode_switch_mqtt import BeatModeSwitchMqttEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    selected_light = entry.data.get("selected_light")

    if entry.data.get("protocol") == "http":
        host = entry.data.get("host")
        switches = [
            BeatModeSwitchEntity(hass, host, selected_light),
        ]

    if entry.data.get("protocol") == "mqtt":
        subscription = entry.data.get("subscription")
        switches = [
            BeatModeSwitchMqttEntity(hass, subscription, selected_light),
        ]

    async_add_entities(switches)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    switches = [
        BeatModeSwitchEntity(
            hass, "http://homeassistant.crunk.dedyn.io:5000", "light.flair_viyu"
        ),
    ]
    async_add_entities(switches)
