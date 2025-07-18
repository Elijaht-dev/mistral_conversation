"""Config flow for Mistral Conversation integration."""

from __future__ import annotations

from typing import Any
import voluptuous as vol
from mistralai import Mistral
from mistralai.exceptions import MistralAPIError

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .const import (
    CONF_CHAT_MODEL,
    DOMAIN,
    LOGGER,
    RECOMMENDED_CHAT_MODEL,
)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Optional(CONF_CHAT_MODEL, default=RECOMMENDED_CHAT_MODEL): SelectSelector(
        SelectSelectorConfig(
            options=[
                "mistral-tiny-latest",
                "mistral-small-latest",
                "mistral-medium-latest",
                "mistral-large-latest"
            ],
            translation_key="chat_model"
        )
    ),
})

class MistralConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mistral Conversation."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Test the API key by making a simple request
                client = Mistral(api_key=user_input[CONF_API_KEY])
                await client.chat.create_async(
                    model=user_input[CONF_CHAT_MODEL],
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                )

                return self.async_create_entry(
                    title="Mistral Conversation",
                    data=user_input,
                )
            except MistralAPIError as err:
                LOGGER.error("Error validating API key: %s", err)
                errors["base"] = "invalid_auth"
            except Exception as err:
                LOGGER.error("Unexpected error: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
