import { useState, useEffect } from "react";
import { sendMessage, getChatHistory } from "../api/api";
import type { ChatMessage } from "../types";

interface Props {
  token: string;
}

export default function Chat({ token }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      const history = await getChatHistory(token);
      setMessages(history);
    };
    fetchHistory();
  }, [token]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const newMsg = await sendMessage(token, input);
    setMessages((prev) => [...prev, newMsg]);
    setInput("");
  };

  return (
    <div>
      <h2>Chat</h2>
      <div style={{ maxHeight: "400px", overflowY: "scroll", border: "1px solid #ccc", padding: "10px" }}>
        {messages.map((m) => (
          <div key={m.id}>
            <b>User:</b> {m.message} <br />
            <b>AI:</b> {m.response}
            <hr />
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type a message..."
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
