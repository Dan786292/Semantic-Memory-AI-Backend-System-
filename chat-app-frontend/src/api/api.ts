import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
});

export const registerUser = async (email: string) => {
  console.log("➡️ Frontend sending register:", email);
  const res = await api.post("/auth/register", { email });
  return res.data;
};

export const loginUser = async (email: string, code: string) => {
  const res = await api.post("/auth/login", { email, code });
  return res.data;
};

export const sendMessage = async (token: string, message: string) => {
  const res = await api.post(
    "/chat/message",
    { message },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
};

export const getChatHistory = async (token: string) => {
  const res = await api.get("/chat/history", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export default api;
