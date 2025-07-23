# Mistral Conversation Integration for Home Assistant

## Overview
This is a Home Assistant custom integration that provides conversation/chat capabilities using Mistral AI's LLM models. The integration follows Home Assistant's conversation platform architecture with config flows, subentries for multiple conversation agents, and streaming support.

## Architecture

### Key Components
- **`__init__.py`**: Entry point with client initialization, migration logic, and config entry management
- **`conversation.py`**: ConversationEntity implementation for the HA conversation platform
- **`entity.py`**: Base LLM entity with Mistral API integration, streaming, and tool support
- **`config_flow.py`**: Configuration UI flows for API keys and conversation agent options
- **`const.py`**: Constants including model names, defaults, and thinking model configurations

### Config Entry Structure
- **Parent entries**: Store API keys and Mistral client instances in `runtime_data`
- **Subentries**: Individual conversation agents with model settings, prompts, and LLM API configurations
- **Migration system**: Handles v1→v2 migration for subentry architecture

### Mistral API Integration
- Uses `mistralai` Python SDK (v1.9.2)
- Client stored in config entry `runtime_data` as `mistralai.Mistral`
- Streaming via `client.chat.stream()` with async iteration
- Model validation via `client.models.retrieve()`

## Key Patterns

### Error Handling
```python
try:
    # Mistral API calls
except mistralai.models.SDKError as err:
    if err.status_code == 422:
        # Handle validation errors specifically
    # Handle other SDK errors
```

### Message Format Conversion
- Convert HA conversation format to Mistral's chat completion format
- Handle tool calls/results in message history
- Stream processing for real-time responses

### Configuration Options
- **Recommended mode**: Uses default settings optimized for HA
- **Advanced mode**: Exposes model, temperature, max_tokens, thinking_budget
- **Thinking models**: Special handling for models supporting extended reasoning

## Development Notes

### Dependencies
- `mistralai==1.9.2` (Mistral Python SDK)
- `voluptuous_openapi` for tool schema conversion
- Standard HA conversation/config_flow infrastructure

### Model Configuration
- Default model: `mistral-small-latest`
- Thinking models have special budget token settings
- Temperature/max_tokens configurable per conversation agent

### Debugging
- Use `LOGGER` from `const.py` for consistent logging
- API errors surface as HomeAssistantError to users
- Config flow validates API connectivity before saving

### Testing Considerations
- Mock `mistralai.Mistral` client for unit tests
- Test both recommended and advanced configuration modes
- Verify migration logic handles existing v1 entries
- Test streaming response handling and error cases
