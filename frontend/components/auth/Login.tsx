import { useState, useEffect } from "react";
import { useRouter } from "next/router";

export default function Login() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Handle OAuth2 callback
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      localStorage.setItem('token', token);
      // Remove token from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      router.push('/');
    }
  }, [router]);

  const handleGoogleLogin = () => {
    setError("");
    setLoading(true);
    // Redirect to Google OAuth2 login
    window.location.href = "http://localhost:8000/auth/oauth2/login/google";
  };

  const handleFacebookLogin = () => {
    setError("");
    setLoading(true);
    // Redirect to Facebook OAuth2 login
    window.location.href = "http://localhost:8000/auth/oauth2/login/facebook";
  };

  return (
    <div style={{ maxWidth: 400, margin: "100px auto", padding: 32, border: "1px solid #ccc", borderRadius: 8 }}>
      <h2>Login to Health Assistant</h2>

      <div style={{ marginBottom: 16, textAlign: "center", color: "#666" }}>
        <p>Sign in with your account to access the AI health assistant.</p>
      </div>

      {/* Google OAuth2 Login */}
      <button
        type="button"
        onClick={handleGoogleLogin}
        style={{
          width: "100%",
          padding: 16,
          backgroundColor: "#4285f4",
          color: "white",
          border: "none",
          borderRadius: 8,
          cursor: "pointer",
          fontSize: 18,
          fontWeight: "600",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 12,
          transition: "background-color 0.2s",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          marginBottom: 12
        }}
        disabled={loading}
        onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#357ae8"}
        onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#4285f4"}
      >
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        Sign in with Google
      </button>

      {/* Facebook OAuth2 Login */}
      <button
        type="button"
        onClick={handleFacebookLogin}
        style={{
          width: "100%",
          padding: 16,
          backgroundColor: "#1877f2",
          color: "white",
          border: "none",
          borderRadius: 8,
          cursor: "pointer",
          fontSize: 18,
          fontWeight: "600",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 12,
          transition: "background-color 0.2s",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          marginBottom: 12
        }}
        disabled={loading}
        onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#166fe5"}
        onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#1877f2"}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
        Sign in with Facebook
      </button>

      {error && <div style={{ color: "red", marginTop: 16, textAlign: "center" }}>{error}</div>}

      <div style={{ marginTop: 24, textAlign: "center", color: "#888", fontSize: "14px" }}>
        <p>Your Google account information is used only for authentication.</p>
      </div>
    </div>
  );
}
