import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class BeatModeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        self.data = {}  # Speicher für alle Eingaben

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Speichere Eingaben aus diesem Schritt
            self.data.update(user_input)
            return await self.async_step_confirm()

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("protocol", default="http"): vol.In(
                            ["http", "https", "mqtt"]
                        ),
                    }
                ),
                description_placeholders={
                    "protocol": "http or https or mqtt",
                },
            )

        return self.async_abort(reason="Something went wrong, please try again.")

    async def async_step_confirm(self, user_input=None):
        if user_input is not None:
            # Speichere Eingaben aus diesem Schritt
            self.data.update(user_input)
            title = "Beat Mode " + self.data.get("protocol")
            if self.data.get("protocol") == "http":
                title = title + " " + self.data.get("host")
            if self.data.get("protocol") == "https":
                title = title + " " + self.data.get("host")
            if self.data.get("protocol") == "mqtt":
                title = title + " " + self.data.get("subscription")
            return self.async_create_entry(title=title, data=self.data)

        # Liste aller light-Entitäten holen
        light_entities = [
            state.entity_id
            for state in self.hass.states.async_all("light")
            if "supported_color_modes" in state.attributes
        ]

        if not light_entities:
            return self.async_abort(reason="no_light_entities_found")

        if self.data.get("protocol") == "http":
            return self.async_show_form(
                step_id="confirm",
                data_schema=vol.Schema(
                    {
                        vol.Required("host"): str,
                        vol.Required("selected_light"): vol.In(light_entities),
                    }
                ),
                description_placeholders={
                    "host": "hostname or IP address of the server",
                    "selected_light": "Select a light entity",
                },
            )

        if self.data.get("protocol") == "mqtt":
            return self.async_show_form(
                step_id="confirm",
                data_schema=vol.Schema(
                    {
                        vol.Required("subscription"): str,
                        vol.Required("selected_light"): vol.In(light_entities),
                    }
                ),
                description_placeholders={
                    "subscription": "MQTT subscription topic",
                    "selected_light": "Select a light entity",
                },
            )

        return self.async_abort(reason="Something went wrong, please try again.")
