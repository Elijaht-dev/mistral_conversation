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
        """Process a sentence."""
        options = self.subentry.data
        client = self.entry.runtime_data
        model = options.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)
        max_tokens = options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS)
        temperature = options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE)

        # Build the messages list from chat history
        messages = []
        if chat_log.messages and len(chat_log.messages) > 0:
            for message in chat_log.messages[-5:]:  # Use last 5 messages for context
                role = "assistant" if message.is_agent else "user"
                messages.append({"role": role, "content": message.text})
        
        # Add the current message
        messages.append({"role": "user", "content": user_input.text})

        try:
            response = await client.chat.create_async(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            LOGGER.debug("Mistral response: %s", response)
            
            if not response.choices or not response.choices[0].message:
                raise HomeAssistantError("Empty response from Mistral")
                
            response_text = response.choices[0].message.content.strip()
            
            intent_response = conversation.IntentResponse(language=user_input.language)
            intent_response.async_set_speech(response_text)
            return conversation.ConversationResult(
                response=intent_response,
                conversation_id=chat_log.conversation_id,
                continue_conversation=True,
            )
        except Exception as err:
            LOGGER.error("Error talking to Mistral: %s", err)
            raise HomeAssistantError(f"Error talking to Mistral: {err}") from err

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    for subentry in config_entry.subentries.values():
        if subentry.subentry_type != "conversation":
            continue
        async_add_entities([
            MistralConversationEntity(config_entry, subentry)
        ], config_subentry_id=subentry.subentry_id)
