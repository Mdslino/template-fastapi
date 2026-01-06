#!/usr/bin/env bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

set -e

# Linting
echo -e "${GREEN}Running linting...${NC}"

# Run ruff in format mode if MODE is set to fix
if [ "$1" = "fix" ]; then
  echo -e "${YELLOW}Fixing linting errors...${NC}"
  uv run ruff check --select I --fix
  uv run ruff format
else
  echo -e "${YELLOW}Checking linting errors...${NC}"
  uv run ruff check --select I
fi
