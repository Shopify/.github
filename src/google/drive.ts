import { google, drive_v3 } from "googleapis";
import { GoogleAuth, JWT } from "google-auth-library";
import fs from "fs";
import { config } from "../config";
import { logger } from "../logger";

function loadServiceAccount(): { clientEmail: string; privateKey: string } {
  let jsonText: string | undefined = config.google.credentialsJson;
  if (!jsonText && config.google.credentialsFile) {
    jsonText = fs.readFileSync(config.google.credentialsFile, "utf8");
  }
  if (!jsonText) {
    throw new Error("Google credentials not provided. Set GOOGLE_CREDENTIALS_JSON or GOOGLE_CREDENTIALS_FILE");
  }
  const parsed = JSON.parse(jsonText);
  const clientEmail = parsed.client_email as string;
  // Private key may come with escaped newlines; normalize
  const privateKey = String(parsed.private_key).replace(/\\n/g, "\n");
  if (!clientEmail || !privateKey) {
    throw new Error("client_email or private_key missing in Google credentials JSON");
  }
  return { clientEmail, privateKey };
}

export function createDriveClient(): drive_v3.Drive {
  const { clientEmail, privateKey } = loadServiceAccount();
  const scopes = [
    "https://www.googleapis.com/auth/drive.readonly",
  ];

  const auth = new JWT({
    email: clientEmail,
    key: privateKey,
    scopes,
    subject: config.google.impersonatedUser,
  });

  const drive = google.drive({ version: "v3", auth });
  return drive;
}

export type DriveSearchResult = {
  id: string;
  name: string;
  mimeType: string;
  webViewLink?: string | null;
  iconLink?: string | null;
  size?: string | null;
  owners?: { displayName?: string | null; emailAddress?: string | null }[] | null;
  modifiedTime?: string | null;
};

export async function searchDriveFiles(drive: drive_v3.Drive, query: string, limit: number = 10): Promise<DriveSearchResult[]> {
  // Simple full-text search with corpora across user drives and shared
  const res = await drive.files.list({
    q: `name contains '${query.replace(/'/g, "\\'")}' and trashed = false`,
    pageSize: Math.min(limit, 50),
    fields: "files(id,name,mimeType,webViewLink,iconLink,size,owners(displayName,emailAddress),modifiedTime)",
    includeItemsFromAllDrives: true,
    supportsAllDrives: true,
    corpora: "allDrives",
  });
  return (res.data.files ?? []) as DriveSearchResult[];
}

export async function getFileMetadata(drive: drive_v3.Drive, fileId: string): Promise<DriveSearchResult | undefined> {
  const res = await drive.files.get({
    fileId,
    fields: "id,name,mimeType,webViewLink,iconLink,size,owners(displayName,emailAddress),modifiedTime",
    supportsAllDrives: true,
  });
  return res.data as DriveSearchResult;
}

export async function downloadSmallFile(drive: drive_v3.Drive, fileId: string): Promise<Buffer> {
  const res = await drive.files.get({ fileId, alt: "media" }, { responseType: "arraybuffer" });
  return Buffer.from(res.data as ArrayBuffer);
}

