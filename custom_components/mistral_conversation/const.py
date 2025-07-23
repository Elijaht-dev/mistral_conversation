"""Constants for the Mistral integration."""

import logging

DOMAIN = "mistral_conversation"
LOGGER = logging.getLogger(__package__)

DEFAULT_CONVERSATION_NAME = "Mistral conversation"

CONF_RECOMMENDED = "recommended"
CONF_PROMPT = "prompt"
CONF_CHAT_MODEL = "chat_model"
RECOMMENDED_CHAT_MODEL = "mistral-small-latest"
CONF_MAX_TOKENS = "max_tokens"
RECOMMENDED_MAX_TOKENS = 3000
CONF_TEMPERATURE = "temperature"
RECOMMENDED_TEMPERATURE = 1.0
CONF_THINKING_BUDGET = "thinking_budget"
RECOMMENDED_THINKING_BUDGET = 0
MIN_THINKING_BUDGET = 1024

THINKING_MODELS = [
    "mistral-large-latest",
    "mistral-large-2411",
    "mistral-medium-latest",
]
