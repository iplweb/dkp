#!/usr/bin/env python3
"""
Database wait script for Docker containers
Waits for PostgreSQL database to be available before proceeding.
Usage: python docker/scripts/wait-for-db.py
"""

import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError
from decouple import config

def wait_for_db():
    """Wait for database to be available."""
    db_host = config('DB_HOST', default='postgres')
    db_name = config('DB_NAME', default='dkp')
    db_user = config('DB_USER', default='dkp')
    db_password = config('DB_PASSWORD', default='dkp')
    db_port = config('DB_PORT', default='5432')

    max_attempts = 30
    attempt = 0

    print(f"Waiting for database at {db_host}:{db_port}...")

    while attempt < max_attempts:
        try:
            connection = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password,
                port=db_port,
                connect_timeout=5
            )
            print("Database is ready!")
            connection.close()
            return True
        except OperationalError as e:
            attempt += 1
            print(f"Attempt {attempt}/{max_attempts}: Database not ready ({e})")
            time.sleep(2)

    print("Failed to connect to database after maximum attempts")
    return False

def wait_for_redis():
    """Wait for Redis to be available."""
    redis_url = config('REDIS_URL', default='redis://redis:6379/0')
    max_attempts = 30
    attempt = 0

    print(f"Waiting for Redis at {redis_url}...")

    # Parse Redis URL
    try:
        import redis
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 6379
        db = parsed.path.lstrip('/') or 0

        while attempt < max_attempts:
            try:
                r = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=5)
                r.ping()
                print("Redis is ready!")
                return True
            except redis.ConnectionError as e:
                attempt += 1
                print(f"Attempt {attempt}/{max_attempts}: Redis not ready ({e})")
                time.sleep(2)

        print("Failed to connect to Redis after maximum attempts")
        return False
    except ImportError:
        print("Redis client not available, skipping Redis check")
        return True

if __name__ == "__main__":
    db_ready = wait_for_db()
    redis_ready = wait_for_redis()

    if db_ready and redis_ready:
        print("All services are ready!")
        sys.exit(0)
    else:
        print("Some services are not ready!")
        sys.exit(1)