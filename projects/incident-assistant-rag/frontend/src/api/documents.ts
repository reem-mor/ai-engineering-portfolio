import { apiRequest } from "./client";
import type { DocumentIndexResponse, DocumentListResponse } from "../types/document";

export function listSampleDocuments(): Promise<DocumentListResponse> {
  return apiRequest<DocumentListResponse>("/documents/samples");
}

export function listUploadedDocuments(): Promise<DocumentListResponse> {
  return apiRequest<DocumentListResponse>("/documents/uploaded");
}

export function indexSampleDocuments(): Promise<DocumentIndexResponse> {
  return apiRequest<DocumentIndexResponse>("/documents/index-samples", { method: "POST" });
}

export function indexUploadedDocuments(): Promise<DocumentIndexResponse> {
  return apiRequest<DocumentIndexResponse>("/documents/index-uploaded", { method: "POST" });
}
