import axios from 'axios';
import type { FormState } from '../store/formSlice';

const API_BASE = 'http://localhost:8000';

export interface ChatApiResponse {
  reply: string;
  form_updates: Partial<FormState>;
  action: string | null;
}

export async function sendChatMessage(
  message: string,
  formState: FormState,
  chatHistory: Array<{ role: string; content: string }>
): Promise<ChatApiResponse> {
  const response = await axios.post<ChatApiResponse>(`${API_BASE}/api/chat`, {
    message,
    form_state: formState,
    chat_history: chatHistory,
  });
  return response.data;
}
