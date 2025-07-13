import React, { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);
  return (
    <main style={{ padding: 32 }}>
      <h1>OpenHealth-Inspired AI Health Assistant</h1>
      <p>Welcome! Upload your health data and chat with our AI assistant.</p>
      {/* Add upload and chat components here */}
    </main>
  );
}
