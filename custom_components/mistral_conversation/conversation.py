"""Conversation support for Mistral AI."""

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from homeassistant.config_entries import ConfigEntry
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

class MistralConversationEntity(conversation.ConversationEntity):
    """Mistral AI conversation agent."""
    _attr_supports_streaming = False

    def __init__(self, entry: ConfigEntry, subentry: ConfigSubentry) -> None:
        self.entry = entry
        self.subentry = subentry
        self._attr_name = subentry.title
        self._attr_unique_id = subentry.subentry_id

    async def _async_handle_message(self, user_input: conversation.ConversationInput, chat_log: conversation.ChatLog) -> conversation.ConversationResult:
        options = self.subentry.data
        client = self.entry.runtime_data
        model = options.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
        prompt = user_input.text
        max_tokens = options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS)
        temperature = options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE)
        try:
            response = await client.chat.complete_async(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as err:
            raise HomeAssistantError(f"Error talking to Mistral: {err}") from err
        intent_response = conversation.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response.choices[0].message.content or "")
        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=chat_log.conversation_id,
            continue_conversation=False,
        )

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != "conversation":
            continue
        async_add_entities([
            MistralConversationEntity(config_entry, subentry)
        ], config_subentry_id=subentry.subentry_id)
