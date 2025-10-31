#!/bin/bash
# Google MCP Setup Script
# This script helps you set up the Google MCP connection

set -e

echo "======================================"
echo "Google MCP Connection Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}?${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}?${NC} $1"
}

print_error() {
    echo -e "${RED}?${NC} $1"
}

# Check if Node.js is installed
echo "Step 1: Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js is installed: $NODE_VERSION"
else
    print_error "Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/ or use:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install nodejs npm"
    echo "  macOS: brew install node"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm is installed: $NPM_VERSION"
else
    print_error "npm is not installed!"
    exit 1
fi

# Ask if user wants to install the MCP server globally
echo ""
echo "Step 2: Install Google MCP Server"
read -p "Do you want to install @modelcontextprotocol/server-google globally? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Google MCP server..."
    npm install -g @modelcontextprotocol/server-google
    print_success "Google MCP server installed!"
else
    print_warning "Skipping installation. Configuration will use npx instead."
fi

# Create credentials directory
echo ""
echo "Step 3: Setting up credentials directory..."
CRED_DIR="$HOME/.config/google-mcp"
mkdir -p "$CRED_DIR"
print_success "Created directory: $CRED_DIR"

# Check for credentials file
CRED_FILE="$CRED_DIR/credentials.json"
echo ""
echo "Step 4: Google Cloud Credentials"
echo "You need to download your service account JSON key from Google Cloud Console."
echo ""
echo "Instructions:"
echo "1. Go to https://console.cloud.google.com/"
echo "2. Select your project (or create one)"
echo "3. Navigate to 'IAM & Admin > Service Accounts'"
echo "4. Create a service account or select an existing one"
echo "5. Go to 'Keys' tab and create a new JSON key"
echo "6. Download the key file"
echo ""

if [ -f "$CRED_FILE" ]; then
    print_success "Credentials file already exists at: $CRED_FILE"
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Keeping existing credentials."
    else
        read -p "Enter the path to your downloaded credentials JSON file: " INPUT_CRED_PATH
        if [ -f "$INPUT_CRED_PATH" ]; then
            cp "$INPUT_CRED_PATH" "$CRED_FILE"
            chmod 600 "$CRED_FILE"
            print_success "Credentials copied and secured!"
        else
            print_error "File not found: $INPUT_CRED_PATH"
        fi
    fi
else
    read -p "Enter the path to your downloaded credentials JSON file (or press Enter to skip): " INPUT_CRED_PATH
    if [ -n "$INPUT_CRED_PATH" ] && [ -f "$INPUT_CRED_PATH" ]; then
        cp "$INPUT_CRED_PATH" "$CRED_FILE"
        chmod 600 "$CRED_FILE"
        print_success "Credentials copied and secured!"
    else
        print_warning "Credentials not set. You'll need to manually copy them to: $CRED_FILE"
    fi
fi

# Detect OS and set config path
echo ""
echo "Step 5: Creating MCP configuration..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CURSOR_CONFIG="$HOME/.config/cursor/mcp_settings.json"
    CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CURSOR_CONFIG="$HOME/Library/Application Support/Cursor/mcp_settings.json"
    CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    CURSOR_CONFIG="$APPDATA/Cursor/mcp_settings.json"
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
else
    print_warning "Unknown OS type. You'll need to manually configure."
    exit 0
fi

echo "Select your MCP client:"
echo "1) Cursor IDE"
echo "2) Claude Desktop"
echo "3) Both"
echo "4) Skip (I'll configure manually)"
read -p "Enter choice [1-4]: " -n 1 -r CHOICE
echo

CONFIG_CONTENT=$(cat <<EOF
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "$CRED_FILE"
      }
    }
  }
}
EOF
)

configure_client() {
    local CONFIG_PATH=$1
    local CLIENT_NAME=$2
    
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$CONFIG_PATH")"
    
    if [ -f "$CONFIG_PATH" ]; then
        print_warning "Config file already exists: $CONFIG_PATH"
        read -p "Do you want to backup and replace it? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp "$CONFIG_PATH" "$CONFIG_PATH.backup.$(date +%Y%m%d_%H%M%S)"
            echo "$CONFIG_CONTENT" > "$CONFIG_PATH"
            print_success "$CLIENT_NAME configuration updated! (Backup created)"
        else
            print_warning "Skipping $CLIENT_NAME configuration."
        fi
    else
        echo "$CONFIG_CONTENT" > "$CONFIG_PATH"
        print_success "$CLIENT_NAME configuration created!"
    fi
}

case $CHOICE in
    1)
        configure_client "$CURSOR_CONFIG" "Cursor"
        ;;
    2)
        configure_client "$CLAUDE_CONFIG" "Claude Desktop"
        ;;
    3)
        configure_client "$CURSOR_CONFIG" "Cursor"
        configure_client "$CLAUDE_CONFIG" "Claude Desktop"
        ;;
    4)
        print_warning "Skipping automatic configuration."
        echo "You can manually create the config file at:"
        echo "  Cursor: $CURSOR_CONFIG"
        echo "  Claude: $CLAUDE_CONFIG"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Final instructions
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
print_success "Google MCP is configured!"
echo ""
echo "Next steps:"
echo "1. Ensure you have enabled the required Google APIs in Cloud Console:"
echo "   - Google Drive API"
echo "   - Gmail API"
echo "   - Google Calendar API"
echo "   - Google Maps API (if needed)"
echo "   - Custom Search API (if needed)"
echo ""
echo "2. Restart your MCP client (Cursor or Claude Desktop)"
echo ""
echo "3. Test the connection by asking your AI assistant:"
echo "   - 'List my Google Drive files'"
echo "   - 'Show my calendar for today'"
echo ""
echo "For more details, see GOOGLE_MCP_SETUP.md"
echo ""
print_warning "Remember: Never commit your credentials.json file to version control!"
echo ""
