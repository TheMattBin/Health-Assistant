// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the health assistant database
db = db.getSiblingDB('health_assistant');

// Create the application user with read/write permissions
db.createUser({
  user: 'health_app',
  pwd: 'health_password',
  roles: [
    {
      role: 'readWrite',
      db: 'health_assistant'
    }
  ]
});

// Create collections with default settings (optional)
db.createCollection('users');
db.createCollection('chat_sessions');
db.createCollection('messages');
db.createCollection('file_uploads');

// Create initial indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.chat_sessions.createIndex({ "user_id": 1 });
db.chat_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.messages.createIndex({ "session_id": 1 });
db.messages.createIndex({ "timestamp": -1 });
db.file_uploads.createIndex({ "user_id": 1 });

// Insert sample welcome document (optional)
db.welcome.insertOne({
  message: "Health Assistant Database initialized successfully!",
  created_at: new Date()
});

print('MongoDB database initialized successfully!');