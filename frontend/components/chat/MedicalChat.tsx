import React, { useEffect, useState } from "react";
import ChatHistoryPanel from "./ChatHistoryPanel";
import ChatMainPanel from "./ChatMainPanel";
import { v4 as uuidv4 } from "uuid";
import styles from "./MedicalChat.module.css";

interface ChatMessage {
  sender: "user" | "ai";
  text: string;
  fileName?: string;
  filePath?: string;
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

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch("http://localhost:8000/chat/sessions", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(async (sessions: { id: string; title: string; created_at: string }[]) => {
        if (sessions.length === 0) {
          const response = await fetch("http://localhost:8000/chat/sessions", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ title: "New Chat" }),
          });
          const result = await response.json();
          const newSession = {
            id: result.session_id,
            title: "New Chat",
            created_at: new Date().toISOString(),
            messages: [],
          };
          setChats([newSession]);
          setActiveChatId(newSession.id);
        } else {
          const sessionsWithMessages = await Promise.all(
            sessions.map(async (session) => {
              const response = await fetch(`http://localhost:8000/chat/sessions/${session.id}`, {
                headers: { Authorization: `Bearer ${token}` },
              });
              const sessionData = await response.json();
              return {
                ...session,
                messages: sessionData.messages || [],
              };
            })
          );
          setChats(sessionsWithMessages);
          setActiveChatId(sessionsWithMessages[0].id);
        }
      })
      .catch((error) => {
        console.error("Failed to load sessions:", error);
      });
  }, []);

  const handleSelectChat = (id: string) => {
    setActiveChatId(id);
  };

  const handleNewChat = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:8000/chat/sessions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: "New Chat" }),
      });
      const result = await response.json();
      const newSession = {
        id: result.session_id,
        title: "New Chat",
        created_at: new Date().toISOString(),
        messages: [],
      };
      setChats((prev) => [...prev, newSession]);
      setActiveChatId(newSession.id);
    } catch (error) {
      console.error("Failed to create new session:", error);
    }
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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);

      const res = await fetch("http://localhost:8000/chat/ask", {
        method: "POST",
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        body: form,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      let aiMsg: ChatMessage;
      if (res.ok) {
        const data = await res.json();
        aiMsg = {
          sender: "ai",
          text: data.result,
          timestamp: new Date().toISOString(),
        };
        // Update user message with file path from response
        if (data.filePath) {
          userMsg.filePath = data.filePath;
        }
      } else {
        const errorText = await res.text();
        console.error("Backend error:", res.status, errorText);
        aiMsg = {
          sender: "ai",
          text: `Error: Unable to get response from AI. Status: ${res.status}`,
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
      const token = localStorage.getItem("token");
      await fetch(`http://localhost:8000/chat/sessions/${activeChatId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(userMsg),
      });
      await fetch(`http://localhost:8000/chat/sessions/${activeChatId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(aiMsg),
      });

      const activeChat = chats.find(chat => chat.id === activeChatId);
      if (activeChat && activeChat.messages.length === 0) {
        const updatedTitle = userMsg.text.slice(0, 20) + (userMsg.text.length > 20 ? "..." : "");
        setChats(prev => prev.map(chat =>
          chat.id === activeChatId
            ? { ...chat, title: updatedTitle }
            : chat
        ));
      }
    } catch (err: any) {
      console.error("Network error:", err);
      let errorMessage = "Network error.";
      if (err.name === 'AbortError') {
        errorMessage = "Request timed out. The AI model is taking too long to respond. Please try again.";
      } else if (err.message) {
        errorMessage = `Network error: ${err.message}`;
      }

      setChats((prev) =>
        prev.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                messages: [
                  ...chat.messages,
                  { sender: "ai", text: errorMessage, timestamp: new Date().toISOString() },
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
        LogoutButton={LogoutButton}
      />
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
  );
}
