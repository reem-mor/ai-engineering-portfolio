import { apiUpload } from "./client";
import type { UploadResponse } from "../types/document";

export function uploadDocument(file: File): Promise<UploadResponse> {
  return apiUpload<UploadResponse>("/upload", file);
}
