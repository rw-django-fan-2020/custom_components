"""The beat mode integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
    #    "host": entry.data["host"],
    # }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    )
    return True
