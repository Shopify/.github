## Slack + Google Drive Search Assistant

This app lets your Slack users find Google Drive documents via a slash command or by mentioning the bot.

### Features

- `/finddoc <query>`: searches Google Drive (My Drive + Shared drives)
- App mentions: `@bot <query>` returns top matches
- Domain-wide delegation: searches as an impersonated user so you respect permissions

### Prerequisites

- Node.js 18+
- Slack App with Socket Mode enabled
- Google Cloud project with a Service Account and Domain-Wide Delegation (Workspace domain)

### Setup

1) Install dependencies

```bash
npm install
```

2) Configure environment

Copy `.env.example` to `.env` and fill in values.

Required:
- `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_SIGNING_SECRET`
- One of `GOOGLE_CREDENTIALS_JSON` or `GOOGLE_CREDENTIALS_FILE`
- `GOOGLE_IMPERSONATED_USER` (an email in your Workspace)

3) Slack configuration

- Enable Socket Mode and generate an App Token (connections:write)
- Bot Token scopes: `app_mentions:read`, `commands`, `chat:write`, `files:write`
- Add Slash Command `/finddoc` with Request URL: `https://example.com` (for local Socket Mode, the URL isn't used)
- Install the app to your workspace

4) Google configuration

- Create a Service Account in Google Cloud
- Download JSON key and set as `GOOGLE_CREDENTIALS_JSON` or point `GOOGLE_CREDENTIALS_FILE`
- Enable the Drive API
- In Admin Console, grant domain-wide delegation to the service account with scopes:
  - `https://www.googleapis.com/auth/drive.readonly`
- Set `GOOGLE_IMPERSONATED_USER` to a user to impersonate

If you only need public link retrieval (no domain delegation), you can omit impersonation and query only files visible to the service account, but most org setups require domain-wide delegation to respect user-specific permissions in search results.

### Run

```bash
npm run dev
```

Then invite the bot to a channel and try:

```
/finddoc quarterly plan
```

or mention it:

```
@your-bot quarterly plan
```

### Notes

- For file uploads to Slack (small files), set `ENABLE_SMALL_FILE_UPLOAD=true` and tune `MAX_UPLOAD_BYTES`.

*Community health files for the @Shopify organization*

For more information, please see the article on [creating a default community health file for your organization](https://help.github.com/en/articles/creating-a-default-community-health-file-for-your-organization).
