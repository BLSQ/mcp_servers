#!/bin/bash

# =============================================================================
# BLSQ Gemini Skills Installer
# =============================================================================
# Run this script from your workspace folder to install/update Gemini skills.
#
# Usage:
#   cd /path/to/your/workspace
#   ./setup_gemini_skills.sh
#
# The script will:
#   1. Clone the BLSQ repo to a temp folder
#   2. Copy skills to .claude/skills/ in the current directory
#   3. If .claude doesn't exist, ask for confirmation before creating it
# =============================================================================

set -e

REPO_URL="https://github.com/BLSQ/mcp_servers.git"
TEMP_DIR="/tmp/blsq_mcp_servers_$$"
CURRENT_DIR="$(pwd)"
DEST_PATH="$CURRENT_DIR/.claude/skills"

# Cleanup function - ensures temp folder is removed even on error/interrupt
cleanup() {
    rm -rf "$TEMP_DIR" 2>/dev/null
}
trap cleanup EXIT

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  BLSQ Gemini Skills Installer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if .claude folder exists
if [ ! -d "$CURRENT_DIR/.claude" ]; then
    echo -e "${YELLOW}⚠ No .claude folder found in current directory${NC}"
    echo ""
    echo -e "Current path: ${BLUE}$CURRENT_DIR${NC}"
    echo ""
    echo "Are you in the correct workspace folder?"
    read -p "Create .claude/skills/ here? [y/N]: " confirm

    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${RED}Installation cancelled.${NC}"
        echo "Please navigate to your workspace folder and run the script again."
        exit 1
    fi
    echo ""
fi

# Step 1: Clone repo to temp folder
echo -e "${BLUE}[1/4]${NC} Fetching latest skills from GitHub..."
rm -rf "$TEMP_DIR"
git clone --depth 1 --quiet "$REPO_URL" "$TEMP_DIR"
echo -e "${GREEN}✓${NC} Downloaded latest skills"

# Step 2: Create folders if needed
echo -e "${BLUE}[2/4]${NC} Preparing destination..."
mkdir -p "$DEST_PATH"
echo -e "${GREEN}✓${NC} Ready: $DEST_PATH"

# Step 3: Copy skills
echo -e "${BLUE}[3/4]${NC} Installing skills..."
cp -r "$TEMP_DIR/.claude/skills/"* "$DEST_PATH/"
echo -e "${GREEN}✓${NC} Skills copied"

# Step 4: Cleanup (also handled by trap on exit)
echo -e "${BLUE}[4/4]${NC} Cleaning up temp files..."
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✓${NC} Temp folder removed"

# Count skills
SKILL_COUNT=$(find "$DEST_PATH" -maxdepth 1 -type d | wc -l)
SKILL_COUNT=$((SKILL_COUNT - 1))

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✓ Installed $SKILL_COUNT skills${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Skills installed:"
for skill in "$DEST_PATH"/*/; do
    [ -d "$skill" ] && echo "  • $(basename "$skill")"
done
echo ""
echo -e "Location: ${BLUE}$DEST_PATH${NC}"
