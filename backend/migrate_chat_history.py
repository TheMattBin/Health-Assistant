#!/usr/bin/env python3
"""
Migration script to convert flat chat history to session-based format
Run this from the backend directory
"""

import json
import os
from datetime import datetime

CHAT_HISTORY_DIR = "chat_history_db"

def migrate_chat_history():
    demo_user_file = os.path.join(CHAT_HISTORY_DIR, "demo_user.json")

    if not os.path.exists(demo_user_file):
        print("No existing chat history found")
        return

    # Load existing flat messages
    with open(demo_user_file, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    if not messages:
        print("Chat history is empty")
        return

    # Check if data is already in session format
    if messages and isinstance(messages, list) and len(messages) > 0 and isinstance(messages[0], dict) and "id" in messages[0] and "messages" in messages[0]:
        print("Chat history is already in session format")
        return

    print(f"Migrating {len(messages)} messages to session format...")

    # Group messages into sessions (simple heuristic: create a new session every 10 messages or when there's a big gap)
    sessions = []
    current_session = None
    session_counter = 1

    for i, message in enumerate(messages):
        # Create new session every 10 messages or for the first message
        if i == 0 or i % 10 == 0:
            if current_session:
                sessions.append(current_session)

            title = message.get("text", "New Chat")[:30]
            if len(message.get("text", "")) > 30:
                title += "..."

            current_session = {
                "id": f"migrated_session_{session_counter}",
                "title": title or f"Chat {session_counter}",
                "created_at": message.get("timestamp", datetime.utcnow().isoformat()),
                "messages": []
            }
            session_counter += 1

        if current_session:
            current_session["messages"].append(message)

    # Add the last session
    if current_session:
        sessions.append(current_session)

    # Backup old data
    backup_file = demo_user_file + ".backup"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    # Save new session-based data
    with open(demo_user_file, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

    print(f"Migration complete! Created {len(sessions)} sessions")
    print(f"Original data backed up to: {backup_file}")

if __name__ == "__main__":
    migrate_chat_history()