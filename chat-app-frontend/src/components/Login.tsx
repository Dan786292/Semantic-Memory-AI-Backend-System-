import { useState } from "react";
import { loginUser } from "../api/api";

interface Props {
  onLogin: (token: string) => void;
}

export default function Login({ onLogin }: Props) {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");

  const handleLogin = async () => {
    try {
      const data = await loginUser(email, code);
      onLogin(data.access_token);
    } catch (err) {
      alert("Login failed");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="text"
        placeholder="Code"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}
