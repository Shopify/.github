# Google Cloud Credentials Setup Guide

This guide provides detailed instructions for obtaining and configuring Google Cloud credentials for the MCP connection.

## Table of Contents
1. [Creating a Google Cloud Project](#creating-a-google-cloud-project)
2. [Enabling Required APIs](#enabling-required-apis)
3. [Service Account Setup](#service-account-setup)
4. [OAuth Setup (Optional)](#oauth-setup-optional)
5. [Security Best Practices](#security-best-practices)

---

## Creating a Google Cloud Project

### Step 1: Access Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Accept the Terms of Service if prompted

### Step 2: Create New Project
1. Click the project dropdown at the top of the page
2. Click **"New Project"**
3. Enter project details:
   - **Project name**: e.g., "MCP Google Integration"
   - **Organization**: (optional) Select your organization
   - **Location**: (optional) Select parent folder
4. Click **"Create"**
5. Wait for the project to be created (usually takes a few seconds)

### Step 3: Note Your Project ID
- Your Project ID will be displayed (e.g., `mcp-integration-123456`)
- **Save this** - you'll need it for API calls and billing

---

## Enabling Required APIs

You need to enable the Google APIs you plan to use. Here's how:

### Method 1: Via Console UI

1. In Google Cloud Console, select your project
2. Navigate to **"APIs & Services" > "Library"**
3. Search for and enable each of these APIs:

#### Essential APIs:
- ? **Google Drive API** - For file access and management
  - Search: "Google Drive API"
  - Click "Enable"
  
- ? **Gmail API** - For email operations
  - Search: "Gmail API"
  - Click "Enable"
  
- ? **Google Calendar API** - For calendar management
  - Search: "Google Calendar API"
  - Click "Enable"

#### Optional APIs:
- ?? **Google Maps Platform** - For location services
  - Enable: Maps JavaScript API, Places API, Geocoding API
  
- ?? **Custom Search API** - For web search
  - Search: "Custom Search API"
  - Note: Requires additional setup

### Method 2: Via gcloud CLI

If you have gcloud CLI installed:

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable drive.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable maps-backend.googleapis.com
gcloud services enable customsearch.googleapis.com
```

### Verify Enabled APIs
```bash
gcloud services list --enabled
```

---

## Service Account Setup

Service accounts are used for application-level access (recommended for most MCP use cases).

### Step 1: Create Service Account

1. Navigate to **"IAM & Admin" > "Service Accounts"**
2. Click **"Create Service Account"**
3. Fill in details:
   ```
   Service account name: mcp-google-connector
   Service account ID: mcp-google-connector (auto-generated)
   Description: Service account for MCP Google integration
   ```
4. Click **"Create and Continue"**

### Step 2: Grant Permissions

Choose the appropriate roles based on your needs:

#### For Google Drive:
- **Basic Access**: `roles/drive.reader` (read-only)
- **Full Access**: `roles/drive.admin` or `roles/drive.file` (read/write)

#### For Gmail:
- **Basic Access**: `roles/gmail.readonly`
- **Full Access**: `roles/gmail.admin`

#### For Google Calendar:
- **Basic Access**: `roles/calendar.reader`
- **Full Access**: `roles/calendar.admin`

**Recommendation**: Start with read-only access and expand as needed.

### Step 3: Create and Download JSON Key

1. After creating the service account, click on it
2. Go to the **"Keys"** tab
3. Click **"Add Key" > "Create New Key"**
4. Select **"JSON"** as the key type
5. Click **"Create"**
6. The JSON key file will automatically download
   - Filename format: `PROJECT_ID-RANDOM_STRING.json`
   
### Step 4: Secure the Credentials

**CRITICAL SECURITY STEP:**

```bash
# Create secure directory
mkdir -p ~/.config/google-mcp

# Move the downloaded file
mv ~/Downloads/your-project-*-*.json ~/.config/google-mcp/credentials.json

# Set strict permissions (owner read/write only)
chmod 600 ~/.config/google-mcp/credentials.json

# Verify permissions
ls -l ~/.config/google-mcp/credentials.json
# Should show: -rw------- (owner read/write only)
```

### Step 5: Understanding the Credentials File

Your JSON key file contains:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Never share or commit this file!**

---

## OAuth Setup (Optional)

Use OAuth for user-specific data access (e.g., accessing a specific user's Gmail).

### When to Use OAuth vs Service Account

| Use Case | Recommendation |
|----------|----------------|
| Access your own Drive files | OAuth |
| Access organization Drive | Service Account |
| Read/send personal Gmail | OAuth |
| Application-level access | Service Account |
| Multiple user access | OAuth |

### Step 1: Create OAuth Client ID

1. Navigate to **"APIs & Services" > "Credentials"**
2. Click **"Create Credentials" > "OAuth Client ID"**
3. If prompted, configure the OAuth consent screen:
   - User Type: **"External"** (for personal use) or **"Internal"** (for organization)
   - Fill in required fields (App name, User support email)
   - Add scopes you need
   - Add test users (for external apps)
   
4. For Application Type, select **"Desktop App"**
5. Name it (e.g., "MCP Google OAuth")
6. Click **"Create"**
7. Download the JSON file

### Step 2: OAuth Scopes

Configure the scopes your application needs:

```
# Google Drive
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/drive

# Gmail
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.modify

# Calendar
https://www.googleapis.com/auth/calendar.readonly
https://www.googleapis.com/auth/calendar
```

### Step 3: Configure MCP with OAuth

Update your MCP configuration:

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

### Step 4: First-Time Authorization

1. The first time you use the MCP connection, you'll be prompted to authorize
2. A browser window will open
3. Sign in with your Google account
4. Review and accept the requested permissions
5. The access token will be stored securely

---

## Security Best Practices

### ? DO:

1. **Use least privilege principle**
   - Only grant the minimum required permissions
   - Start with read-only access

2. **Secure your credentials**
   ```bash
   # Proper permissions
   chmod 600 ~/.config/google-mcp/credentials.json
   
   # Add to .gitignore
   echo "credentials.json" >> .gitignore
   echo "*.json" >> .gitignore
   ```

3. **Rotate keys regularly**
   - Generate new service account keys every 90 days
   - Delete old keys after rotation

4. **Monitor usage**
   - Check Google Cloud Console for unexpected API calls
   - Set up billing alerts
   - Review service account activity logs

5. **Use separate service accounts**
   - One per application or environment
   - Makes debugging and auditing easier

### ? DON'T:

1. **Never commit credentials to version control**
   ```bash
   # Check for accidentally committed credentials
   git log --all --full-history -- "*credentials*"
   ```

2. **Never share credentials**
   - Don't send via email, chat, or cloud storage
   - Don't embed in code or documentation

3. **Never use production credentials for testing**
   - Create separate projects for dev/test/prod

4. **Never grant excessive permissions**
   - Avoid "Owner" or "Editor" roles unless absolutely necessary

### ?? Auditing

Regularly review:
- Service account key age (rotate old keys)
- Granted permissions (remove unused permissions)
- API usage (detect anomalies)
- Access logs (check for unauthorized access)

---

## Troubleshooting

### Error: "The caller does not have permission"

**Solution**: Add the required role to your service account:
1. Go to **IAM & Admin > IAM**
2. Find your service account
3. Click edit (pencil icon)
4. Add the necessary role
5. Save

### Error: "API not enabled"

**Solution**: Enable the API:
```bash
gcloud services enable [API_NAME].googleapis.com
```

Or via console: **APIs & Services > Library**

### Error: "Invalid grant"

**Possible causes**:
- Service account key has been deleted
- Project has been disabled
- System clock is out of sync

**Solution**: Generate a new key or check project status

### Error: "Quota exceeded"

**Solution**:
1. Check quota limits in **APIs & Services > Quotas**
2. Request quota increase if needed
3. Implement rate limiting in your application

---

## Additional Resources

- [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs)
- [Service Accounts Best Practices](https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Google APIs Explorer](https://developers.google.com/apis-explorer)
- [Quotas and Limits](https://cloud.google.com/docs/quota)

---

## Quick Reference

### Commands Cheat Sheet

```bash
# List enabled APIs
gcloud services list --enabled

# Enable an API
gcloud services enable [API_NAME].googleapis.com

# List service accounts
gcloud iam service-accounts list

# Create service account key
gcloud iam service-accounts keys create ~/key.json \
  --iam-account=SERVICE_ACCOUNT_EMAIL

# List service account keys
gcloud iam service-accounts keys list \
  --iam-account=SERVICE_ACCOUNT_EMAIL

# Delete a service account key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=SERVICE_ACCOUNT_EMAIL
```

### Environment Variables

```bash
# Service Account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# OAuth
export GOOGLE_OAUTH_CLIENT_ID="your-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="your-secret"
export GOOGLE_OAUTH_REDIRECT_URI="http://localhost:3000/oauth/callback"

# Project
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

---

**Last Updated**: 2025-10-31  
**Version**: 1.0
