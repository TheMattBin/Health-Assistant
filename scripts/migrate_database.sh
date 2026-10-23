#!/bin/bash

# Database Migration Script
# This script helps migrate from JSON storage to PostgreSQL or MongoDB

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Configuration
BACKUP_DIR="database/backups"
MIGRATION_LOGS="database/logs"

# Create necessary directories
create_directories() {
    print_step "Creating backup and log directories..."
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$MIGRATION_LOGS"
}

# Backup existing JSON data
backup_json_data() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/chat_history_backup_$timestamp.tar.gz"

    print_step "Creating backup of existing JSON data..."

    if [ -d "backend/chat_history_db" ]; then
        tar -czf "$backup_file" backend/chat_history_db/
        print_info "Backup created: $backup_file"
    else
        print_warning "No JSON data directory found to backup"
    fi
}

# Start database services
start_databases() {
    local db_type=$1
    print_step "Starting $db_type database service..."

    # Start the database containers
    docker-compose -f docker-compose.db.yml up -d $db_type

    # Wait for database to be ready
    print_info "Waiting for $db_type to be ready..."
    sleep 10

    # Check database health
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if [ "$db_type" = "postgres" ]; then
            if docker exec health_assistant_postgres pg_isready -U postgres > /dev/null 2>&1; then
                print_info "$db_type is ready!"
                break
            fi
        elif [ "$db_type" = "mongodb" ]; then
            if docker exec health_assistant_mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
                print_info "$db_type is ready!"
                break
            fi
        fi

        print_info "Attempt $attempt/$max_attempts: Waiting for $db_type..."
        sleep 2
        attempt=$((attempt + 1))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_error "$db_type failed to start within expected time"
        exit 1
    fi
}

# Setup PostgreSQL schema
setup_postgresql() {
    print_step "Setting up PostgreSQL schema..."

    # Execute schema creation
    docker exec -i health_assistant_postgres psql -U postgres -d health_assistant < database/postgresql/schema.sql

    print_info "PostgreSQL schema created successfully!"
}

# Setup MongoDB collections
setup_mongodb() {
    print_step "Setting up MongoDB collections..."

    # Execute collections setup
    docker exec -i health_assistant_mongodb mongosh health_assistant < database/mongodb/collections.js

    print_info "MongoDB collections created successfully!"
}

# Run PostgreSQL migration
run_postgresql_migration() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$MIGRATION_LOGS/postgresql_migration_$timestamp.log"

    print_step "Running PostgreSQL migration..."

    # Set environment variables for migration
    export DB_HOST=localhost
    export DB_PORT=5432
    export DB_NAME=health_assistant
    export DB_USER=postgres
    export DB_PASSWORD=password

    # Run migration script
    cd database/migrations
    python3 migrate_to_postgresql.py 2>&1 | tee "$log_file"
    cd - > /dev/null

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_info "PostgreSQL migration completed successfully!"
        print_info "Migration log: $log_file"
    else
        print_error "PostgreSQL migration failed! Check log: $log_file"
        exit 1
    fi
}

# Run MongoDB migration
run_mongodb_migration() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$MIGRATION_LOGS/mongodb_migration_$timestamp.log"

    print_step "Running MongoDB migration..."

    # Set environment variables for migration
    export MONGODB_URI="mongodb://admin:password@localhost:27017"
    export DB_NAME=health_assistant

    # Run migration script
    cd database/migrations
    python3 migrate_to_mongodb.py 2>&1 | tee "$log_file"
    cd - > /dev/null

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_info "MongoDB migration completed successfully!"
        print_info "Migration log: $log_file"
    else
        print_error "MongoDB migration failed! Check log: $log_file"
        exit 1
    fi
}

# Update environment configuration
update_environment() {
    local db_type=$1
    print_step "Updating environment configuration for $db_type..."

    # Update .env file
    if [ "$db_type" = "postgresql" ]; then
        cat >> .env << EOF

# Database Configuration (PostgreSQL)
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=health_assistant
DB_USER=postgres
DB_PASSWORD=password
DATABASE_URL=postgresql://postgres:password@localhost:5432/health_assistant
EOF
    elif [ "$db_type" = "mongodb" ]; then
        cat >> .env << EOF

# Database Configuration (MongoDB)
DB_TYPE=mongodb
MONGODB_URI=mongodb://admin:password@localhost:27017
DB_NAME=health_assistant
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=password
EOF
    fi

    print_info "Environment configuration updated!"
}

# Verify migration
verify_migration() {
    local db_type=$1
    print_step "Verifying $db_type migration..."

    if [ "$db_type" = "postgresql" ]; then
        # Check PostgreSQL data
        docker exec health_assistant_postgres psql -U postgres -d health_assistant -c "
            SELECT
                (SELECT COUNT(*) FROM users) as users,
                (SELECT COUNT(*) FROM chat_sessions) as sessions,
                (SELECT COUNT(*) FROM messages) as messages;
        "
    elif [ "$db_type" = "mongodb" ]; then
        # Check MongoDB data
        docker exec health_assistant_mongodb mongosh health_assistant --eval "
            db.users.countDocuments();
            db.chat_sessions.countDocuments();
            db.messages.countDocuments();
        "
    fi

    print_info "Migration verification completed!"
}

# Stop databases
stop_databases() {
    print_step "Stopping database services..."
    docker-compose -f docker-compose.db.yml down
    print_info "Database services stopped!"
}

# Show usage
show_usage() {
    echo "Usage: $0 [postgresql|mongodb] [backup|migrate|setup|verify|stop]"
    echo ""
    echo "Commands:"
    echo "  postgresql    - Work with PostgreSQL database"
    echo "  mongodb       - Work with MongoDB database"
    echo ""
    echo "Options:"
    echo "  backup        - Backup existing JSON data only"
    echo "  setup         - Setup database schema only"
    echo "  migrate       - Run full migration (backup + setup + migrate)"
    echo "  verify        - Verify migration results"
    echo "  stop          - Stop database services"
    echo ""
    echo "Examples:"
    echo "  $0 postgresql migrate    - Full migration to PostgreSQL"
    echo "  $0 mongodb setup         - Setup MongoDB only"
    echo "  $0 postgresql verify     - Verify PostgreSQL migration"
}

# Main execution
main() {
    local db_type=$1
    local action=$2

    case $db_type in
        postgresql|mongodb)
            case $action in
                backup)
                    create_directories
                    backup_json_data
                    ;;
                setup)
                    create_directories
                    start_databases $db_type
                    if [ "$db_type" = "postgresql" ]; then
                        setup_postgresql
                    else
                        setup_mongodb
                    fi
                    ;;
                migrate|"" )
                    create_directories
                    backup_json_data
                    start_databases $db_type
                    if [ "$db_type" = "postgresql" ]; then
                        setup_postgresql
                        run_postgresql_migration
                    else
                        setup_mongodb
                        run_mongodb_migration
                    fi
                    update_environment $db_type
                    verify_migration $db_type
                    ;;
                verify)
                    verify_migration $db_type
                    ;;
                stop)
                    stop_databases
                    ;;
                *)
                    show_usage
                    exit 1
                    ;;
            esac
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Run main function
main "$@"