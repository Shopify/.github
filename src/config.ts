import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envSchema = z.object({
  SLACK_BOT_TOKEN: z.string().min(1, "SLACK_BOT_TOKEN is required"),
  SLACK_APP_TOKEN: z.string().min(1, "SLACK_APP_TOKEN is required"),
  SLACK_SIGNING_SECRET: z.string().min(1, "SLACK_SIGNING_SECRET is required"),
  GOOGLE_CREDENTIALS_JSON: z.string().optional(),
  GOOGLE_CREDENTIALS_FILE: z.string().optional(),
  GOOGLE_IMPERSONATED_USER: z.string().email().min(1, "GOOGLE_IMPERSONATED_USER is required for domain-wide delegation"),
  ENABLE_SMALL_FILE_UPLOAD: z.string().optional(),
  MAX_UPLOAD_BYTES: z.string().optional(),
  PORT: z.string().optional(),
});

const parsed = envSchema.safeParse(process.env);
if (!parsed.success) {
  const issues = parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
  throw new Error(`Invalid environment variables: ${issues}`);
}

export const config = {
  slack: {
    botToken: parsed.data.SLACK_BOT_TOKEN,
    appToken: parsed.data.SLACK_APP_TOKEN,
    signingSecret: parsed.data.SLACK_SIGNING_SECRET,
  },
  google: {
    credentialsJson: parsed.data.GOOGLE_CREDENTIALS_JSON,
    credentialsFile: parsed.data.GOOGLE_CREDENTIALS_FILE,
    impersonatedUser: parsed.data.GOOGLE_IMPERSONATED_USER,
  },
  upload: {
    enable: (parsed.data.ENABLE_SMALL_FILE_UPLOAD ?? "false").toLowerCase() === "true",
    maxBytes: Number(parsed.data.MAX_UPLOAD_BYTES ?? 800000),
  },
  port: Number(parsed.data.PORT ?? 3000),
};

