#!/usr/bin/env python3
"""
Migration script to convert JSON chat history to PostgreSQL database
Run with: python migrate_to_postgresql.py
"""

import os
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import uuid
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONToPostgreSQLMigrator:
    def __init__(self, db_config=None):
        self.db_config = db_config or {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'health_assistant'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        self.chat_history_dir = Path('backend/chat_history_db')

    def connect_to_db(self):
        """Establish database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = False
            logger.info("Connected to PostgreSQL database")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def create_user_if_not_exists(self, conn, email):
        """Create user if not exists and return user ID"""
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (email, created_at, updated_at)
                VALUES (%s, NOW(), NOW())
                ON CONFLICT (email)
                DO UPDATE SET updated_at = NOW()
                RETURNING id
            """, (email,))
            result = cur.fetchone()
            conn.commit()
            return result[0]

    def create_chat_session(self, conn, user_id, session_data):
        """Create chat session and return session ID"""
        with conn.cursor() as cur:
            session_uuid = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO chat_sessions (id, user_id, title, session_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (session_id)
                DO UPDATE SET title = EXCLUDED.title, updated_at = NOW()
                RETURNING id
            """, (
                session_uuid,
                user_id,
                session_data.get('title', 'New Chat'),
                session_data['id'],
                session_data.get('created_at', datetime.now())
            ))
            result = cur.fetchone()
            conn.commit()
            return result[0]

    def create_messages(self, conn, session_id, messages):
        """Create messages for a session"""
        if not messages:
            return

        message_data = []
        file_upload_data = []

        for order, message in enumerate(messages):
            # Handle nested session data (edge case found in demo data)
            if isinstance(message, dict) and 'id' in message and 'messages' in message:
                # This is a nested session, extract the messages
                nested_messages = message['messages']
                for nested_order, nested_msg in enumerate(nested_messages):
                    message_uuid = str(uuid.uuid4())
                    timestamp = self.parse_timestamp(nested_msg.get('timestamp'))

                    message_data.append((
                        message_uuid,
                        session_id,
                        nested_msg.get('sender', 'user'),
                        nested_msg.get('text', ''),
                        nested_msg.get('fileName'),
                        nested_msg.get('filePath'),
                        timestamp,
                        nested_order
                    ))

                    # Track file uploads separately
                    if nested_msg.get('fileName'):
                        file_upload_data.append(self.create_file_upload_data(
                            session_id, message_uuid, nested_msg
                        ))
                continue

            # Normal message processing
            message_uuid = str(uuid.uuid4())
            timestamp = self.parse_timestamp(message.get('timestamp'))

            message_data.append((
                message_uuid,
                session_id,
                message.get('sender', 'user'),
                message.get('text', ''),
                message.get('fileName'),
                message.get('filePath'),
                timestamp,
                order
            ))

            # Track file uploads separately
            if message.get('fileName'):
                file_upload_data.append(self.create_file_upload_data(
                    session_id, message_uuid, message
                ))

        # Insert messages
        if message_data:
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO messages (id, session_id, sender, text, file_name, file_path, timestamp, message_order)
                    VALUES %s
                    """,
                    message_data
                )

        # Insert file uploads
        if file_upload_data:
            self.insert_file_uploads(conn, file_upload_data)

        conn.commit()

    def create_file_upload_data(self, session_id, message_id, message):
        """Create file upload data structure"""
        file_path = message.get('filePath') or message.get('file_path')
        if not file_path and message.get('fileName'):
            # Construct file path from filename
            file_path = f"uploads/users/unknown/{message['fileName']}"

        return (
            str(uuid.uuid4()),  # file_upload_id
            session_id,         # session_id
            message_id,         # message_id
            message.get('fileName', 'unknown'),
            message.get('fileName', 'unknown'),  # stored_filename (same as original for now)
            file_path,
            None,  # file_size (would need to read file to determine)
            None,  # mime_type
            self.parse_timestamp(message.get('timestamp'))
        )

    def insert_file_uploads(self, conn, file_data):
        """Insert file upload records"""
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO file_uploads (id, session_id, message_id, original_filename, stored_filename, file_path, file_size, mime_type, upload_timestamp)
                VALUES %s
                """,
                file_data
            )

    def parse_timestamp(self, timestamp_str):
        """Parse various timestamp formats"""
        if not timestamp_str:
            return datetime.now()

        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse timestamp: {timestamp_str}")
        return datetime.now()

    def migrate_all_users(self):
        """Migrate all user chat histories"""
        if not self.chat_history_dir.exists():
            logger.error(f"Chat history directory not found: {self.chat_history_dir}")
            return

        conn = self.connect_to_db()

        try:
            json_files = list(self.chat_history_dir.glob('*.json'))
            logger.info(f"Found {len(json_files)} JSON files to migrate")

            total_sessions = 0
            total_messages = 0

            for json_file in json_files:
                if json_file.name.endswith('.backup'):
                    continue

                email = json_file.stem  # Remove .json extension
                logger.info(f"Migrating chat history for: {email}")

                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        sessions = json.load(f)

                    # Create or get user
                    user_id = self.create_user_if_not_exists(conn, email)

                    # Migrate each session
                    for session in sessions:
                        if not isinstance(session, dict) or 'id' not in session:
                            logger.warning(f"Skipping invalid session: {session}")
                            continue

                        # Create session
                        session_id = self.create_chat_session(conn, user_id, session)

                        # Create messages
                        messages = session.get('messages', [])
                        self.create_messages(conn, session_id, messages)

                        total_sessions += 1
                        total_messages += len(messages)

                    logger.info(f"Migrated {len(sessions)} sessions for {email}")

                except Exception as e:
                    logger.error(f"Error migrating {email}: {e}")
                    conn.rollback()
                    continue

            logger.info(f"Migration completed! Total sessions: {total_sessions}, Total messages: {total_messages}")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def verify_migration(self):
        """Verify migration results"""
        conn = self.connect_to_db()

        try:
            with conn.cursor() as cur:
                # Count users
                cur.execute("SELECT COUNT(*) FROM users")
                user_count = cur.fetchone()[0]

                # Count sessions
                cur.execute("SELECT COUNT(*) FROM chat_sessions")
                session_count = cur.fetchone()[0]

                # Count messages
                cur.execute("SELECT COUNT(*) FROM messages")
                message_count = cur.fetchone()[0]

                # Count files
                cur.execute("SELECT COUNT(*) FROM file_uploads")
                file_count = cur.fetchone()[0]

                logger.info(f"Migration verification:")
                logger.info(f"  Users: {user_count}")
                logger.info(f"  Sessions: {session_count}")
                logger.info(f"  Messages: {message_count}")
                logger.info(f"  Files: {file_count}")

                # Show sample data
                cur.execute("""
                    SELECT u.email, COUNT(cs.id) as session_count
                    FROM users u
                    LEFT JOIN chat_sessions cs ON u.id = cs.user_id
                    GROUP BY u.email
                    LIMIT 5
                """)

                logger.info("Sample users with session counts:")
                for row in cur.fetchall():
                    logger.info(f"  {row[0]}: {row[1]} sessions")

        finally:
            conn.close()

def main():
    """Main migration function"""
    migrator = JSONToPostgreSQLMigrator()

    try:
        logger.info("Starting JSON to PostgreSQL migration...")
        migrator.migrate_all_users()
        migrator.verify_migration()
        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())