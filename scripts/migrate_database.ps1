# Database Migration Script for PowerShell
# This script helps migrate from JSON storage to PostgreSQL or MongoDB

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("postgresql", "mongodb")]
    [string]$DatabaseType,

    [Parameter(Mandatory=$false)]
    [ValidateSet("backup", "setup", "migrate", "verify", "stop")]
    [string]$Action = "migrate"
)

# Color functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Blue
}

# Configuration
$BackupDir = "database\backups"
$MigrationLogs = "database\logs"

# Create necessary directories
function Create-Directories {
    Write-Step "Creating backup and log directories..."
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    New-Item -ItemType Directory -Force -Path $MigrationLogs | Out-Null
}

# Backup existing JSON data
function Backup-JsonData {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "$BackupDir\chat_history_backup_$timestamp.tar.gz"

    Write-Step "Creating backup of existing JSON data..."

    if (Test-Path "backend\chat_history_db") {
        # Use tar (available in Windows 10+)
        tar -czf $backupFile backend\chat_history_db\
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Backup created: $backupFile"
        } else {
            Write-Warning "Backup creation failed"
        }
    } else {
        Write-Warning "No JSON data directory found to backup"
    }
}

# Start database services
function Start-Databases {
    param([string]$DbType)

    Write-Step "Starting $DbType database service..."

    # Start the database containers
    docker-compose -f docker-compose.db.yml up -d $DbType

    # Wait for database to be ready
    Write-Info "Waiting for $DbType to be ready..."
    Start-Sleep -Seconds 10

    # Check database health
    $maxAttempts = 30
    $attempt = 1

    while ($attempt -le $maxAttempts) {
        if ($DbType -eq "postgres") {
            $result = docker exec health_assistant_postgres pg_isready -U postgres 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Info "$DbType is ready!"
                break
            }
        } elseif ($DbType -eq "mongodb") {
            $result = docker exec health_assistant_mongodb mongosh --eval "db.adminCommand('ping')" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Info "$DbType is ready!"
                break
            }
        }

        Write-Info "Attempt $attempt/$maxAttempts : Waiting for $DbType..."
        Start-Sleep -Seconds 2
        $attempt++
    }

    if ($attempt -gt $maxAttempts) {
        Write-Error "$DbType failed to start within expected time"
        exit 1
    }
}

# Setup PostgreSQL schema
function Setup-PostgreSQL {
    Write-Step "Setting up PostgreSQL schema..."

    # Execute schema creation
    $result = Get-Content "database\postgresql\schema.sql" | docker exec -i health_assistant_postgres psql -U postgres -d health_assistant

    if ($LASTEXITCODE -eq 0) {
        Write-Info "PostgreSQL schema created successfully!"
    } else {
        Write-Error "PostgreSQL schema creation failed"
        exit 1
    }
}

# Setup MongoDB collections
function Setup-MongoDB {
    Write-Step "Setting up MongoDB collections..."

    # Execute collections setup
    $result = Get-Content "database\mongodb\collections.js" | docker exec -i health_assistant_mongodb mongosh health_assistant

    if ($LASTEXITCODE -eq 0) {
        Write-Info "MongoDB collections created successfully!"
    } else {
        Write-Error "MongoDB collections creation failed"
        exit 1
    }
}

# Run PostgreSQL migration
function Run-PostgreSQLMigration {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile = "$MigrationLogs\postgresql_migration_$timestamp.log"

    Write-Step "Running PostgreSQL migration..."

    # Set environment variables for migration
    $env:DB_HOST = "localhost"
    $env:DB_PORT = "5432"
    $env:DB_NAME = "health_assistant"
    $env:DB_USER = "postgres"
    $env:DB_PASSWORD = "password"

    # Run migration script
    Set-Location "database\migrations"
    python migrate_to_postgresql.py *>&1 | Tee-Object -FilePath $logFile
    Set-Location -Path (Get-Location).Path.Replace("\database\migrations", "")

    if ($LASTEXITCODE -eq 0) {
        Write-Info "PostgreSQL migration completed successfully!"
        Write-Info "Migration log: $logFile"
    } else {
        Write-Error "PostgreSQL migration failed! Check log: $logFile"
        exit 1
    }

    # Clear environment variables
    Remove-Item Env:\DB_HOST,Env:\DB_PORT,Env:\DB_NAME,Env:\DB_USER,Env:\DB_PASSWORD -ErrorAction SilentlyContinue
}

# Run MongoDB migration
function Run-MongoDBMigration {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile = "$MigrationLogs\mongodb_migration_$timestamp.log"

    Write-Step "Running MongoDB migration..."

    # Set environment variables for migration
    $env:MONGODB_URI = "mongodb://admin:password@localhost:27017"
    $env:DB_NAME = "health_assistant"

    # Run migration script
    Set-Location "database\migrations"
    python migrate_to_mongodb.py *>&1 | Tee-Object -FilePath $logFile
    Set-Location -Path (Get-Location).Path.Replace("\database\migrations", "")

    if ($LASTEXITCODE -eq 0) {
        Write-Info "MongoDB migration completed successfully!"
        Write-Info "Migration log: $logFile"
    } else {
        Write-Error "MongoDB migration failed! Check log: $logFile"
        exit 1
    }

    # Clear environment variables
    Remove-Item Env:\MONGODB_URI,Env:\DB_NAME -ErrorAction SilentlyContinue
}

# Update environment configuration
function Update-Environment {
    param([string]$DbType)

    Write-Step "Updating environment configuration for $DbType..."

    $envContent = @"

# Database Configuration ($($DbType.ToUpper())
DB_TYPE=$DbType
"@

    if ($DbType -eq "postgresql") {
        $envContent += @"
DB_HOST=localhost
DB_PORT=5432
DB_NAME=health_assistant
DB_USER=postgres
DB_PASSWORD=password
DATABASE_URL=postgresql://postgres:password@localhost:5432/health_assistant
"@
    } elseif ($DbType -eq "mongodb") {
        $envContent += @"
MONGODB_URI=mongodb://admin:password@localhost:27017
DB_NAME=health_assistant
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=password
"@
    }

    # Append to .env file
    Add-Content -Path ".env" -Value $envContent

    Write-Info "Environment configuration updated!"
}

# Verify migration
function Verify-Migration {
    param([string]$DbType)

    Write-Step "Verifying $DbType migration..."

    if ($DbType -eq "postgresql") {
        # Check PostgreSQL data
        $query = @"
            SELECT
                (SELECT COUNT(*) FROM users) as users,
                (SELECT COUNT(*) FROM chat_sessions) as sessions,
                (SELECT COUNT(*) FROM messages) as messages;
"@
        docker exec health_assistant_postgres psql -U postgres -d health_assistant -c $query
    } elseif ($DbType -eq "mongodb") {
        # Check MongoDB data
        $script = @"
            db.users.countDocuments();
            db.chat_sessions.countDocuments();
            db.messages.countDocuments();
"@
        docker exec health_assistant_mongodb mongosh health_assistant --eval $script
    }

    Write-Info "Migration verification completed!"
}

# Stop databases
function Stop-Databases {
    Write-Step "Stopping database services..."
    docker-compose -f docker-compose.db.yml down
    Write-Info "Database services stopped!"
}

# Check if Docker is running
function Test-Docker {
    try {
        $null = docker version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Docker is not running. Please start Docker Desktop first."
            exit 1
        }
        Write-Info "Docker is running."
    }
    catch {
        Write-Error "Docker is not installed or not running. Please install Docker Desktop."
        exit 1
    }
}

# Main execution
function Main {
    # Check Docker
    Test-Docker

    switch ($Action) {
        "backup" {
            Create-Directories
            Backup-JsonData
        }
        "setup" {
            Create-Directories
            Start-Databases $DatabaseType
            if ($DatabaseType -eq "postgresql") {
                Setup-PostgreSQL
            } else {
                Setup-MongoDB
            }
        }
        "migrate" {
            Create-Directories
            Backup-JsonData
            Start-Databases $DatabaseType
            if ($DatabaseType -eq "postgresql") {
                Setup-PostgreSQL
                Run-PostgreSQLMigration
            } else {
                Setup-MongoDB
                Run-MongoDBMigration
            }
            Update-Environment $DatabaseType
            Verify-Migration $DatabaseType
        }
        "verify" {
            Verify-Migration $DatabaseType
        }
        "stop" {
            Stop-Databases
        }
        default {
            Write-Error "Invalid action: $Action"
            Write-Host "Valid actions: backup, setup, migrate, verify, stop"
            exit 1
        }
    }
}

# Execute main function
try {
    Main
    Write-Info "Database migration script completed successfully!"
}
catch {
    Write-Error "Script failed: $_"
    exit 1
}