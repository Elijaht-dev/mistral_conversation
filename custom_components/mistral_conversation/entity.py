"""LLM API entity base for the Mistral AI integration."""

from __future__ import annotations

import json
import logging
from typing import Any

import mistralai
import voluptuous as vol
from voluptuous_openapi import convert

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import Entity
from homeassistant.util import ulid

from . import MistralConfigEntry
from .const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_RECOMMENDED,
    CONF_TEMPERATURE,
    CONF_THINKING_BUDGET,
    LOGGER,
    MIN_THINKING_BUDGET,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_TEMPERATURE,
    RECOMMENDED_THINKING_BUDGET,
    THINKING_MODELS,
)

_LOGGER = logging.getLogger(__name__)


class MistralBaseLLMEntity(Entity):
    """Base class for Mistral LLM entities."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, entry: MistralConfigEntry, subentry: ConfigSubentry) -> None:
        """Initialize the entity."""
        self.entry = entry
        self.subentry = subentry
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = self._device_info()

    def _device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {("mistral", self.subentry.subentry_id)},
            "name": self.subentry.title,
            "manufacturer": "Mistral AI",
            "model": self._get_model_name(),
            "entry_type": "service",
        }

    def _get_model_name(self) -> str:
        """Get the model name from config."""
        if self.subentry.data.get(CONF_RECOMMENDED, False):
            return RECOMMENDED_CHAT_MODEL
        return self.subentry.data.get(CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL)

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.subentry.title

    async def _async_handle_chat_log(
        self, chat_log: conversation.ChatLog
    ) -> None:
        """Handle the chat log and generate a response."""
        client: mistralai.Mistral = self.entry.runtime_data
        options = self.subentry.data

        # Get configuration
        model = self._get_model_name()
        temperature = (
            RECOMMENDED_TEMPERATURE
            if options.get(CONF_RECOMMENDED, False)
            else options.get(CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE)
        )
        max_tokens = (
            RECOMMENDED_MAX_TOKENS
            if options.get(CONF_RECOMMENDED, False)
            else options.get(CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS)
        )
        thinking_budget = (
            RECOMMENDED_THINKING_BUDGET
            if options.get(CONF_RECOMMENDED, False)
            else options.get(CONF_THINKING_BUDGET, RECOMMENDED_THINKING_BUDGET)
        )

        # Convert messages to Mistral format
        messages = self._convert_messages(chat_log.messages)

        # Prepare tools if available
        tools = None
        if chat_log.tools:
            tools = [self._convert_tool(tool) for tool in chat_log.tools]

        # Build request parameters
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        # Add tools if available
        if tools:
            request_params["tools"] = tools

        # Add thinking budget for thinking models
        if model in THINKING_MODELS and thinking_budget >= MIN_THINKING_BUDGET:
            request_params["thinking_budget"] = thinking_budget

        try:
            # Stream the response
            stream = await self.hass.async_add_executor_job(
                lambda: client.chat.stream(**request_params)
            )
            
            # Process streaming response
            await self._process_stream(stream, chat_log)

        except mistralai.models.SDKError as err:
            if err.status_code == 422:
                error_msg = f"Invalid request parameters: {err.message}"
            elif err.status_code == 401:
                error_msg = "Authentication failed. Please check your API key."
            elif err.status_code == 429:
                error_msg = "Rate limit exceeded. Please try again later."
            else:
                error_msg = f"Mistral API error: {err.message}"
            
            LOGGER.error("Error calling Mistral API: %s", error_msg)
            raise HomeAssistantError(error_msg) from err
        except Exception as err:
            LOGGER.error("Unexpected error calling Mistral API: %s", err)
            raise HomeAssistantError(f"Unexpected error: {err}") from err

    async def _process_stream(
        self, stream, chat_log: conversation.ChatLog
    ) -> None:
        """Process the streaming response from Mistral."""
        collected_content = ""
        tool_calls = []
        
        for chunk in stream:
            if chunk.data and chunk.data.choices:
                delta = chunk.data.choices[0].delta
                
                if delta.content:
                    collected_content += delta.content
                    # Stream content to chat log
                    chat_log.async_update_response_stream(delta.content)
                
                if delta.tool_calls:
                    # Handle tool calls
                    for tool_call in delta.tool_calls:
                        if tool_call.function:
                            tool_calls.append({
                                "id": tool_call.id or ulid.ulid(),
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                },
                                "type": "function",
                            })

        # Process any tool calls
        if tool_calls:
            await self._handle_tool_calls(tool_calls, chat_log)
        elif collected_content:
            # Add the final response to chat log
            chat_log.async_add_llm_message(
                conversation.LLMMessage(
                    content=collected_content,
                    role="assistant",
                )
            )

    async def _handle_tool_calls(
        self, tool_calls: list[dict[str, Any]], chat_log: conversation.ChatLog
    ) -> None:
        """Handle tool calls from the LLM."""
        # Add the assistant message with tool calls
        chat_log.async_add_llm_message(
            conversation.LLMMessage(
                content="",
                role="assistant",
                tool_calls=tool_calls,
            )
        )

        # Execute the tools and add results
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_args = tool_call["function"]["arguments"]
            
            try:
                # Parse arguments if they're a string
                if isinstance(function_args, str):
                    function_args = json.loads(function_args)
                
                # Execute the tool
                tool_result = await chat_log.async_tool_call(
                    tool_call["id"], function_name, function_args
                )
                
                # Add tool result to chat log
                chat_log.async_add_llm_message(
                    conversation.LLMMessage(
                        content=str(tool_result),
                        role="tool",
                        tool_call_id=tool_call["id"],
                    )
                )
                
            except Exception as err:
                LOGGER.error("Error executing tool %s: %s", function_name, err)
                chat_log.async_add_llm_message(
                    conversation.LLMMessage(
                        content=f"Error executing {function_name}: {err}",
                        role="tool",
                        tool_call_id=tool_call["id"],
                    )
                )

        # Make another API call to get the final response
        await self._async_handle_chat_log(chat_log)

    def _convert_messages(
        self, messages: list[conversation.LLMMessage]
    ) -> list[dict[str, Any]]:
        """Convert Home Assistant messages to Mistral format."""
        mistral_messages = []
        
        for message in messages:
            if message.role == "tool":
                # Tool result message
                mistral_messages.append({
                    "role": "tool",
                    "content": message.content,
                    "tool_call_id": message.tool_call_id,
                })
            elif message.tool_calls:
                # Assistant message with tool calls
                mistral_messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_call["function"]["name"],
                                "arguments": tool_call["function"]["arguments"],
                            },
                        }
                        for tool_call in message.tool_calls
                    ],
                })
            else:
                # Regular message
                mistral_messages.append({
                    "role": message.role,
                    "content": message.content,
                })
        
        return mistral_messages

    def _convert_tool(self, tool: conversation.Tool) -> dict[str, Any]:
        """Convert Home Assistant tool to Mistral function format."""
        try:
            # Convert the Home Assistant tool schema to OpenAPI format
            parameters_schema = convert(tool.parameters, spec_version="3.0.0")
            
            return {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": parameters_schema,
                },
            }
        except Exception as err:
            LOGGER.warning("Failed to convert tool %s: %s", tool.name, err)
            # Fallback to basic schema
            return {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            }
