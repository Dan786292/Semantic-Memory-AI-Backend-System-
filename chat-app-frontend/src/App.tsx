import { useState } from "react";
import Register from "./components/Register";
import Login from "./components/Login";
import Chat from "./components/Chat";

function App() {
  const [token, setToken] = useState<string | null>(null);

  if (!token) {
    return (
      <div>
        <Register />
        <Login onLogin={setToken} />
      </div>
    );
  }

  return <Chat token={token} />;
}

export default App;
