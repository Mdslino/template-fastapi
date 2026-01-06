#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
POSTGRES_SERVER=${POSTGRES_SERVER:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_DB=${POSTGRES_DB:-postgres}

# Check if database is available
echo -e "${YELLOW}Checking database connection...${NC}"

# Try to connect to the database using psql or pg_isready
if command -v pg_isready &> /dev/null; then
    pg_isready -h "$POSTGRES_SERVER" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" &> /dev/null
    DB_STATUS=$?
else
    # Fallback to nc (netcat) to check if port is open
    nc -z "$POSTGRES_SERVER" "$POSTGRES_PORT" &> /dev/null
    DB_STATUS=$?
fi

if [ $DB_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Database is available at ${POSTGRES_SERVER}:${POSTGRES_PORT}${NC}"
    echo -e "${BLUE}Running migrations...${NC}\n"
    
    # Run the alembic command with all passed arguments
    uv run alembic "$@"
else
    echo -e "${RED}✗ Database connection failed!${NC}"
    echo -e "${YELLOW}Could not connect to PostgreSQL at ${POSTGRES_SERVER}:${POSTGRES_PORT}${NC}"
    echo ""
    echo -e "${YELLOW}Please make sure:${NC}"
    echo -e "  1. PostgreSQL is running"
    echo -e "  2. Database connection settings in .env are correct"
    echo -e "  3. Run: ${GREEN}make run-db${NC} or ${GREEN}docker-compose up -d${NC}"
    echo ""
    exit 1
fi
