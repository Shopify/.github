import { App } from "@slack/bolt";
import { config } from "../config";
import { logger } from "../logger";
import { createDriveClient, searchDriveFiles, downloadSmallFile } from "../google/drive";
import { maybeUploadSmallFile } from "./uploads";

export function createSlackApp() {
  const app = new App({
    token: config.slack.botToken,
    signingSecret: config.slack.signingSecret,
    appToken: config.slack.appToken,
    socketMode: true,
  });

  const drive = createDriveClient();

  app.command("/finddoc", async ({ ack, respond, command, client, body }) => {
    await ack();
    const query = command.text?.trim();
    if (!query) {
      await respond({ text: "Usage: /finddoc <search terms>", response_type: "ephemeral" });
      return;
    }
    await respond({ text: `Searching Google Drive for: ${query} …`, response_type: "ephemeral" });

    try {
      const results = await searchDriveFiles(drive, query, 10);
      if (results.length === 0) {
        await respond({ text: "No results found.", response_type: "ephemeral" });
        return;
      }

      const blocks = results.slice(0, 10).map((f) => ({
        type: "section",
        text: { type: "mrkdwn", text: `*<${f.webViewLink}|${f.name}>* — ${f.mimeType}\nOwner: ${(f.owners?.[0]?.displayName ?? "")}  Modified: ${f.modifiedTime ?? ""}` },
        accessory: f.iconLink ? { type: "image", image_url: f.iconLink, alt_text: f.mimeType } : undefined,
      }));

      // Optionally upload the first small file (if enabled and within size limit)
      const first = results[0];
      const sizeBytes = first.size ? Number(first.size) : Number.NaN;
      if (config.upload.enable && Number.isFinite(sizeBytes) && sizeBytes <= config.upload.maxBytes) {
        try {
          const buf = await downloadSmallFile(drive, first.id);
          await maybeUploadSmallFile({
            client,
            channel: command.channel_id,
            filename: first.name,
            content: buf,
            initialComment: `Uploading small file for “${query}”`,
          });
        } catch (e) {
          logger.warn({ err: e }, "Optional small file upload failed");
        }
      }

      await respond({
        response_type: "in_channel",
        text: `Results for: ${query}`,
        blocks,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      logger.error({ err }, "Drive search failed");
      await respond({ text: `Search failed: ${message}`, response_type: "ephemeral" });
    }
  });

  app.event("app_mention", async ({ event, say }) => {
    const text = (event.text ?? "").replace(/<@[^>]+>/g, "").trim();
    if (!text) {
      await say("Hi! Use /finddoc <search terms> to search Google Drive.");
      return;
    }

    try {
      const results = await searchDriveFiles(drive, text, 5);
      if (results.length === 0) {
        await say(`No results for “${text}”.`);
        return;
      }

      const lines = results.map((f) => `• <${f.webViewLink}|${f.name}> (${f.mimeType})`).join("\n");
      await say(`Here are some matches:\n${lines}`);
    } catch (err: unknown) {
      logger.error({ err }, "Mention search failed");
      await say("Sorry, I couldn't complete that search.");
    }
  });

  return app;
}

