# Google MCP Quick Start Guide

Get connected to Google services via MCP in 5 minutes! ??

## Prerequisites
- ? Node.js 16+ installed
- ? Google account
- ? Cursor IDE or Claude Desktop

## Quick Setup (Linux/macOS)

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
chmod +x setup_google_mcp.sh
./setup_google_mcp.sh
```

The script will:
1. ? Check Node.js installation
2. ? Install Google MCP server
3. ? Set up credentials directory
4. ? Configure your MCP client
5. ? Provide next steps

### Option 2: Manual Setup

#### Step 1: Install MCP Server
```bash
npm install -g @modelcontextprotocol/server-google
```

#### Step 2: Get Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable these APIs:
   - Google Drive API
   - Gmail API
   - Google Calendar API
4. Create a Service Account
5. Generate & download JSON key

#### Step 3: Save Credentials
```bash
mkdir -p ~/.config/google-mcp
mv ~/Downloads/your-key-*.json ~/.config/google-mcp/credentials.json
chmod 600 ~/.config/google-mcp/credentials.json
```

#### Step 4: Configure MCP Client

**For Cursor** (`~/.config/cursor/mcp_settings.json`):
```json
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/home/YOUR_USERNAME/.config/google-mcp/credentials.json"
      }
    }
  }
}
```

**For Claude Desktop** (`~/.config/claude/claude_desktop_config.json`): Same config as above.

**Replace** `/home/YOUR_USERNAME/` with your actual path!

#### Step 5: Restart & Test
1. Restart Cursor or Claude Desktop
2. Try: "List my Google Drive files"

## Windows Quick Setup

### Step 1: Install MCP Server
```powershell
npm install -g @modelcontextprotocol/server-google
```

### Step 2: Get & Save Credentials
```powershell
# Create directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\google-mcp"

# Move credentials (adjust source path)
Move-Item "$env:USERPROFILE\Downloads\your-key-*.json" "$env:USERPROFILE\.config\google-mcp\credentials.json"
```

### Step 3: Configure MCP Client

**Config location**:
- Cursor: `%APPDATA%\Cursor\mcp_settings.json`
- Claude: `%APPDATA%\Claude\claude_desktop_config.json`

**Config content**:
```json
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\YOUR_USERNAME\\.config\\google-mcp\\credentials.json"
      }
    }
  }
}
```

**Replace** `YOUR_USERNAME` with your Windows username!

### Step 4: Restart & Test
Restart your application and test the connection.

## Verify Installation

After setup, test with these commands:

```
?? "List my Google Drive files"
?? "Show my recent Gmail messages"
?? "What's on my calendar today?"
?? "Search my Drive for documents about MCP"
```

## What's Available?

Once connected, you can:

### Google Drive
- ?? List, search, read, create, update, delete files
- ?? Manage folders and permissions
- ?? Download and upload files

### Gmail
- ?? Read, search, send emails
- ?? Manage labels and threads
- ?? Draft and compose messages

### Google Calendar
- ?? View, create, update events
- ? Manage event reminders
- ?? Handle attendees and invitations

### Google Maps (if enabled)
- ?? Search locations
- ??? Get directions
- ?? Geocoding and reverse geocoding

### Google Search (if enabled)
- ?? Web search capabilities
- ?? Custom search integration

## Troubleshooting

### "Cannot find module" error
```bash
npm install -g @modelcontextprotocol/server-google
```

### "Invalid credentials" error
- Verify credentials file path is correct
- Check file permissions: `ls -l ~/.config/google-mcp/credentials.json`
- Ensure service account has required API access

### "API not enabled" error
Enable missing APIs in [Google Cloud Console](https://console.cloud.google.com/apis/library)

### No tools appearing
1. Check config file syntax (must be valid JSON)
2. Verify command path is correct
3. Check application logs for errors
4. Restart your MCP client

## Need More Help?

- ?? **Detailed Setup**: See `GOOGLE_MCP_SETUP.md`
- ?? **Credentials Guide**: See `CREDENTIALS_GUIDE.md`
- ??? **Configuration Template**: See `mcp_config_template.json`

## Security Reminder

?? **NEVER commit your credentials.json to version control!**

The `.gitignore` file has been configured to prevent this, but always double-check:

```bash
git status  # Make sure credentials.json is not listed
```

## Next Steps

1. ? Complete setup using automated script or manual steps
2. ? Enable required APIs in Google Cloud Console
3. ? Restart your MCP client
4. ? Test the connection
5. ?? Start using Google services via MCP!

---

**Quick Links**:
- [Google Cloud Console](https://console.cloud.google.com/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google APIs Explorer](https://developers.google.com/apis-explorer)

**Created**: 2025-10-31
