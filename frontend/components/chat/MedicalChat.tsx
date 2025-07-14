import React, { useEffect, useState } from "react";
import ChatHistoryPanel from "./ChatHistoryPanel";
import ChatMainPanel from "./ChatMainPanel";
import { v4 as uuidv4 } from "uuid";
import styles from "./MedicalChat.module.css";

interface ChatMessage {
  sender: "user" | "ai";
  text: string;
  fileName?: string;
  timestamp?: string;
}

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  messages: ChatMessage[];
}

interface MedicalChatProps {
  LogoutButton?: React.ComponentType;
}

export default function MedicalChat({ LogoutButton }: MedicalChatProps) {
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch chat history on mount
  useEffect(() => {
    fetch("http://localhost:8000/chat/history")
      .then((res) => res.json())
      .then((data: ChatMessage[]) => {
        // Group messages into sessions (for demo, one session)
        const sessionId = uuidv4();
        setChats([
          {
            id: sessionId,
            title: data[0]?.text?.slice(0, 20) || "New Chat",
            created_at: data[0]?.timestamp || new Date().toISOString(),
            messages: data,
          },
        ]);
        setActiveChatId(sessionId);
      });
  }, []);

  const handleSelectChat = (id: string) => {
    setActiveChatId(id);
  };

  const handleNewChat = () => {
    const newId = uuidv4();
    setChats((prev) => [
      ...prev,
      {
        id: newId,
        title: "New Chat",
        created_at: new Date().toISOString(),
        messages: [],
      },
    ]);
    setActiveChatId(newId);
  };

  const handleSend = async () => {
    if ((!input && !file) || !activeChatId) return;
    setLoading(true);
    const userMsg: ChatMessage = {
      sender: "user",
      text: input,
      fileName: file?.name,
      timestamp: new Date().toISOString(),
    };
    setChats((prev) =>
      prev.map((chat) =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, userMsg] }
          : chat
      )
    );
    try {
      const form = new FormData();
      form.append("question", input);
      if (file) form.append("file", file);
      const res = await fetch("http://localhost:8000/chat/ask", {
        method: "POST",
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        body: form,
      });
      let aiMsg: ChatMessage;
      if (res.ok) {
        const data = await res.json();
        aiMsg = {
          sender: "ai",
          text: data.result,
          timestamp: new Date().toISOString(),
        };
      } else {
        aiMsg = {
          sender: "ai",
          text: "Error: Unable to get response from AI.",
          timestamp: new Date().toISOString(),
        };
      }
      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? { ...chat, messages: [...chat.messages, aiMsg] }
            : chat
        )
      );
      // Save both messages to backend
      await fetch("http://localhost:8000/chat/history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userMsg),
      });
      await fetch("http://localhost:8000/chat/history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(aiMsg),
      });
    } catch (err) {
      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                messages: [
                  ...chat.messages,
                  { sender: "ai", text: "Network error.", timestamp: new Date().toISOString() },
                ],
              }
            : chat
        )
      );
    } finally {
      setInput("");
      setFile(null);
      setLoading(false);
    }
  };

  const activeChat = chats.find((chat) => chat.id === activeChatId);

  return (
    <div className={styles.container}>
      <ChatHistoryPanel
        chats={chats.map(({ id, title, created_at }) => ({ id, title, created_at }))}
        activeChatId={activeChatId}
        onSelect={handleSelectChat}
        onNewChat={handleNewChat}
      />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", position: "relative" }}>
        {LogoutButton && (
          <div style={{ position: "absolute", top: 18, right: 24, zIndex: 10 }}>
            <LogoutButton />
          </div>
        )}
        <ChatMainPanel
          messages={activeChat?.messages || []}
          input={input}
          setInput={setInput}
          file={file}
          setFile={setFile}
          loading={loading}
          onSend={handleSend}
        />
      </div>
    </div>
  );
}
