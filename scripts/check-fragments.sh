#!/bin/bash

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Get the current branch name
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Skip check for main, master, develop, and release branches
if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]] || [[ "$current_branch" == "develop" ]] || [[ "$current_branch" =~ ^release/.* ]]; then
    exit 0
fi

# Determine base branch (main or master)
if git rev-parse --verify main >/dev/null 2>&1; then
    base_branch="main"
elif git rev-parse --verify master >/dev/null 2>&1; then
    base_branch="master"
else
    echo -e "${YELLOW}⚠ Warning: Could not determine base branch (main/master)${NC}"
    exit 0
fi

# Check if fragments directory exists
if [ ! -d "fragments" ]; then
    echo -e "${RED}✗ Error: fragments/ directory does not exist${NC}"
    exit 1
fi

# Get list of new fragment files added in this branch (excluding README.md)
# This checks for files that exist in current branch but not in base branch
committed_fragments=$(git diff --name-only --diff-filter=A "$base_branch"..."$current_branch" -- fragments/ | grep -v "README.md" || true)

# Check for fragments in stage (not yet committed)
staged_fragments=$(git diff --cached --name-only --diff-filter=A -- fragments/ | grep -v "README.md" || true)

# Combine both committed and staged fragments
all_new_fragments=$(printf "%s\n%s" "$committed_fragments" "$staged_fragments" | sort -u | grep -v '^$' || true)

if [ -z "$all_new_fragments" ]; then
    echo -e "${RED}✗ Error: No new changelog fragments found in this branch${NC}"
    echo -e "${YELLOW}Please create a changelog fragment before committing:${NC}"
    echo -e "  ${GREEN}make fragment${NC}"
    echo ""
    echo -e "${YELLOW}This check verifies that you've added a new fragment file in this branch.${NC}"
    echo -e "Or skip this check with: ${YELLOW}git commit --no-verify${NC}"
    exit 1
fi

fragment_count=$(echo "$all_new_fragments" | wc -l | tr -d ' ')
echo -e "${GREEN}✓ Found $fragment_count new fragment(s) in this branch (committed + staged)${NC}"
exit 0
