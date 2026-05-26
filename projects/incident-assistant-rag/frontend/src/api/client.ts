import { API_BASE_URL } from "../config/env";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type RequestOptions = { method?: string; body?: unknown; headers?: Record<string, string> };

function parseApiErrorDetail(errorData: unknown): string {
  if (typeof errorData === "object" && errorData !== null && "detail" in errorData) {
    const detail = (errorData as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
      return detail
        .map((item) =>
          typeof item === "object" && item !== null && "msg" in item ? String((item as { msg: unknown }).msg) : JSON.stringify(item),
        )
        .join(", ");
    return JSON.stringify(detail);
  }
  return "Unexpected API error.";
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (!response.ok) {
    let message = "Unexpected API error.";
    try {
      message = parseApiErrorDetail(await response.json());
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}

export async function apiUpload<T>(path: string, file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}${path}`, { method: "POST", body: formData });
  if (!response.ok) {
    let message = "Unexpected upload error.";
    try {
      message = parseApiErrorDetail(await response.json());
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}
