# AI Health Assistant Docker Deployment Script for Windows PowerShell
# This script helps deploy the application using Docker Compose

param(
    [string]$Action = "menu"
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

# Check if Docker is installed
function Test-Docker {
    try {
        $null = Get-Command docker -ErrorAction Stop
        $null = Get-Command docker-compose -ErrorAction Stop

        # Test Docker is running
        docker version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Docker is not running. Please start Docker Desktop."
            exit 1
        }

        Write-Info "Docker and Docker Compose are installed and running."
        return $true
    }
    catch {
        Write-Error "Docker or Docker Compose is not installed or not running."
        Write-Error "Please install Docker Desktop for Windows: https://www.docker.com/products/docker-desktop"
        exit 1
    }
}

# Check if .env file exists
function Test-EnvFile {
    if (-not (Test-Path .env)) {
        Write-Warning ".env file not found. Creating from .env.example..."
        Copy-Item .env.example .env
        Write-Warning "Please edit .env file with your configuration before continuing."
        Write-Warning "Especially set your HF_TOKEN (Hugging Face token)."
        Write-Host "Press Enter after editing .env file..."
        $null = Read-Host
    }
    else {
        Write-Info ".env file found."
    }
}

# Build and start services
function Deploy-Application {
    Write-Info "Building and starting services..."

    # Stop any existing containers
    Write-Info "Stopping existing containers..."
    docker-compose down --remove-orphans

    # Build new images
    Write-Info "Building Docker images..."
    docker-compose build --no-cache

    # Start services
    Write-Info "Starting services..."
    docker-compose up -d

    Write-Info "Waiting for services to be ready..."
    Start-Sleep -Seconds 30

    # Check service health
    Test-Services

    Write-Info "Deployment completed successfully!"
    Write-Info "Frontend: http://localhost:3000"
    Write-Info "Backend API: http://localhost:8000"
    Write-Info "API Documentation: http://localhost:8000/docs"
}

# Check service health
function Test-Services {
    Write-Info "Checking service health..."

    # Check backend health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Info "✓ Backend is healthy"
        }
    }
    catch {
        Write-Error "✗ Backend health check failed"
        docker-compose logs backend
        exit 1
    }

    # Check frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Info "✓ Frontend is running"
        }
    }
    catch {
        Write-Warning "Frontend might still be starting up..."
    }
}

# Show logs
function Show-Logs {
    Write-Info "Showing logs..."
    docker-compose logs -f
}

# Stop services
function Stop-Services {
    Write-Info "Stopping services..."
    docker-compose down
    Write-Info "Services stopped."
}

# Clean up
function Clean-All {
    $response = Read-Host "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    if ($response -match '^[yY]([eE][sS])?$') {
        Write-Info "Cleaning up Docker resources..."
        docker-compose down -v --rmi all
        docker system prune -f
        Write-Info "Cleanup completed."
    }
    else {
        Write-Info "Cleanup cancelled."
    }
}

# Update dependencies
function Update-Dependencies {
    Write-Info "Updating dependencies..."

    # Update backend dependencies
    Write-Info "Updating Python dependencies..."
    docker-compose exec backend pip install --upgrade -r requirements.txt

    # Update frontend dependencies
    Write-Info "Updating Node.js dependencies..."
    docker-compose exec frontend npm update

    Write-Info "Dependencies updated."
}

# Main menu
function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Info "AI Health Assistant Docker Deployment"
    Write-Host "1) Deploy application"
    Write-Host "2) Show logs"
    Write-Host "3) Stop services"
    Write-Host "4) Clean up (remove everything)"
    Write-Host "5) Update dependencies"
    Write-Host "6) Exit"
    Write-Host ""

    $choice = Read-Host "Choose an option (1-6)"

    switch ($choice) {
        "1" {
            Test-Docker
            Test-EnvFile
            Deploy-Application
            Show-Menu
        }
        "2" {
            Show-Logs
            Show-Menu
        }
        "3" {
            Stop-Services
            Show-Menu
        }
        "4" {
            Clean-All
            Show-Menu
        }
        "5" {
            Update-Dependencies
            Show-Menu
        }
        "6" {
            Write-Info "Goodbye!"
            exit 0
        }
        default {
            Write-Error "Invalid option. Please choose 1-6."
            Show-Menu
        }
    }
}

# Main execution
switch ($Action.ToLower()) {
    "deploy" {
        Test-Docker
        Test-EnvFile
        Deploy-Application
    }
    "stop" {
        Stop-Services
    }
    "logs" {
        Show-Logs
    }
    "clean" {
        Clean-All
    }
    "update" {
        Update-Dependencies
    }
    "menu" {
        Show-Menu
    }
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "Usage: .\deploy.ps1 [deploy|stop|logs|clean|update|menu]"
        exit 1
    }
}