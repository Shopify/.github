import { createSlackApp } from "./slack/app";
import { config } from "./config";
import { logger } from "./logger";

async function main() {
  const app = createSlackApp();
  await app.start({ port: config.port });
  logger.info(`⚡️ Slack app is running on port ${config.port}`);
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});

