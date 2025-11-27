#!/bin/bash

# Cursor Uninstall Script for Linux and macOS
# Usage: ./uninstall-cursor.sh [--full]
# Options:
#   --full    Performs a complete uninstall including all user data and configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
    echo "This script only supports Linux and macOS."
    exit 1
fi

# Parse arguments
FULL_UNINSTALL=false
if [[ "$1" == "--full" ]]; then
    FULL_UNINSTALL=true
fi

echo -e "${GREEN}Cursor Uninstall Script${NC}"
echo -e "Operating System: ${YELLOW}$OS${NC}"
echo ""

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
    echo -e "${YELLOW}Warning: Running as root. This may cause issues with removing user-specific files.${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to remove file/directory if it exists
remove_if_exists() {
    local path="$1"
    local use_sudo="$2"
    
    if [ -e "$path" ]; then
        echo "Removing: $path"
        if [ "$use_sudo" = "true" ]; then
            sudo rm -rf "$path"
        else
            rm -rf "$path"
        fi
    fi
}

# Check if Cursor is running
echo "Checking if Cursor is running..."
if [[ "$OS" == "macos" ]]; then
    if pgrep -x "Cursor" > /dev/null; then
        echo -e "${YELLOW}Cursor is currently running.${NC}"
        read -p "Would you like to quit Cursor now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            killall Cursor 2>/dev/null || true
            sleep 2
        else
            echo -e "${RED}Please quit Cursor before uninstalling.${NC}"
            exit 1
        fi
    fi
elif [[ "$OS" == "linux" ]]; then
    if pgrep -i cursor > /dev/null; then
        echo -e "${YELLOW}Cursor is currently running.${NC}"
        read -p "Would you like to quit Cursor now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pkill -i cursor 2>/dev/null || true
            sleep 2
        else
            echo -e "${RED}Please quit Cursor before uninstalling.${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo -e "${GREEN}Starting uninstallation...${NC}"
echo ""

# Platform-specific uninstallation
if [[ "$OS" == "macos" ]]; then
    echo "Removing Cursor application..."
    remove_if_exists "/Applications/Cursor.app" false
    
    echo "Removing user data and configuration..."
    remove_if_exists "$HOME/Library/Application Support/Cursor" false
    remove_if_exists "$HOME/Library/Preferences/com.cursor.plist" false
    remove_if_exists "$HOME/Library/Caches/Cursor" false
    remove_if_exists "$HOME/Library/Caches/com.cursor.Cursor" false
    remove_if_exists "$HOME/Library/Caches/com.cursor.ShipIt" false
    remove_if_exists "$HOME/Library/Logs/Cursor" false
    remove_if_exists "$HOME/Library/Saved Application State/com.cursor.savedState" false
    
elif [[ "$OS" == "linux" ]]; then
    echo "Removing Cursor application..."
    remove_if_exists "/opt/Cursor" true
    remove_if_exists "/usr/share/cursor" true
    remove_if_exists "$HOME/.local/share/cursor" false
    
    echo "Removing desktop entries..."
    remove_if_exists "$HOME/.local/share/applications/cursor.desktop" false
    remove_if_exists "/usr/share/applications/cursor.desktop" true
    
    echo "Removing symlinks..."
    remove_if_exists "/usr/bin/cursor" true
    remove_if_exists "/usr/local/bin/cursor" true
    
    echo "Removing user data and configuration..."
    remove_if_exists "$HOME/.config/Cursor" false
    remove_if_exists "$HOME/.cache/Cursor" false
    remove_if_exists "$HOME/.local/share/Cursor" false
fi

# Full uninstall: remove additional data
if [[ "$FULL_UNINSTALL" == true ]]; then
    echo ""
    echo -e "${YELLOW}Performing full uninstall (including all user data)...${NC}"
    remove_if_exists "$HOME/.cursor" false
    remove_if_exists "$HOME/.config/cursor" false
    
    # Search for any remaining cursor-related files
    echo "Searching for any remaining Cursor files..."
    if [[ "$OS" == "macos" ]]; then
        find "$HOME/Library" -iname "*cursor*" -maxdepth 3 2>/dev/null | while read -r file; do
            remove_if_exists "$file" false
        done
    fi
fi

echo ""
echo -e "${GREEN}Uninstallation complete!${NC}"
echo ""

# Verification
echo "Verifying uninstallation..."
FOUND_FILES=false

if [[ "$OS" == "macos" ]]; then
    if [ -d "/Applications/Cursor.app" ]; then
        echo -e "${YELLOW}Warning: /Applications/Cursor.app still exists${NC}"
        FOUND_FILES=true
    fi
elif [[ "$OS" == "linux" ]]; then
    if command -v cursor &> /dev/null; then
        echo -e "${YELLOW}Warning: 'cursor' command still available in PATH${NC}"
        FOUND_FILES=true
    fi
fi

if [[ "$FOUND_FILES" == false ]]; then
    echo -e "${GREEN}✓ Cursor has been successfully uninstalled!${NC}"
else
    echo -e "${YELLOW}⚠ Some Cursor files may still remain. Please check manually.${NC}"
fi

echo ""
echo "Thank you for using Cursor!"
echo ""

if [[ "$FULL_UNINSTALL" == false ]]; then
    echo -e "${YELLOW}Tip: Run with --full flag to remove all user data and configurations${NC}"
fi
