"""Config flow for Mistral Conversation integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from .const import DOMAIN, CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Optional(CONF_CHAT_MODEL, default=RECOMMENDED_CHAT_MODEL): str,
})

class MistralConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mistral Conversation."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Optionally, validate API key by making a test request here
            return self.async_create_entry(
                title="Mistral Conversation",
                data=user_input,
            )
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
