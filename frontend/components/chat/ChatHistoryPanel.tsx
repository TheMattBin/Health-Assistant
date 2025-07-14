import React from "react";

interface ChatHistoryPanelProps {
  chats: { id: string; title: string; created_at: string }[];
  activeChatId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
}

export default function ChatHistoryPanel({ chats, activeChatId, onSelect, onNewChat }: ChatHistoryPanelProps) {
  return (
    <aside style={{ width: 260, background: "#23272f", color: "#fff", borderRight: "1px solid #222", display: "flex", flexDirection: "column", padding: 0 }}>
      <div style={{ padding: 24, borderBottom: "1px solid #333", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700, letterSpacing: 1 }}>🩺 MedAI Chat</h2>
        <button onClick={onNewChat} title="New Chat" style={{ background: "#e0f7fa", border: "none", borderRadius: "50%", width: 32, height: 32, fontSize: 20, cursor: "pointer", marginLeft: 8 }}>+</button>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
        <h4 style={{ color: "#b0b3b8", fontWeight: 500, margin: "0 0 12px 0" }}>History</h4>
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {chats.map(chat => (
            <li key={chat.id} style={{ marginBottom: 18 }}>
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
    </aside>
  );
}
