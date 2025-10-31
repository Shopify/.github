# Google MCP Connection Setup Guide

This guide will walk you through connecting to Google services via the Model Context Protocol (MCP).

## What is MCP?

Model Context Protocol (MCP) is an open protocol that enables AI assistants to securely connect to various data sources and tools. The Google MCP server allows integration with Google services like Drive, Gmail, Calendar, Maps, and Search.

## Prerequisites

- Node.js 16 or higher
- Google Cloud account
- Cursor IDE or Claude Desktop (or any MCP-compatible client)

## Step 1: Install Node.js (if not already installed)

Check if Node.js is installed:
```bash
node --version
```

If not installed, download from [nodejs.org](https://nodejs.org/) or use a package manager:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install nodejs npm

# macOS
brew install node

# Windows
winget install OpenJS.NodeJS
```

## Step 2: Set Up Google Cloud Credentials

### 2.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

### 2.2 Enable Required APIs

Enable the APIs you want to use:
- **Google Drive API** - For file access
- **Gmail API** - For email operations
- **Google Calendar API** - For calendar management
- **Google Maps Platform** - For location services
- **Custom Search API** - For web search

Enable them via:
```bash
gcloud services enable drive.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable maps-backend.googleapis.com
```

Or enable via the [API Library](https://console.cloud.google.com/apis/library)

### 2.3 Create Service Account

1. Navigate to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name it (e.g., "mcp-google-connector")
4. Grant necessary roles:
   - **Google Drive**: "Drive Admin" or "Drive API User"
   - **Gmail**: "Gmail API User"
   - **Calendar**: "Calendar API User"
5. Click **Done**

### 2.4 Generate JSON Key

1. Click on the service account you created
2. Go to **Keys** tab
3. Click **Add Key > Create New Key**
4. Select **JSON** format
5. Download the key file
6. **Important**: Keep this file secure and never commit it to version control!

### 2.5 Save Credentials

Save the JSON key file to a secure location:
```bash
# Recommended location
mkdir -p ~/.config/google-mcp
mv ~/Downloads/your-project-*-*.json ~/.config/google-mcp/credentials.json
chmod 600 ~/.config/google-mcp/credentials.json
```

## Step 3: Install Google MCP Server

You have two options:

### Option A: Global Installation (Recommended)
```bash
npm install -g @modelcontextprotocol/server-google
```

### Option B: Use npx (No Installation)
The configuration will use `npx` to run the server on-demand.

## Step 4: Configure MCP Client

### For Cursor IDE

Create or edit the MCP configuration file:

**Location:**
- **Linux**: `~/.config/cursor/mcp_settings.json`
- **macOS**: `~/Library/Application Support/Cursor/mcp_settings.json`
- **Windows**: `%APPDATA%\Cursor\mcp_settings.json`

**Configuration:**
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

**Replace** `/home/YOUR_USERNAME/` with your actual home directory path.

### For Claude Desktop

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

Use the same JSON configuration as above.

## Step 5: Configure OAuth (Optional, for User-Based Access)

For accessing user-specific data (recommended for Gmail, Drive):

1. Create OAuth 2.0 Credentials:
   - Go to **APIs & Credentials > Create Credentials > OAuth Client ID**
   - Choose **Desktop App**
   - Download the JSON file

2. Update your MCP configuration:
```json
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-client-secret",
        "GOOGLE_OAUTH_REDIRECT_URI": "http://localhost:3000/oauth/callback"
      }
    }
  }
}
```

## Step 6: Restart Your MCP Client

1. **Cursor**: Restart the application
2. **Claude Desktop**: Restart the application

## Step 7: Verify Connection

After restart, you should see Google MCP tools available. Try:
- "List files in my Google Drive"
- "Search my Gmail for recent messages"
- "Show my calendar events for today"

## Troubleshooting

### Error: "Cannot find module"
```bash
npm install -g @modelcontextprotocol/server-google
```

### Error: "Invalid credentials"
- Verify the path to your credentials.json is correct
- Check file permissions (should be readable)
- Ensure the service account has the necessary API permissions

### Error: "API not enabled"
Enable the required API in Google Cloud Console:
```bash
gcloud services enable [API_NAME]
```

### Connection timeout
- Check your internet connection
- Verify firewall settings aren't blocking the connection
- Try increasing timeout in MCP settings

### No tools appearing
1. Check the MCP server logs (usually in client app logs)
2. Verify the configuration file syntax is valid JSON
3. Ensure the command path is correct

## Available Google MCP Tools

Once connected, you'll have access to:

- **Google Drive**: File search, read, write, create, delete
- **Gmail**: Email search, read, send, compose
- **Google Calendar**: Event creation, viewing, updating
- **Google Maps**: Location search, directions, geocoding
- **Google Search**: Web search capabilities

## Security Best Practices

1. ? **Never commit credentials to git**
   ```bash
   echo "credentials.json" >> .gitignore
   echo "*.json" >> .gitignore  # if storing in repo
   ```

2. ? **Use least privilege** - Only grant necessary API permissions

3. ? **Rotate keys regularly** - Generate new service account keys periodically

4. ? **Monitor usage** - Check Google Cloud Console for unexpected API calls

5. ? **Use OAuth for user data** - Service accounts for application data

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google Cloud IAM Guide](https://cloud.google.com/iam/docs)
- [Google APIs Documentation](https://developers.google.com/apis-explorer)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review MCP client logs
3. Verify Google Cloud Console for API quotas and errors
4. Consult the [MCP GitHub repository](https://github.com/modelcontextprotocol)

---

**Last Updated**: 2025-10-31
