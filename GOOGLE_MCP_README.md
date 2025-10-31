# Google MCP Connection Documentation

Complete setup documentation and tools for connecting to Google services via Model Context Protocol (MCP).

## ?? Documentation Overview

This repository contains everything you need to connect your MCP client (Cursor IDE or Claude Desktop) to Google services.

### Quick Navigation

| Document | Purpose | Best For |
|----------|---------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | 5-minute setup guide | Getting started quickly |
| **[GOOGLE_MCP_SETUP.md](GOOGLE_MCP_SETUP.md)** | Comprehensive setup guide | Detailed instructions |
| **[CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md)** | Google Cloud credentials | Setting up authentication |
| **[mcp_config_template.json](mcp_config_template.json)** | Configuration template | Reference configuration |
| **[setup_google_mcp.sh](setup_google_mcp.sh)** | Automated setup script | Linux/macOS automated setup |

## ?? Getting Started

### Option 1: Quick Start (5 minutes)
Follow **[QUICKSTART.md](QUICKSTART.md)** for the fastest path to connection.

### Option 2: Automated Setup (Linux/macOS)
```bash
chmod +x setup_google_mcp.sh
./setup_google_mcp.sh
```

### Option 3: Manual Setup
Follow **[GOOGLE_MCP_SETUP.md](GOOGLE_MCP_SETUP.md)** for detailed step-by-step instructions.

## ?? What You Can Do

Once connected to Google MCP, you'll have access to:

### ?? Google Drive
- List, search, and manage files
- Read and write documents
- Create folders and organize content
- Share files and manage permissions

### ?? Gmail
- Read and search emails
- Send and compose messages
- Manage labels and threads
- Filter and organize inbox

### ?? Google Calendar
- View and create events
- Manage scheduling
- Handle attendees and invitations
- Set reminders and notifications

### ??? Google Maps
- Search locations
- Get directions
- Geocoding services
- Place information

### ?? Google Search
- Web search capabilities
- Custom search integration

## ?? Setup Checklist

- [ ] Node.js 16+ installed
- [ ] Google Cloud account created
- [ ] Google Cloud project created
- [ ] Required APIs enabled (Drive, Gmail, Calendar)
- [ ] Service account created
- [ ] JSON credentials downloaded
- [ ] Credentials saved securely
- [ ] MCP client configured (Cursor/Claude)
- [ ] Application restarted
- [ ] Connection tested

## ?? Prerequisites

### System Requirements
- **Node.js**: Version 16 or higher
- **npm**: Usually comes with Node.js
- **MCP Client**: Cursor IDE or Claude Desktop

### Google Cloud Requirements
- Google account
- Google Cloud project
- Enabled APIs:
  - Google Drive API
  - Gmail API
  - Google Calendar API
  - (Optional) Google Maps API
  - (Optional) Custom Search API

### Accounts & Access
- Google Cloud Console access
- Permission to create service accounts
- Permission to enable APIs

## ?? Detailed Documentation

### For First-Time Users
1. Start with **[QUICKSTART.md](QUICKSTART.md)**
2. Reference **[CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md)** for Google Cloud setup
3. Use the automated script `setup_google_mcp.sh` (Linux/macOS)

### For Advanced Setup
1. Read **[GOOGLE_MCP_SETUP.md](GOOGLE_MCP_SETUP.md)** thoroughly
2. Review **[CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md)** for OAuth setup
3. Customize **[mcp_config_template.json](mcp_config_template.json)** for your needs

### For Troubleshooting
- Check the Troubleshooting section in **[GOOGLE_MCP_SETUP.md](GOOGLE_MCP_SETUP.md)**
- Review credential issues in **[CREDENTIALS_GUIDE.md](CREDENTIALS_GUIDE.md)**
- Verify configuration against **[mcp_config_template.json](mcp_config_template.json)**

## ?? Security

### Critical Security Practices

? **DO:**
- Keep credentials.json secure (600 permissions)
- Use .gitignore to prevent committing credentials
- Rotate service account keys regularly
- Use least privilege principle for API access
- Monitor API usage in Google Cloud Console

? **DON'T:**
- Never commit credentials to version control
- Never share credentials via email/chat
- Never grant excessive permissions
- Never use production credentials for testing

### Files Excluded from Git
The `.gitignore` file automatically excludes:
- `credentials.json`
- `*-credentials.json`
- `google-credentials*.json`
- `mcp_settings.json` (may contain sensitive paths)
- `claude_desktop_config.json`

## ??? Scripts & Tools

### setup_google_mcp.sh
Interactive setup script that:
- ? Checks system requirements
- ? Installs Google MCP server
- ? Creates credentials directory
- ? Guides through credential setup
- ? Configures MCP client automatically
- ? Provides verification steps

**Usage:**
```bash
chmod +x setup_google_mcp.sh
./setup_google_mcp.sh
```

### mcp_config_template.json
Template configuration for MCP clients. Copy and customize for your setup.

**Usage:**
```bash
# For Cursor (Linux)
cp mcp_config_template.json ~/.config/cursor/mcp_settings.json

# For Claude Desktop (Linux)
cp mcp_config_template.json ~/.config/claude/claude_desktop_config.json

# Edit and update paths
nano ~/.config/cursor/mcp_settings.json
```

## ?? Testing Your Setup

After completing setup, test with these commands in your MCP client:

```
# Google Drive
"List my Google Drive files"
"Search my Drive for documents about MCP"

# Gmail
"Show my recent Gmail messages"
"Search my email for messages from last week"

# Calendar
"What's on my calendar today?"
"Show my upcoming meetings this week"

# General
"Help me organize my Drive files"
"Summarize my recent emails"
```

## ?? Common Issues

### Installation Issues
**Problem**: "Cannot find module @modelcontextprotocol/server-google"
**Solution**: 
```bash
npm install -g @modelcontextprotocol/server-google
```

### Credential Issues
**Problem**: "Invalid credentials" or "Permission denied"
**Solution**: 
1. Verify path to credentials.json
2. Check file permissions: `chmod 600 ~/.config/google-mcp/credentials.json`
3. Ensure service account has required API access

### API Issues
**Problem**: "API not enabled"
**Solution**: Enable the API in [Google Cloud Console](https://console.cloud.google.com/apis/library)

### Configuration Issues
**Problem**: No tools appearing in MCP client
**Solution**:
1. Verify JSON syntax in config file
2. Check config file location
3. Restart MCP client
4. Check application logs

## ?? Additional Resources

### Official Documentation
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Google APIs Documentation](https://developers.google.com/apis-explorer)

### Google Cloud Guides
- [IAM Best Practices](https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys)
- [Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)

### API-Specific Docs
- [Google Drive API](https://developers.google.com/drive)
- [Gmail API](https://developers.google.com/gmail/api)
- [Google Calendar API](https://developers.google.com/calendar)
- [Google Maps Platform](https://developers.google.com/maps)

## ?? Support

If you encounter issues:

1. **Check Documentation**: Review relevant guides above
2. **Verify Setup**: Run through checklist again
3. **Check Logs**: Look at MCP client logs for errors
4. **Test Credentials**: Verify Google Cloud Console settings
5. **Consult Community**: Check MCP GitHub issues

## ?? Version History

- **1.0** (2025-10-31)
  - Initial release
  - Complete setup documentation
  - Automated setup script
  - Configuration templates
  - Security best practices

## ??? Document Map

```
Google MCP Documentation/
?
??? QUICKSTART.md              # Start here! 5-min setup
??? GOOGLE_MCP_SETUP.md        # Comprehensive guide
??? CREDENTIALS_GUIDE.md       # Google Cloud setup
??? mcp_config_template.json   # Config template
??? setup_google_mcp.sh        # Automated setup
??? .gitignore                 # Security protection
??? GOOGLE_MCP_README.md       # This file
```

## ?? Next Steps

1. ? Choose your setup path (Quick/Automated/Manual)
2. ? Follow the guide step-by-step
3. ? Test your connection
4. ? Start using Google services via MCP!

---

**Created**: 2025-10-31  
**Last Updated**: 2025-10-31  
**Branch**: cursor/connect-to-google-mcp-8a44

For questions or improvements, please refer to the detailed documentation files linked above.
