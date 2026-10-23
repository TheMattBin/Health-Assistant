#!/usr/bin/env python3
"""
Migration script to convert JSON chat history to MongoDB database
Run with: python migrate_to_mongodb.py
"""

import os
import json
from datetime import datetime
from pymongo import MongoClient
from pathlib import Path
import logging
from bson import ObjectId
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONToMongoDBMigrator:
    def __init__(self, mongodb_uri=None):
        self.mongodb_uri = mongodb_uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.db_name = os.getenv('DB_NAME', 'health_assistant')
        self.chat_history_dir = Path('backend/chat_history_db')

        # Connect to MongoDB
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.db_name]

        # Get collections
        self.users_collection = self.db['users']
        self.sessions_collection = self.db['chat_sessions']
        self.messages_collection = self.db['messages']
        self.file_uploads_collection = self.db['file_uploads']

    def create_user_if_not_exists(self, email):
        """Create user if not exists and return user ID"""
        user = self.users_collection.find_one({'email': email})

        if user:
            # Update last modified time
            self.users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'updated_at': datetime.now()}}
            )
            return user['_id']
        else:
            # Create new user
            user_doc = {
                'email': email,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'metadata': {
                    'total_sessions': 0,
                    'total_messages': 0,
                    'last_login': None
                }
            }
            result = self.users_collection.insert_one(user_doc)
            return result.inserted_id

    def create_chat_session(self, user_id, session_data):
        """Create chat session and return session ID"""
        session_doc = {
            'user_id': user_id,
            'session_id': session_data['id'],
            'title': session_data.get('title', 'New Chat'),
            'created_at': self.parse_timestamp(session_data.get('created_at')),
            'updated_at': datetime.now(),
            'metadata': {
                'message_count': len(session_data.get('messages', [])),
                'file_count': 0,  # Will be updated later
                'last_message_timestamp': None
            }
        }

        # Check if session already exists
        existing = self.sessions_collection.find_one({'session_id': session_data['id']})
        if existing:
            self.sessions_collection.update_one(
                {'_id': existing['_id']},
                {'$set': session_doc}
            )
            return existing['_id']
        else:
            result = self.sessions_collection.insert_one(session_doc)
            return result.inserted_id

    def create_messages(self, session_id, messages):
        """Create messages for a session and return file count"""
        if not messages:
            return 0

        message_docs = []
        file_uploads = []
        file_count = 0

        for order, message in enumerate(messages):
            # Handle nested session data (edge case found in demo data)
            if isinstance(message, dict) and 'id' in message and 'messages' in message:
                # This is a nested session, extract the messages
                nested_messages = message['messages']
                for nested_order, nested_msg in enumerate(nested_messages):
                    msg_doc = self.create_message_document(
                        session_id, nested_msg, nested_order
                    )
                    message_docs.append(msg_doc)

                    if nested_msg.get('fileName'):
                        file_doc = self.create_file_upload_document(
                            session_id, msg_doc['_id'], nested_msg
                        )
                        file_uploads.append(file_doc)
                        file_count += 1
                continue

            # Normal message processing
            msg_doc = self.create_message_document(session_id, message, order)
            message_docs.append(msg_doc)

            if message.get('fileName'):
                file_doc = self.create_file_upload_document(
                    session_id, msg_doc['_id'], message
                )
                file_uploads.append(file_doc)
                file_count += 1

        # Insert messages in bulk
        if message_docs:
            self.messages_collection.insert_many(message_docs)

        # Insert file uploads in bulk
        if file_uploads:
            self.file_uploads_collection.insert_many(file_uploads)

        return file_count

    def create_message_document(self, session_id, message, order):
        """Create a message document"""
        return {
            'session_id': session_id,
            'sender': message.get('sender', 'user'),
            'text': message.get('text', ''),
            'file_name': message.get('fileName'),
            'file_path': message.get('filePath') or message.get('file_path'),
            'timestamp': self.parse_timestamp(message.get('timestamp')),
            'message_order': order,
            'metadata': {
                'processing_time': None,
                'model_used': 'medgemma-4b',
                'confidence_score': None
            }
        }

    def create_file_upload_document(self, session_id, message_id, message):
        """Create a file upload document"""
        file_path = message.get('filePath') or message.get('file_path')
        if not file_path and message.get('fileName'):
            # Construct file path from filename
            file_path = f"uploads/users/unknown/{message['fileName']}"

        return {
            'session_id': session_id,
            'message_id': message_id,
            'original_filename': message.get('fileName', 'unknown'),
            'stored_filename': message.get('fileName', 'unknown'),
            'file_path': file_path,
            'file_size': self.get_file_size(file_path),
            'mime_type': self.get_mime_type(message.get('fileName')),
            'upload_timestamp': self.parse_timestamp(message.get('timestamp')),
            'metadata': {
                'file_hash': None,  # Would be calculated if file exists
                'extracted_text': None,
                'analysis_results': None
            }
        }

    def get_file_size(self, file_path):
        """Get file size if file exists"""
        try:
            if file_path and os.path.exists(file_path):
                return os.path.getsize(file_path)
        except Exception:
            pass
        return None

    def get_mime_type(self, filename):
        """Get MIME type based on file extension"""
        if not filename:
            return None

        ext = filename.lower().split('.')[-1]
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return mime_types.get(ext)

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

        json_files = list(self.chat_history_dir.glob('*.json'))
        logger.info(f"Found {len(json_files)} JSON files to migrate")

        total_sessions = 0
        total_messages = 0
        total_files = 0

        for json_file in json_files:
            if json_file.name.endswith('.backup'):
                continue

            email = json_file.stem  # Remove .json extension
            logger.info(f"Migrating chat history for: {email}")

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)

                # Create or get user
                user_id = self.create_user_if_not_exists(email)

                user_session_count = 0
                user_message_count = 0
                user_file_count = 0

                # Migrate each session
                for session in sessions:
                    if not isinstance(session, dict) or 'id' not in session:
                        logger.warning(f"Skipping invalid session: {session}")
                        continue

                    # Create session
                    session_id = self.create_chat_session(user_id, session)

                    # Create messages
                    messages = session.get('messages', [])
                    file_count = self.create_messages(session_id, messages)

                    # Update session metadata
                    self.sessions_collection.update_one(
                        {'_id': session_id},
                        {
                            '$set': {
                                'metadata.file_count': file_count,
                                'metadata.last_message_timestamp': self.get_last_message_timestamp(messages)
                            }
                        }
                    )

                    user_session_count += 1
                    user_message_count += len(messages)
                    user_file_count += file_count

                # Update user metadata
                self.users_collection.update_one(
                    {'_id': user_id},
                    {
                        '$set': {
                            'metadata.total_sessions': user_session_count,
                            'metadata.total_messages': user_message_count,
                            'updated_at': datetime.now()
                        }
                    }
                )

                total_sessions += user_session_count
                total_messages += user_message_count
                total_files += user_file_count

                logger.info(f"Migrated {user_session_count} sessions, {user_message_count} messages, {user_file_count} files for {email}")

            except Exception as e:
                logger.error(f"Error migrating {email}: {e}")
                continue

        logger.info(f"Migration completed! Total sessions: {total_sessions}, Total messages: {total_messages}, Total files: {total_files}")

    def get_last_message_timestamp(self, messages):
        """Get the timestamp of the last message in a session"""
        if not messages:
            return None

        last_timestamp = None
        for message in messages:
            if isinstance(message, dict) and 'messages' in message:
                # Handle nested messages
                for nested_msg in message['messages']:
                    timestamp = self.parse_timestamp(nested_msg.get('timestamp'))
                    if timestamp and (not last_timestamp or timestamp > last_timestamp):
                        last_timestamp = timestamp
            else:
                timestamp = self.parse_timestamp(message.get('timestamp'))
                if timestamp and (not last_timestamp or timestamp > last_timestamp):
                    last_timestamp = timestamp

        return last_timestamp

    def verify_migration(self):
        """Verify migration results"""
        user_count = self.users_collection.count_documents({})
        session_count = self.sessions_collection.count_documents({})
        message_count = self.messages_collection.count_documents({})
        file_count = self.file_uploads_collection.count_documents({})

        logger.info(f"Migration verification:")
        logger.info(f"  Users: {user_count}")
        logger.info(f"  Sessions: {session_count}")
        logger.info(f"  Messages: {message_count}")
        logger.info(f"  Files: {file_count}")

        # Show sample data
        pipeline = [
            {
                '$lookup': {
                    'from': 'chat_sessions',
                    'localField': '_id',
                    'foreignField': 'user_id',
                    'as': 'sessions'
                }
            },
            {
                '$project': {
                    'email': 1,
                    'session_count': {'$size': '$sessions'}
                }
            },
            {'$limit': 5}
        ]

        logger.info("Sample users with session counts:")
        for user in self.users_collection.aggregate(pipeline):
            logger.info(f"  {user['email']}: {user['session_count']} sessions")

    def create_indexes(self):
        """Create MongoDB indexes for better performance"""
        logger.info("Creating MongoDB indexes...")

        # Users indexes
        self.users_collection.create_index('email', unique=True)

        # Chat sessions indexes
        self.sessions_collection.create_index('user_id')
        self.sessions_collection.create_index('session_id', unique=True)
        self.sessions_collection.create_index('created_at', -1)

        # Messages indexes
        self.messages_collection.create_index('session_id')
        self.messages_collection.create_index('timestamp', -1)
        self.messages_collection.create_index('sender')
        self.messages_collection.create_index([('session_id', 1), ('message_order', 1)])

        # File uploads indexes
        self.file_uploads_collection.create_index('user_id')
        self.file_uploads_collection.create_index('session_id')
        self.file_uploads_collection.create_index('message_id')
        self.file_uploads_collection.create_index('upload_timestamp', -1)

        logger.info("Indexes created successfully")

    def close(self):
        """Close database connection"""
        self.client.close()

def main():
    """Main migration function"""
    migrator = JSONToMongoDBMigrator()

    try:
        logger.info("Starting JSON to MongoDB migration...")
        migrator.create_indexes()
        migrator.migrate_all_users()
        migrator.verify_migration()
        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1
    finally:
        migrator.close()

    return 0

if __name__ == "__main__":
    exit(main())