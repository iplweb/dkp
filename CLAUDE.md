# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DKP (Direct Communication Protocol) is a hospital communication system built with Django Channels for real-time WebSocket-based messaging between medical staff. It uses role-based access for Anesthetists, Nurses, and Surgeons operating in different locations (Operating Rooms and Wards).

## Development Commands

All commands should be run from the project root directory:

```bash
# Core development workflow
make install        # Install project dependencies with pip
make migrate        # Run makemigrations and migrate
make run           # Start Django dev server (port 8000)
make run-asgi      # Start Daphne ASGI server for WebSockets
make test          # Run Django tests
make shell         # Open Django shell

# Setup and maintenance
make superuser     # Create Django admin user
make collectstatic # Collect static files
make clean         # Remove cache and temporary files
```

For single test execution:
```bash
python dkp/manage.py test comms.tests.TestCaseName  # Run specific test
python dkp/manage.py test comms --keepdb            # Run app tests, keep test DB
```

## Architecture

### Django Apps Structure
- **`dkp/hospital/`**: Core models for locations (OperatingRoom, Ward) and Roles
- **`dkp/comms/`**: WebSocket consumers, message routing, and MessageLog model
- **`dkp/dkp/`**: Main project settings and configuration

### Key Technologies
- **Django Channels** with Redis as the channel layer for WebSocket handling
- **PostgreSQL** for data persistence
- **Daphne** as the ASGI server for production WebSocket support
- **python-decouple** for environment configuration

### WebSocket Architecture
- Consumer pattern: `CommunicationConsumer` in `comms/consumers.py` handles connections
- Room naming: `{role}_{location_type}_{location_id}` (e.g., `anesthetist_or_1`)
- Heartbeat system: 3-second ping to monitor connection health
- Message types: `CAN_ACCEPT_PATIENTS`, `SURGERY_DONE`, `PATIENT_IN_THE_OR`

### Database Configuration
The project uses PostgreSQL with configuration from environment variables:
- DB_NAME (default: 'dkp')
- DB_USER (default: 'dkp')
- DB_PASSWORD (default: 'dkp')
- DB_HOST (default: 'localhost')
- DB_PORT (default: '5432')

Redis configuration:
- REDIS_URL (default: 'redis://localhost:6379/0')

### Static Files
- Static files are served using WhiteNoise middleware
- Templates directory: `dkp/templates/`
- Static directory: `dkp/static/`
- Collected to: `dkp/staticfiles/`

## Message Flow

1. **Anesthetist** connects to WebSocket, selects Operating Room
2. **Nurse/Surgeon** connects to WebSocket, selects Ward
3. Anesthetist sends messages to specific roles in specific locations
4. Recipients must acknowledge messages (stored in MessageLog with timestamps)
5. All messages are persisted in PostgreSQL for audit trail

## Important Notes

- All manage.py commands must be run from the `dkp/` directory or use `python dkp/manage.py`
- Makefile handles the directory navigation automatically
- WebSocket connections require Redis server to be running
- Admin interface available at `/admin` for monitoring message logs and system configuration
- **Development Environment**: Please assume that Redis, PostgreSQL database, and Django development server are already running in the background