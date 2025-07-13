import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/router";
import styles from "./MedicalChat.module.css";

interface ChatMessage {
  sender: "user" | "ai";
  text: string;
  fileName?: string;
}

export default function MedicalChat() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input && !file) return;
    setLoading(true);
    setMessages((prev) => [
      ...prev,
      { sender: "user", text: input, fileName: file?.name },
    ]);
    try {
      const form = new FormData();
      form.append("question", input);
      if (file) form.append("file", file);
      const res = await fetch("http://localhost:8000/chat/ask", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: form,
      });
      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          { sender: "ai", text: data.result },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: "ai", text: "Error: Unable to get response from AI." },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Network error." },
      ]);
    } finally {
      setInput("");
      setFile(null);
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className={styles.container}>
      {/* Left panel: Chat history */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <h2 className={styles.sidebarTitle}>🩺 MedAI Chat</h2>
        </div>
        <div className={styles.sidebarHistory}>
          <h4 className={styles.sidebarHistoryTitle}>History</h4>
          <ul className={styles.sidebarHistoryList}>
            {messages
              .filter((m) => m.sender === "user")
              .map((msg, idx) => (
                <li key={idx} className={styles.sidebarHistoryItem}>
                  <div className={styles.sidebarHistoryUser}>You</div>
                  <div className={styles.sidebarHistoryText}>{msg.text}</div>
                  {msg.fileName && (
                    <div className={styles.sidebarHistoryFile}>
                      📎 {msg.fileName}
                    </div>
                  )}
                </li>
              ))}
          </ul>
        </div>
      </aside>
      {/* Main chat panel */}
      <main className={styles.main}>
        <div className={styles.chatArea}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={
                styles.chatMessageRow +
                " " +
                (msg.sender === "user"
                  ? styles.chatMessageRowUser
                  : styles.chatMessageRowAI)
              }
            >
              <div
                className={
                  styles.chatBubble +
                  " " +
                  (msg.sender === "user" ? styles.chatBubbleUser : "")
                }
              >
                {msg.text}
                {msg.fileName && (
                  <div className={styles.chatFile}>📎 {msg.fileName}</div>
                )}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className={styles.inputBar}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
            className={styles.inputText}
            disabled={loading}
            autoFocus
          />
          <input
            type="file"
            accept=".pdf,image/*"
            ref={fileInputRef}
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className={styles.inputFile}
            disabled={loading}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className={styles.attachButton}
            disabled={loading}
            title="Attach file"
          >
            📎
          </button>
          <button
            type="submit"
            disabled={loading || (!input && !file)}
            className={styles.sendButton}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </form>
      </main>
    </div>
  );
}
