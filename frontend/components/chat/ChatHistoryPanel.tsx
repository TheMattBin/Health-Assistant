
import React from "react";
import styles from "./MedicalChat.module.css";

interface ChatHistoryPanelProps {
  chats: { id: string; title: string; created_at: string }[];
  activeChatId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  LogoutButton?: React.ComponentType;
}

export default function ChatHistoryPanel({ chats, activeChatId, onSelect, onNewChat, LogoutButton }: ChatHistoryPanelProps) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.sidebarHeader} style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h2 className={styles.sidebarTitle}>🩺 MedAI Chat</h2>
        <button onClick={onNewChat} title="New Chat" style={{ background: "#e0f7fa", border: "none", borderRadius: "50%", width: 32, height: 32, fontSize: 20, cursor: "pointer", marginLeft: 8 }}>+</button>
      </div>
      <div className={styles.sidebarHistory}>
        <h4 className={styles.sidebarHistoryTitle}>History</h4>
        <ul className={styles.sidebarHistoryList}>
          {chats.map(chat => (
            <li key={chat.id} className={styles.sidebarHistoryItem}>
              <button
                onClick={() => onSelect(chat.id)}
                style={{
                  background: chat.id === activeChatId ? "#1976d2" : "#23272f",
                  color: chat.id === activeChatId ? "#fff" : "#e0f7fa",
                  border: "none",
                  borderRadius: 8,
                  width: "100%",
                  textAlign: "left",
                  padding: "10px 12px",
                  fontWeight: 600,
                  cursor: "pointer",
                  fontSize: 15,
                  transition: "background 0.2s",
                }}
              >
                {chat.title || `Chat ${chat.id.slice(-4)}`}
                <div style={{ fontSize: 11, color: "#b0b3b8", marginTop: 2 }}>{new Date(chat.created_at).toLocaleString()}</div>
              </button>
            </li>
          ))}
        </ul>
      </div>
      {LogoutButton && (
        <div className={styles.sidebarFooter}>
          <LogoutButton />
        </div>
      )}
    </aside>
  );
}
