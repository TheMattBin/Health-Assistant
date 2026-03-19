"""
Database models for both PostgreSQL and MongoDB
Unified interface for database operations
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

# Database type based on environment
DB_TYPE = os.getenv('DB_TYPE', 'json').lower()

if DB_TYPE == 'postgresql':
    import psycopg2
    from psycopg2.extras import RealDictCursor
elif DB_TYPE == 'mongodb':
    from pymongo import MongoClient
    from pymongo.collection import Collection
else:
    # JSON fallback
    import json
    from pathlib import Path

class BaseModel(ABC):
    """Abstract base class for database models"""

    @abstractmethod
    def save(self) -> bool:
        pass

    @abstractmethod
    def delete(self) -> bool:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

class User(BaseModel):
    """User model"""

    def __init__(self, email: str, user_id: Optional[str] = None):
        self.id = user_id or str(uuid.uuid4()) if DB_TYPE != 'mongodb' else None
        self.email = email
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self) -> bool:
        if DB_TYPE == 'postgresql':
            return PostgreSQLUserRepository().save(self)
        elif DB_TYPE == 'mongodb':
            return MongoDBUserRepository().save(self)
        else:
            return JSONUserRepository().save(self)

    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        if DB_TYPE == 'postgresql':
            return PostgreSQLUserRepository().find_by_email(email)
        elif DB_TYPE == 'mongodb':
            return MongoDBUserRepository().find_by_email(email)
        else:
            return JSONUserRepository().find_by_email(email)

class ChatSession(BaseModel):
    """Chat session model"""

    def __init__(self, user_id: str, title: str, session_id: Optional[str] = None):
        self.id = str(uuid.uuid4()) if DB_TYPE != 'mongodb' else None
        self.user_id = user_id
        self.title = title
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.messages: List[Message] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'session_id': self.session_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'messages': [msg.to_dict() for msg in self.messages]
        }

    def add_message(self, message: 'Message'):
        self.messages.append(message)
        self.updated_at = datetime.now()

    def save(self) -> bool:
        if DB_TYPE == 'postgresql':
            return PostgreSQLChatRepository().save_session(self)
        elif DB_TYPE == 'mongodb':
            return MongoDBChatRepository().save_session(self)
        else:
            return JSONChatRepository().save_session(self)

    @classmethod
    def find_by_user(cls, user_email: str) -> List['ChatSession']:
        if DB_TYPE == 'postgresql':
            return PostgreSQLChatRepository().find_by_user(user_email)
        elif DB_TYPE == 'mongodb':
            return MongoDBChatRepository().find_by_user(user_email)
        else:
            return JSONChatRepository().find_by_user(user_email)

    @classmethod
    def find_by_session_id(cls, session_id: str) -> Optional['ChatSession']:
        if DB_TYPE == 'postgresql':
            return PostgreSQLChatRepository().find_by_session_id(session_id)
        elif DB_TYPE == 'mongodb':
            return MongoDBChatRepository().find_by_session_id(session_id)
        else:
            return JSONChatRepository().find_by_session_id(session_id)

class Message(BaseModel):
    """Message model"""

    def __init__(self, session_id: str, sender: str, text: str,
                 file_name: Optional[str] = None, file_path: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        self.id = str(uuid.uuid4()) if DB_TYPE != 'mongodb' else None
        self.session_id = session_id
        self.sender = sender  # 'user' or 'ai'
        self.text = text
        self.file_name = file_name
        self.file_path = file_path
        self.timestamp = timestamp or datetime.now()
        self.message_order = 0  # Will be set when saved

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender': self.sender,
            'text': self.text,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'timestamp': self.timestamp,
            'message_order': self.message_order
        }

# Repository Classes

class JSONUserRepository:
    """JSON-based user repository (current implementation)"""

    def __init__(self):
        self.storage_dir = Path('chat_history_db')

    def save(self, user: User) -> bool:
        # In JSON implementation, users are implicit (filename = email)
        # Create empty file if it doesn't exist
        user_file = self.storage_dir / f"{user.email}.json"
        if not user_file.exists():
            user_file.write_text('[]')
        return True

    def find_by_email(self, email: str) -> Optional[User]:
        user_file = self.storage_dir / f"{email}.json"
        if user_file.exists():
            return User(email=email)
        return None

class JSONChatRepository:
    """JSON-based chat repository (current implementation)"""

    def __init__(self):
        self.storage_dir = Path('chat_history_db')

    def save_session(self, session: ChatSession) -> bool:
        user_email = self._get_user_email_from_session_id(session.user_id)
        if not user_email:
            return False

        user_file = self.storage_dir / f"{user_email}.json"

        # Load existing sessions
        sessions = []
        if user_file.exists():
            sessions = json.loads(user_file.read_text())

        # Find and update or create new session
        session_dict = session.to_dict()
        for i, existing_session in enumerate(sessions):
            if existing_session.get('id') == session.session_id:
                sessions[i] = session_dict
                break
        else:
            sessions.append(session_dict)

        user_file.write_text(json.dumps(sessions, indent=2, default=str))
        return True

    def find_by_user(self, user_email: str) -> List[ChatSession]:
        user_file = self.storage_dir / f"{user_email}.json"
        sessions = []

        if user_file.exists():
            sessions_data = json.loads(user_file.read_text())
            for session_data in sessions_data:
                session = ChatSession(
                    user_id=user_email,  # In JSON, user_id is email
                    title=session_data.get('title', 'New Chat'),
                    session_id=session_data.get('id')
                )
                session.created_at = datetime.fromisoformat(session_data.get('created_at', datetime.now().isoformat()))

                # Add messages
                for msg_data in session_data.get('messages', []):
                    message = Message(
                        session_id=session.session_id,
                        sender=msg_data.get('sender', 'user'),
                        text=msg_data.get('text', ''),
                        file_name=msg_data.get('fileName'),
                        file_path=msg_data.get('filePath'),
                        timestamp=datetime.fromisoformat(msg_data.get('timestamp', datetime.now().isoformat()))
                    )
                    session.messages.append(message)

                sessions.append(session)

        return sessions

    def find_by_session_id(self, session_id: str) -> Optional[ChatSession]:
        # This is inefficient for JSON - need to scan all files
        for user_file in self.storage_dir.glob('*.json'):
            sessions_data = json.loads(user_file.read_text())
            for session_data in sessions_data:
                if session_data.get('id') == session_id:
                    user_email = user_file.stem
                    session = ChatSession(
                        user_id=user_email,
                        title=session_data.get('title', 'New Chat'),
                        session_id=session_id
                    )
                    # Add messages...
                    return session
        return None

    def _get_user_email_from_session_id(self, session_id: str) -> Optional[str]:
        """Helper method to find user email for session_id"""
        # This is inefficient - would need to scan files
        # For now, return None or implement caching
        return None

class PostgreSQLUserRepository:
    """PostgreSQL user repository"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'health_assistant'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def save(self, user: User) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (id, email, created_at, updated_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (email)
                        DO UPDATE SET updated_at = %s
                    """, (user.id, user.email, user.created_at, user.updated_at, user.updated_at))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False

    def find_by_email(self, email: str) -> Optional[User]:
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                    result = cur.fetchone()
                    if result:
                        user = User(email=result['email'], user_id=str(result['id']))
                        user.created_at = result['created_at']
                        user.updated_at = result['updated_at']
                        return user
        except Exception as e:
            print(f"Error finding user: {e}")
        return None

class PostgreSQLChatRepository:
    """PostgreSQL chat repository"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'health_assistant'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def save_session(self, session: ChatSession) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Insert/update session
                    cur.execute("""
                        INSERT INTO chat_sessions (id, user_id, title, session_id, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (session_id)
                        DO UPDATE SET title = %s, updated_at = %s
                    """, (
                        session.id, session.user_id, session.title, session.session_id,
                        session.created_at, session.updated_at, session.title, session.updated_at
                    ))

                    # Get session database ID
                    cur.execute("SELECT id FROM chat_sessions WHERE session_id = %s", (session.session_id,))
                    session_db_id = cur.fetchone()[0]

                    # Insert messages
                    for order, message in enumerate(session.messages):
                        cur.execute("""
                            INSERT INTO messages (id, session_id, sender, text, file_name, file_path, timestamp, message_order)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (
                            message.id, session_db_id, message.sender, message.text,
                            message.file_name, message.file_path, message.timestamp, order
                        ))

                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def find_by_user(self, user_email: str) -> List[ChatSession]:
        # Implementation would join users and chat_sessions tables
        # Similar implementation for MongoDB
        pass

# MongoDB implementations would follow similar patterns...

# Database factory function
def get_chat_repository():
    """Get appropriate chat repository based on DB_TYPE"""
    if DB_TYPE == 'postgresql':
        return PostgreSQLChatRepository()
    elif DB_TYPE == 'mongodb':
        # return MongoDBChatRepository()
        return JSONChatRepository()  # Fallback
    else:
        return JSONChatRepository()

def get_user_repository():
    """Get appropriate user repository based on DB_TYPE"""
    if DB_TYPE == 'postgresql':
        return PostgreSQLUserRepository()
    elif DB_TYPE == 'mongodb':
        # return MongoDBUserRepository()
        return JSONUserRepository()  # Fallback
    else:
        return JSONUserRepository()