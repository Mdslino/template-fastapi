#!/usr/bin/env bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

set -e

# Linting
echo -e "${GREEN}Running linting...${NC}"

# Run ruff in format mode if MODE is set to fix
if [ "$1" = "fix" ]; then
  echo -e "${RED}Fixing linting errors...${NC}"
  ruff check --select I --fix
  ruff format
else
  echo -e "${RED}Checking linting errors...${NC}"
  ruff check --select I
fi