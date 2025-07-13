import { useState } from "react";
import { useRouter } from "next/router";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);
      
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { 
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: params.toString(),
      });
      
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        router.push("/");
      } else {
        const errorData = await res.json();
        setError(errorData.detail || "Invalid credentials");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Network error. Make sure the backend is running on http://localhost:8000");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "100px auto", padding: 32, border: "1px solid #ccc", borderRadius: 8 }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 16 }}>
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
            style={{ width: "100%", padding: 8 }}
            disabled={loading}
          />
        </div>
        <div style={{ marginBottom: 16 }}>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: 8 }}
            disabled={loading}
          />
        </div>
        {error && <div style={{ color: "red", marginBottom: 16 }}>{error}</div>}
        <button 
          type="submit" 
          style={{ width: "100%", padding: 10 }}
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}