# Database Migration Guide

This guide explains how to migrate from the current JSON-based storage to PostgreSQL or MongoDB for your AI Health Assistant.

## Overview

Your application currently stores chat history as JSON files in `backend/chat_history_db/`. This guide helps you migrate to a proper database solution for better performance, scalability, and data management.

## Current Data Structure

Each user has a JSON file containing an array of chat sessions:

```json
[
  {
    "id": "session_1759799360.00566",
    "title": "New Chat",
    "created_at": "2025-10-07T09:09:20.005660",
    "messages": [
      {
        "sender": "user",
        "text": "Your health question here",
        "fileName": "xray.png",
        "filePath": "uploads/users/user@example.com/xray.png",
        "timestamp": "2025-10-07T09:11:30.979Z"
      }
    ]
  }
]
```

## Database Options

### PostgreSQL (Recommended)
- **Pros**: ACID compliance, complex queries, JSON support, proven reliability
- **Cons**: More rigid schema, requires migrations for schema changes
- **Best for**: Production applications requiring data consistency

### MongoDB
- **Pros**: Flexible schema, document-oriented, easier for rapid development
- **Cons**: Eventual consistency, less suited for complex transactions
- **Best for**: Applications with evolving data structure

## Quick Start

### 1. Choose Your Database

**PostgreSQL (Recommended for production):**
```bash
# Linux/Mac
./scripts/migrate_database.sh postgresql migrate

# Windows PowerShell
.\scripts\migrate_database.ps1 postgresql migrate
```

**MongoDB:**
```bash
# Linux/Mac
./scripts/migrate_database.sh mongodb migrate

# Windows PowerShell
.\scripts\migrate_database.ps1 mongodb migrate
```

### 2. Update Backend Configuration

After migration, update your `.env` file:

**For PostgreSQL:**
```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=health_assistant
DB_USER=postgres
DB_PASSWORD=password
DATABASE_URL=postgresql://postgres:password@localhost:5432/health_assistant
```

**For MongoDB:**
```env
DB_TYPE=mongodb
MONGODB_URI=mongodb://admin:password@localhost:27017
DB_NAME=health_assistant
```

## Manual Migration Steps

### Prerequisites

1. **Docker** installed and running
2. **Python 3.8+** with required packages
3. **Existing JSON data** in `backend/chat_history_db/`

### Step 1: Backup Data

```bash
# Create backup
./scripts/migrate_database.sh postgresql backup

# Manual backup
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/chat_history_db/
```

### Step 2: Start Database Services

```bash
# Start PostgreSQL
docker-compose -f docker-compose.db.yml up -d postgres

# Start MongoDB
docker-compose -f docker-compose.db.yml up -d mongodb
```

### Step 3: Setup Database Schema

**PostgreSQL:**
```bash
docker exec -i health_assistant_postgres psql -U postgres -d health_assistant < database/postgresql/schema.sql
```

**MongoDB:**
```bash
docker exec -i health_assistant_mongodb mongosh health_assistant < database/mongodb/collections.js
```

### Step 4: Run Migration

**PostgreSQL:**
```bash
cd database/migrations
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=health_assistant
export DB_USER=postgres
export DB_PASSWORD=password

python migrate_to_postgresql.py
```

**MongoDB:**
```bash
cd database/migrations
export MONGODB_URI="mongodb://admin:password@localhost:27017"
export DB_NAME=health_assistant

python migrate_to_mongodb.py
```

## Database Schemas

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id),
    sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'ai')),
    text TEXT,
    file_name VARCHAR(500),
    file_path VARCHAR(1000),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_order INTEGER NOT NULL
);

-- File uploads table
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID REFERENCES chat_sessions(id),
    message_id UUID REFERENCES messages(id),
    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### MongoDB Collections

```javascript
// Users collection
{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-01-01T00:00:00Z"),
  "metadata": {
    "total_sessions": 5,
    "total_messages": 45
  }
}

// Chat sessions collection
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "session_id": "session_1759799360.00566",
  "title": "Health Consultation",
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-01-01T00:00:00Z"),
  "metadata": {
    "message_count": 10,
    "file_count": 2
  }
}

// Messages collection
{
  "_id": ObjectId("..."),
  "session_id": ObjectId("..."),
  "sender": "user",
  "text": "What can you tell me about this X-ray?",
  "file_name": "chest_xray.png",
  "file_path": "uploads/users/user@example.com/chest_xray.png",
  "timestamp": ISODate("2025-01-01T00:00:00Z"),
  "message_order": 1
}
```

## Migration Scripts

### Automated Migration

The migration scripts handle:

1. **Data backup** - Creates timestamped backup of JSON files
2. **Database setup** - Creates schemas/collections
3. **Data migration** - Transforms and inserts data
4. **Verification** - Validates migrated data
5. **Environment update** - Updates `.env` configuration

### Script Options

```bash
# Full migration (backup + setup + migrate + verify)
./scripts/migrate_database.sh postgresql migrate

# Individual steps
./scripts/migrate_database.sh postgresql backup    # Backup only
./scripts/migrate_database.sh postgresql setup     # Setup database only
./scripts/migrate_database.sh postgresql verify    # Verify migration
./scripts/migrate_database.sh postgresql stop      # Stop services
```

## Post-Migration Tasks

### 1. Update Backend Code

After migration, update your backend code to use the database:

```python
# In your chat history router
from backend.database.models import ChatSession, User, get_chat_repository

# Get user sessions
sessions = ChatSession.find_by_user(user_email)

# Save new session
session = ChatSession(user_id=user_id, title="New Chat")
session.add_message(message)
session.save()
```

### 2. Update Docker Configuration

Add database services to your `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: health_assistant
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. Test the Application

1. Start your application with the new database
2. Test creating new chat sessions
3. Test file uploads
4. Verify data persistence
5. Check performance improvements

## Verification

### PostgreSQL Verification

```sql
-- Check migrated data
SELECT
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM chat_sessions) as total_sessions,
    (SELECT COUNT(*) FROM messages) as total_messages,
    (SELECT COUNT(*) FROM file_uploads) as total_files;
```

### MongoDB Verification

```javascript
// Check migrated data
db.users.countDocuments();
db.chat_sessions.countDocuments();
db.messages.countDocuments();
db.file_uploads.countDocuments();
```

## Troubleshooting

### Common Issues

1. **Connection Errors:**
   ```bash
   # Check if database is running
   docker-compose -f docker-compose.db.yml ps

   # Check database logs
   docker-compose -f docker-compose.db.yml logs postgres
   ```

2. **Migration Failures:**
   ```bash
   # Check migration logs
   tail -f database/logs/postgresql_migration_*.log

   # Check JSON data format
   python -m json.tool backend/chat_history_db/your_file.json
   ```

3. **Permission Errors:**
   ```bash
   # Fix file permissions
   chmod +x scripts/migrate_database.sh

   # Check Docker permissions
   sudo usermod -aG docker $USER
   ```

### Rollback

If migration fails, you can rollback:

```bash
# Stop database services
docker-compose -f docker-compose.db.yml down

# Restore from backup (if needed)
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz

# Reset to JSON storage
# Remove DB_TYPE from .env file or set to "json"
```

## Performance Considerations

### PostgreSQL Optimization

1. **Indexes:** Created automatically for foreign keys and common queries
2. **Connection pooling:** Use pgbouncer for high-traffic applications
3. **Partitioning:** Consider partitioning by date for large datasets

### MongoDB Optimization

1. **Indexes:** Compound indexes for common query patterns
2. **Sharding:** Consider sharding for very large datasets
3. **Aggregation pipelines:** Use for complex data analysis

## Production Deployment

### Security

1. **Change default passwords**
2. **Use SSL connections**
3. **Restrict network access**
4. **Regular backups**

### Monitoring

1. **Database metrics:** Connections, queries, performance
2. **Application metrics:** Response times, error rates
3. **Storage monitoring:** Disk usage, growth trends

### Backup Strategy

1. **Automated backups:** Daily or hourly
2. **Point-in-time recovery:** Enable binary logs (PostgreSQL) or oplog (MongoDB)
3. **Cross-region replication:** For disaster recovery

## Support

For issues with the migration:

1. Check the migration logs in `database/logs/`
2. Verify Docker and database service status
3. Test with small datasets first
4. Join the community forums for additional support