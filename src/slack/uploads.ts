import { WebClient } from "@slack/web-api";
import { config } from "../config";
import { logger } from "../logger";

export async function maybeUploadSmallFile(args: {
  client: WebClient;
  channel: string;
  filename: string;
  content: Buffer;
  initialComment?: string;
}): Promise<void> {
  if (!config.upload.enable) return;
  if (args.content.byteLength > config.upload.maxBytes) return;
  try {
    await args.client.files.upload({
      channels: args.channel,
      filename: args.filename,
      file: args.content,
      initial_comment: args.initialComment,
    });
  } catch (err) {
    logger.warn({ err }, "Slack file upload failed");
  }
}

