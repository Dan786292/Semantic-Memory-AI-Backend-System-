export interface Token {
  access_token: string;
  token_type: string;
}

export interface ChatMessage {
  id: number;
  message: string;
  response: string | null;
  created_at: string;
}
