"""Constants for the Mistral Conversation integration."""

import logging

DOMAIN = "mistral_conversation"
LOGGER: logging.Logger = logging.getLogger(__package__)

DEFAULT_CONVERSATION_NAME = "Mistral Conversation"
DEFAULT_NAME = "Mistral Conversation"

CONF_CHAT_MODEL = "chat_model"
CONF_MAX_TOKENS = "max_tokens"
CONF_PROMPT = "prompt"
CONF_TEMPERATURE = "temperature"
CONF_API_KEY = "api_key"

RECOMMENDED_CHAT_MODEL = "mistral-small-latest"
RECOMMENDED_MAX_TOKENS = 150
RECOMMENDED_TEMPERATURE = 1.0

UNSUPPORTED_MODELS: list[str] = []
