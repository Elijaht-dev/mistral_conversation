# Mistral Conversation (not functionnal)

A Home Assistant custom integration that provides conversation/chat capabilities using Mistral AI's LLM models.

## Installation

### HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Search for "Mistral Conversation" in HACS
3. Install the integration
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/mistral_conversation` folder to your `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Mistral"
4. Enter your Mistral API key
5. Configure your conversation agent settings

## Requirements

- Home Assistant 2025.7.2 or newer
- Mistral AI API key

## Features

- Multiple conversation agents
- Streaming responses
- Tool calling support
- Advanced model configuration
- Thinking models support
