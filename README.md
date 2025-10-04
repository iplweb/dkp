# DKP - Direct Communication Protocol

Hospital communication system built with Django Channels for real-time WebSocket communication.

## Features

- **Role-based communication**: Anesthetist, Nurse, and Surgeon roles
- **Real-time messaging**: WebSocket-based instant communication
- **Location-based channels**: Operating Rooms and Wards
- **Message logging**: Tracks sent and acknowledged messages with timestamps
- **Notifications**: Visual alerts and sound notifications for new messages
- **Heartbeat system**: 3-second ping to monitor connection status

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd szpital-django-ws
```

2. Install dependencies:
```bash
make install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database and Redis settings
```

4. Set up PostgreSQL database:
```sql
CREATE DATABASE dkp;
CREATE USER dkp WITH PASSWORD 'dkp';
GRANT ALL PRIVILEGES ON DATABASE dkp TO dkp;
```

5. Run migrations:
```bash
make migrate
```

6. Collect static files:
```bash
make collectstatic
```

## Running the Application

### Development Server

1. Start Redis server:
```bash
redis-server
```

2. Start Django Channels server:
```bash
make run
```

3. Access the application at http://localhost:8000

## Usage

1. **Select Role**: Choose Anesthetist, Nurse, or Surgeon
2. **Select Location**:
   - Anesthetist: Select Operating Room
   - Nurse/Surgeon: Select Ward
3. **Communication**:
   - **Anesthetist**: Can send messages to Nurses and Surgeons
   - **Nurse/Surgeon**: Receive messages and must acknowledge them

## Message Types

- `CAN_ACCEPT_PATIENTS`: From Anesthetist to Nurse
- `SURGERY_DONE`: From Anesthetist to Nurse
- `PATIENT_IN_THE_OR`: From Anesthetist to Surgeon

## Development Commands

```bash
make install      # Install dependencies
make migrate      # Run migrations
make run         # Run development server
make shell       # Open Django shell
make test        # Run tests
make clean       # Clean cache files
make superuser   # Create admin user
```

## Architecture

- **Django**: Web framework
- **Django Channels**: WebSocket support
- **Redis**: Channel layer for WebSocket communication
- **PostgreSQL**: Database for data persistence
- **Daphne**: ASGI server

## Admin Interface

Access the admin interface at http://localhost:8000/admin to:
- View message logs
- Manage roles, operating rooms, and wards
- Monitor system activity