// MongoDB Schema Design for AI Health Assistant
// Migration from JSON-based storage to document database

// MongoDB collections and indexes
db = db.getSiblingDB('health_assistant');

// Users collection
db.users.createIndex({ "email": 1 }, { unique: true });

// Insert user schema validation (optional but recommended)
db.runCommand({
  collMod: "users",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        created_at: {
          bsonType: "date"
        },
        updated_at: {
          bsonType: "date"
        }
      }
    }
  }
});

// Chat sessions collection
db.chat_sessions.createIndex({ "user_id": 1 });
db.chat_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.chat_sessions.createIndex({ "created_at": -1 });

// Messages collection
db.messages.createIndex({ "session_id": 1 });
db.messages.createIndex({ "timestamp": -1 });
db.messages.createIndex({ "sender": 1 });

// File uploads collection
db.file_uploads.createIndex({ "user_id": 1 });
db.file_uploads.createIndex({ "session_id": 1 });
db.file_uploads.createIndex({ "message_id": 1 });
db.file_uploads.createIndex({ "upload_timestamp": -1 });

// Compound index for common queries
db.messages.createIndex({ "session_id": 1, "message_order": 1 });

// Sample user document structure
/*
{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-01-01T00:00:00Z"),
  "metadata": {
    "total_sessions": 5,
    "total_messages": 45,
    "last_login": ISODate("2025-01-15T10:30:00Z")
  }
}
*/

// Sample chat session document structure
/*
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "session_id": "session_1759799360.00566",
  "title": "Health Consultation",
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-01-01T00:00:00Z"),
  "metadata": {
    "message_count": 10,
    "file_count": 2,
    "last_message_timestamp": ISODate("2025-01-01T01:00:00Z")
  }
}
*/

// Sample message document structure
/*
{
  "_id": ObjectId("..."),
  "session_id": ObjectId("..."),
  "sender": "user", // or "ai"
  "text": "What can you tell me about this X-ray?",
  "file_name": "chest_xray.png",
  "file_path": "uploads/users/user@example.com/20250101_120000_abc123.png",
  "timestamp": ISODate("2025-01-01T00:00:00Z"),
  "message_order": 1,
  "metadata": {
    "processing_time": 2.5, // seconds
    "model_used": "medgemma-4b",
    "confidence_score": 0.95
  }
}
*/

// Sample file upload document structure
/*
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "session_id": ObjectId("..."),
  "message_id": ObjectId("..."),
  "original_filename": "my_xray.png",
  "stored_filename": "20250101_120000_abc123.png",
  "file_path": "uploads/users/user@example.com/20250101_120000_abc123.png",
  "file_size": 1024000,
  "mime_type": "image/png",
  "upload_timestamp": ISODate("2025-01-01T00:00:00Z"),
  "metadata": {
    "file_hash": "sha256:abc123...",
    "extracted_text": "OCR text if applicable",
    "analysis_results": {
      "ai_findings": "Normal chest X-ray",
      "confidence": 0.98
    }
  }
}
*/

print("MongoDB collections and indexes created successfully!");