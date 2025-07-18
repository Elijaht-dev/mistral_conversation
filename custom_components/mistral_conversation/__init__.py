"""The Mistral Conversation integration."""

from __future__ import annotations

import logging
from mistralai import Mistral
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    DOMAIN,
    LOGGER,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_TEMPERATURE,
)

SERVICE_GENERATE_CONTENT = "generate_content"
PLATFORMS = (Platform.CONVERSATION,)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Mistral Conversation."""
    await async_setup_services(hass)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mistral Conversation from a config entry."""
    # Create a persistent async Mistral client
    mistral_client = Mistral(api_key=entry.data[CONF_API_KEY])
    entry.runtime_data = mistral_client
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Mistral Conversation."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def send_prompt(call: ServiceCall) -> ServiceResponse:
    """Send a prompt to Mistral and return the response."""
    hass = call.hass
    entry_id = call.data["config_entry"]
    
    entry = hass.config_entries.async_get_entry(entry_id)
    if not entry or entry.domain != DOMAIN:
        raise ServiceValidationError(
            f"Config entry {entry_id} not found or not a Mistral Conversation entry"
        )

    client: Mistral = entry.runtime_data
    model = entry.data.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
    prompt = call.data[CONF_PROMPT]
    max_tokens = entry.data.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS)
    temperature = entry.data.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE)

    try:
        response = await client.chat.create_async(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        if not response.choices or not response.choices[0].message:
            raise HomeAssistantError("Empty response from Mistral")
            
        return {"text": response.choices[0].message.content.strip()}
    except Exception as err:
        LOGGER.error("Error generating content: %s", err)
        raise HomeAssistantError(f"Error generating content: {err}") from err


async def async_setup_services(hass: HomeAssistant):
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_CONTENT,
        send_prompt,
        schema=vol.Schema({
            vol.Required("config_entry"): selector.ConfigEntrySelector({"integration": DOMAIN}),
            vol.Required(CONF_PROMPT): cv.string,
        }),
        supports_response=SupportsResponse.ONLY,
    )

