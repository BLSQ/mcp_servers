#!/bin/bash

# =============================================================================
# OpenHEXA MCP Server Installer for Gemini
# =============================================================================
# Run this script from your workspace folder to configure the OpenHEXA MCP server.
#
# Prerequisites:
#   - Gemini CLI installed
#
# Usage:
#   cd /path/to/your/workspace
#   ./setup_gemini_openhexa_mcp.sh <OPENHEXA_TOKEN>
#
# Parameters:
#   OPENHEXA_TOKEN - Your OpenHEXA API token (required)
#
# The script will:
#   1. Add the OpenHEXA MCP server using gemini CLI
#   2. Export OPENHEXA_TOKEN to your shell profile (~/.bashrc or ~/.zshrc)
#   3. Update .gemini/settings.json with proper MCP configuration
# =============================================================================

set -e

# Check for required argument
if [ -z "$1" ]; then
    echo "Error: OPENHEXA_TOKEN is required"
    echo ""
    echo "Usage: ./setup_gemini_openhexa_mcp.sh <OPENHEXA_TOKEN>"
    exit 1
fi

OPENHEXA_TOKEN="$1"
CURRENT_DIR="$(pwd)"
SETTINGS_FILE="$CURRENT_DIR/.gemini/settings.json"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  OpenHEXA MCP Server Installer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if .gemini folder exists
if [ ! -d "$CURRENT_DIR/.gemini" ]; then
    echo -e "${YELLOW}⚠ No .gemini folder found in current directory${NC}"
    echo ""
    echo -e "Current path: ${BLUE}$CURRENT_DIR${NC}"
    echo ""
    read -p "Create .gemini/ here? [y/N]: " confirm

    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${RED}Installation cancelled.${NC}"
        exit 1
    fi
    mkdir -p "$CURRENT_DIR/.gemini"
    echo ""
fi

# Step 1: Add OpenHEXA MCP server
echo -e "${BLUE}[1/3]${NC} Adding OpenHEXA MCP server..."
gemini mcp add openhexa https://api.openhexa.org/mcp/ --transport http 2>/dev/null || true
echo -e "${GREEN}✓${NC} MCP server entry created"

# Step 2: Add OPENHEXA_TOKEN to shell profiles
echo -e "${BLUE}[2/3]${NC} Setting OPENHEXA_TOKEN environment variable..."

# Function to add token to a profile file
add_token_to_profile() {
    local profile="$1"
    if [ ! -f "$profile" ]; then
        return
    fi

    if grep -q "^export OPENHEXA_TOKEN=" "$profile" 2>/dev/null; then
        sed -i "s|^export OPENHEXA_TOKEN=.*|export OPENHEXA_TOKEN=\"$OPENHEXA_TOKEN\"|" "$profile"
        echo -e "${GREEN}✓${NC} Updated OPENHEXA_TOKEN in $profile"
    else
        echo "" >> "$profile"
        echo "# OpenHEXA API Token" >> "$profile"
        echo "export OPENHEXA_TOKEN=\"$OPENHEXA_TOKEN\"" >> "$profile"
        echo -e "${GREEN}✓${NC} Added OPENHEXA_TOKEN to $profile"
    fi
}

# Add to both bashrc and zshrc if they exist
add_token_to_profile "$HOME/.bashrc"
add_token_to_profile "$HOME/.zshrc"

# Fallback to .profile if neither exists
if [ ! -f "$HOME/.bashrc" ] && [ ! -f "$HOME/.zshrc" ]; then
    add_token_to_profile "$HOME/.profile"
fi

# Export for current session
export OPENHEXA_TOKEN="$OPENHEXA_TOKEN"

# Step 3: Update settings.json with proper configuration
echo -e "${BLUE}[3/3]${NC} Configuring MCP server settings..."

# Create settings.json if it doesn't exist
if [ ! -f "$SETTINGS_FILE" ]; then
    echo '{}' > "$SETTINGS_FILE"
    echo -e "${YELLOW}Created new settings.json${NC}"
fi

# Use Python to safely update the JSON
python3 << EOF
import json

settings_file = "$SETTINGS_FILE"

try:
    with open(settings_file, 'r') as f:
        content = f.read().strip()
        settings = json.loads(content) if content else {}
except (json.JSONDecodeError, FileNotFoundError):
    settings = {}

if 'mcpServers' not in settings:
    settings['mcpServers'] = {}

settings['mcpServers']['openhexa'] = {
    "httpUrl": "https://api.openhexa.org/mcp",
    "headers": {
        "Authorization": "Bearer \${OPENHEXA_TOKEN}",
        "Content-Type": "application/json"
    },
    "timeout": 60000,
    "trust": True
}

with open(settings_file, 'w') as f:
    json.dump(settings, f, indent=2)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Settings configured"
else
    echo -e "${RED}✗${NC} Failed to update settings"
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✓ OpenHEXA MCP Server Configured${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Settings file: ${BLUE}$SETTINGS_FILE${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Restart your terminal to use OPENHEXA_TOKEN."
echo ""
