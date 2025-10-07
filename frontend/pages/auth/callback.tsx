import { useEffect } from "react";
import { useRouter } from "next/router";
import Login from "../../components/auth/Login";

export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      localStorage.setItem('token', token);
      window.history.replaceState({}, document.title, window.location.pathname);
      router.push('/');
    } else {
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