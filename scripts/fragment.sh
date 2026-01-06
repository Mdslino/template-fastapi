#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Create a new changelog fragment${NC}"
echo ""

# Display fragment types menu
echo "Select fragment type:"
echo "  1) feature       - New features and functionality"
echo "  2) bugfix        - Bug fixes"
echo "  3) doc           - Documentation changes"
echo "  4) removal       - Deprecations and removals"
echo "  5) misc          - Miscellaneous changes"
echo ""

# Read fragment type choice
read -p "Enter choice [1-5]: " choice

case $choice in
    1) type="feature" ;;
    2) type="bugfix" ;;
    3) type="doc" ;;
    4) type="removal" ;;
    5) type="misc" ;;
    *)
        echo -e "${YELLOW}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Selected type: ${GREEN}${type}${NC}"
echo ""

# Read fragment message
read -p "Enter fragment message: " msg

if [ -z "$msg" ]; then
    echo -e "${YELLOW}Error: Message cannot be empty${NC}"
    exit 1
fi

# Create fragment file
timestamp=$(date +%s)
filename="fragments/${timestamp}.${type}"
echo "$msg" > "$filename"

echo ""
echo -e "${GREEN}✓ Created fragment: ${filename}${NC}"
echo -e "${GREEN}  Message: ${msg}${NC}"
