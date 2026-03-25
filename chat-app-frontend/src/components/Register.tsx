import { useState } from "react";
import { registerUser } from "../api/api";

export default function Register() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");

  const handleRegister = async () => {
    const data = await registerUser(email);
    alert(`Your code (demo): ${data.code}`);
    setCode(data.code);
  };

  return (
    <div>
      <h2>Register</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button onClick={handleRegister}>Register</button>
      {code && <p>Your code: {code}</p>}
    </div>
  );
}
