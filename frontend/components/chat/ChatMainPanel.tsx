import React, { useRef, useEffect } from "react";
import styles from "./MedicalChat.module.css";
import MarkdownRenderer from "./MarkdownRenderer";

interface ChatMessage {
  sender: "user" | "ai";
  text: string;
  fileName?: string;
  filePath?: string;
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
    <main className={styles.main}>
      <div className={styles.chatArea}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={
              msg.sender === "user"
                ? `${styles.chatMessageRow} ${styles.chatMessageRowUser}`
                : `${styles.chatMessageRow} ${styles.chatMessageRowAI}`
            }
          >
            <div
              className={
                msg.sender === "user"
                  ? `${styles.chatBubble} ${styles.chatBubbleUser}`
                  : styles.chatBubble
              }
            >
              {msg.sender === "ai" ? (
                <MarkdownRenderer content={msg.text} isAI={true} />
              ) : (
                <MarkdownRenderer content={msg.text} isAI={false} />
              )}
              {msg.fileName && (
                <div className={styles.chatFile}>
                  📎 {msg.fileName}
                  {msg.filePath && (
                    <div className={styles.filePreview}>
                      {msg.fileName.toLowerCase().match(/\.(jpg|jpeg|png|gif|webp)$/) ? (
                        <img
                          src={`http://localhost:8000/${msg.filePath}`}
                          alt={msg.fileName}
                          className={styles.imagePreview}
                          loading="lazy"
                        />
                      ) : (
                        <div className={styles.fileIcon}>📄</div>
                      )}
                    </div>
                  )}
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
        className={styles.inputBar}
      >
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your question..."
          className={styles.inputText}
          disabled={loading}
          autoFocus
        />
        <input
          type="file"
          accept=".pdf,image/*"
          ref={fileInputRef}
          onChange={e => setFile(e.target.files?.[0] || null)}
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
  );
}
