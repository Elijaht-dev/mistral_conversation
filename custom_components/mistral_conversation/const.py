"""Constants for the Mistral Conversation integration."""
from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "mistral_conversation"
LOGGER: Final[logging.Logger] = logging.getLogger(__package__)

DEFAULT_CONVERSATION_NAME = "Mistral Conversation"
DEFAULT_NAME = "Mistral Conversation"

# Configuration
CONF_CHAT_MODEL = "chat_model"
CONF_MAX_TOKENS = "max_tokens"
CONF_PROMPT = "prompt"
CONF_TEMPERATURE = "temperature"
CONF_API_KEY = "api_key"

# Models and defaults
RECOMMENDED_CHAT_MODEL = "mistral-small-latest"
RECOMMENDED_MAX_TOKENS = 1000
RECOMMENDED_TEMPERATURE = 0.7

AVAILABLE_MODELS = [
    "mistral-tiny-latest",
    "mistral-small-latest",
    "mistral-medium-latest",
    "mistral-large-latest"
]

# Error messages
ERROR_UNAUTHORIZED = "invalid_api_key"
ERROR_UNKNOWN = "unknown"
