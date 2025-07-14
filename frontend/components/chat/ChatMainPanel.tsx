import React, { useRef, useEffect } from "react";

interface ChatMessage {
  sender: "user" | "ai";
  text: string;
  fileName?: string;
  timestamp?: string;
}

interface ChatMainPanelProps {
  messages: ChatMessage[];
  input: string;
  setInput: (v: string) => void;
  file: File | null;
  setFile: (f: File | null) => void;
  loading: boolean;
  onSend: () => void;
}

export default function ChatMainPanel({ messages, input, setInput, file, setFile, loading, onSend }: ChatMainPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <main style={{ flex: 1, display: "flex", flexDirection: "column", background: "#fff" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: "32px 0 16px 0", display: "flex", flexDirection: "column", gap: 0 }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
              marginBottom: 10,
            }}
          >
            <div
              style={{
                background: msg.sender === "user" ? "#e0f7fa" : "#f1f8e9",
                color: "#222",
                padding: "14px 18px",
                borderRadius: 18,
                maxWidth: "60%",
                fontSize: 16,
                boxShadow: msg.sender === "user" ? "0 2px 8px #b2ebf2" : "0 2px 8px #c8e6c9",
                borderBottomRightRadius: msg.sender === "user" ? 4 : 18,
                borderBottomLeftRadius: msg.sender === "user" ? 18 : 4,
                wordBreak: "break-word",
              }}
            >
              {msg.text}
              {msg.fileName && (
                <div style={{ fontSize: 12, color: "#888", marginTop: 6 }}>
                  📎 {msg.fileName}
                </div>
              )}
              {msg.timestamp && (
                <div style={{ fontSize: 10, color: "#bbb", marginTop: 4, textAlign: "right" }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <form
        onSubmit={e => {
          e.preventDefault();
          onSend();
        }}
        style={{ display: "flex", alignItems: "center", gap: 10, padding: "18px 24px", borderTop: "1px solid #eee", background: "#fafbfc" }}
      >
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your question..."
          style={{ flex: 1, padding: "14px 16px", borderRadius: 18, border: "1px solid #ccc", fontSize: 16, outline: "none", background: "#fff" }}
          disabled={loading}
          autoFocus
        />
        <input
          type="file"
          accept=".pdf,image/*"
          ref={fileInputRef}
          onChange={e => setFile(e.target.files?.[0] || null)}
          style={{ display: "none" }}
          disabled={loading}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          style={{ background: "#e0f7fa", border: "none", borderRadius: "50%", width: 40, height: 40, display: "flex", alignItems: "center", justifyContent: "center", cursor: loading ? "not-allowed" : "pointer", fontSize: 22, marginRight: 4 }}
          disabled={loading}
          title="Attach file"
        >
          📎
        </button>
        <button
          type="submit"
          disabled={loading || (!input && !file)}
          style={{ background: "#1976d2", color: "#fff", border: "none", borderRadius: 18, padding: "12px 28px", fontSize: 16, fontWeight: 600, cursor: loading ? "not-allowed" : "pointer", boxShadow: "0 2px 8px #90caf9", transition: "background 0.2s" }}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </form>
    </main>
  );
}
