import { apiRequest } from "./client";
import type { ChatRequest, ChatResponse } from "../types/chat";

export function askChat(request: ChatRequest): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/chat", { method: "POST", body: request });
}
