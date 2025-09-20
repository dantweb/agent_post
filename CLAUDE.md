# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in the agent_post container.

## Agent Post Service Overview

Agent Post is a Python-based microservice for inter-agent message processing within the LoopAI ecosystem. It handles message collection, storage, and delivery between agents, integrating with the main LoopAI application via API calls.

## Development Commands

### Docker Environment
- `make up` - Start agent_post container
- `make down` - Stop agent_post container
- `make post` - Access agent_post container shell
- `make logs` - View container logs

### Testing
- `python -m unittest discover tests` - Run all unit tests
- `python run_tests.py` - Run unified test runner
- Tests cover message processing, delivery, and integration with LoopAI

### Setup
- `python setup/install.py` - Initialize database
- `python setup/uninstall.py` - Drop database

## Architecture

### Core Components

**Application Structure:**
- `app.py` - Flask API server for message endpoints
- `src/` - Core business logic modules
- `tests/` - Unit and integration tests
- `setup/` - Database initialization scripts

**Core Modules:**
- `src/message_service.py` - Core message processing logic
- `src/city_api.py` - Communication with LoopAI CityAPI endpoints
- `src/external_api.py` - External agent communication (outbox/inbox)
- `src/message.py` - Message data model

### Integration with LoopAI

**API Communication:**
- **POST** `/api/public/agent/<agent_id>/action/RECEIVE_POST/` - Sends messages to LoopAI
- **GET** agent outbox endpoints - Collects messages from other agents
- **POST** agent inbox endpoints - Delivers messages to recipients

**Message Flow:**
1. Collect messages from external agent outboxes
2. Store messages in local SQLite database
3. Process multi-recipient delivery (comma/semicolon/space separated)
4. Filter out self-addressing to prevent loops
5. Deliver to LoopAI via API calls
6. Create filesystem artifacts via LoopAI's file creation system

### Key Features

**Message Processing:**
- Multi-recipient support with address parsing
- Self-address filtering to prevent message loops
- Automatic message deduplication
- Filesystem integration via LoopAI API

**Error Handling:**
- Retry logic for failed deliveries
- Comprehensive logging for debugging
- Graceful handling of network failures

## Environment Configuration

Key environment variables in `.env`:
- `DATABASE_URL` - SQLite database connection
- `EXTERNAL_API_TOKEN` - Authentication for external APIs
- `CITY_API_URL` - LoopAI CityAPI endpoint URL
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHANNEL_ID` - Optional Telegram integration

## Common Development Patterns

### Adding New Message Types
1. Extend message model in `src/message.py`
2. Update processing logic in `src/message_service.py`
3. Add corresponding tests

### API Integration Changes
1. Modify `src/city_api.py` for LoopAI API changes
2. Update `src/external_api.py` for external agent protocols
3. Test integration with `tests/test_*_integration.py`

### Message Delivery Flow
- Messages collected from outboxes are stored locally
- Multi-recipient parsing splits addresses by comma/semicolon/space
- Each recipient gets individual delivery attempts
- Failed deliveries are logged and can be retried

## Common Issues

### Missing Module Dependencies
- Ensure `city_api` module is available in Python path
- Check `requirements.txt` for all dependencies
- Verify container has access to shared modules

### Database Connection Issues
- Ensure SQLite database is initialized with `setup/install.py`
- Check file permissions for database access
- Verify container volume mounts for persistence

### API Communication Failures
- Verify LoopAI web container is accessible at expected URLs
- Check network connectivity between containers
- Validate API tokens and authentication

## Testing Strategy

**Unit Tests:**
- `test_message.py` - Message model validation
- `test_message_service.py` - Core business logic
- `test_city_api.py` - API communication

**Integration Tests:**
- `test_message_integration.py` - End-to-end message flow
- `test_direct_save_file.py` - LoopAI filesystem integration
- `test_external_api.py` - External agent communication

**Test Execution:**
```bash
# Run all tests
python -m unittest discover tests

# Run specific test modules
python -m unittest tests.test_message_service
python -m unittest tests.test_message_integration
```