#!/bin/bash

# AI Health Assistant Docker Deployment Script
# This script helps deploy the application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    print_info "Docker and Docker Compose are installed."
}

# Check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before continuing."
        print_warning "Especially set your HF_TOKEN (Hugging Face token)."
        read -p "Press Enter after editing .env file..."
    else
        print_info ".env file found."
    fi
}

# Build and start services
deploy() {
    print_info "Building and starting services..."

    # Stop any existing containers
    print_info "Stopping existing containers..."
    docker-compose down --remove-orphans

    # Build new images
    print_info "Building Docker images..."
    docker-compose build --no-cache

    # Start services
    print_info "Starting services..."
    docker-compose up -d

    print_info "Waiting for services to be ready..."
    sleep 30

    # Check service health
    check_services

    print_info "Deployment completed successfully!"
    print_info "Frontend: http://localhost:3000"
    print_info "Backend API: http://localhost:8000"
    print_info "API Documentation: http://localhost:8000/docs"
}

# Check service health
check_services() {
    print_info "Checking service health..."

    # Check backend health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_info "✓ Backend is healthy"
    else
        print_error "✗ Backend health check failed"
        docker-compose logs backend
        exit 1
    fi

    # Check frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        print_info "✓ Frontend is running"
    else
        print_warning "Frontend might still be starting up..."
    fi
}

# Show logs
show_logs() {
    print_info "Showing logs..."
    docker-compose logs -f
}

# Stop services
stop() {
    print_info "Stopping services..."
    docker-compose down
    print_info "Services stopped."
}

# Clean up
clean() {
    print_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Cleaning up Docker resources..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_info "Cleanup completed."
    else
        print_info "Cleanup cancelled."
    fi
}

# Update dependencies
update() {
    print_info "Updating dependencies..."

    # Update backend dependencies
    print_info "Updating Python dependencies..."
    docker-compose exec backend pip install --upgrade -r requirements.txt

    # Update frontend dependencies
    print_info "Updating Node.js dependencies..."
    docker-compose exec frontend npm update

    print_info "Dependencies updated."
}

# Main menu
main_menu() {
    echo ""
    print_info "AI Health Assistant Docker Deployment"
    echo "1) Deploy application"
    echo "2) Show logs"
    echo "3) Stop services"
    echo "4) Clean up (remove everything)"
    echo "5) Update dependencies"
    echo "6) Exit"
    echo ""

    read -p "Choose an option (1-6): " choice

    case $choice in
        1)
            check_docker
            check_env_file
            deploy
            main_menu
            ;;
        2)
            show_logs
            main_menu
            ;;
        3)
            stop
            main_menu
            ;;
        4)
            clean
            main_menu
            ;;
        5)
            update
            main_menu
            ;;
        6)
            print_info "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please choose 1-6."
            main_menu
            ;;
    esac
}

# Start script
if [ "$1" = "deploy" ]; then
    check_docker
    check_env_file
    deploy
elif [ "$1" = "stop" ]; then
    stop
elif [ "$1" = "logs" ]; then
    show_logs
elif [ "$1" = "clean" ]; then
    clean
elif [ "$1" = "update" ]; then
    update
else
    main_menu
fi