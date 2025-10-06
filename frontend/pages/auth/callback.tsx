import { useEffect } from "react";
import { useRouter } from "next/router";
import Login from "../../components/auth/Login";

export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    // Handle OAuth2 callback
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      localStorage.setItem('token', token);
      // Remove token from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      // Redirect to chat page after successful login
      router.push('/');
    } else {
      // If no token, redirect to login page after a short delay
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    }
  }, [router]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      flexDirection: 'column'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h2>Processing authentication...</h2>
        <p>You will be redirected shortly.</p>
      </div>
    </div>
  );
}