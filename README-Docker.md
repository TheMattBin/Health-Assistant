# Docker Deployment Guide

This guide explains how to deploy the AI Health Assistant using Docker and Docker Compose.

## Prerequisites

1. **Docker Desktop** (for Windows/Mac) or **Docker Engine** (for Linux)
   - Download from: https://www.docker.com/products/docker-desktop

2. **Hugging Face Token** (required for MedGemma AI model)
   - Get your token from: https://huggingface.co/settings/tokens
   - You need a token with "read" permissions

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Health-Assistant
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration, especially HF_TOKEN
   ```

3. **Run the deployment script:**

   **For Windows (PowerShell):**
   ```powershell
   .\scripts\deploy.ps1 -Action deploy
   ```

   **For Linux/Mac (Bash):**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh deploy
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Deployment Scripts

### PowerShell (Windows)

The `scripts/deploy.ps1` script provides an interactive menu:

```powershell
# Show menu
.\scripts\deploy.ps1

# Direct actions
.\scripts\deploy.ps1 -Action deploy
.\scripts\deploy.ps1 -Action stop
.\scripts\deploy.ps1 -Action logs
.\scripts\deploy.ps1 -Action clean
.\scripts\deploy.ps1 -Action update
```

### Bash (Linux/Mac)

The `scripts/deploy.sh` script provides similar functionality:

```bash
# Make executable
chmod +x scripts/deploy.sh

# Show menu
./scripts/deploy.sh

# Direct actions
./scripts/deploy.sh deploy
./scripts/deploy.sh stop
./scripts/deploy.sh logs
./scripts/deploy.sh clean
./scripts/deploy.sh update
```

## Environment Variables

Create a `.env` file from `.env.example` and configure:

```env
# Required: Hugging Face token for MedGemma model
HF_TOKEN=your_huggingface_token_here

# Backend Configuration
BACKEND_URL=http://localhost:8000
API_SECRET_KEY=your_secret_key_here

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## Docker Compose Files

- **`docker-compose.yml`** - Development configuration with hot reload
- **`docker-compose.prod.yml`** - Production configuration without development volumes

### Development vs Production

**Development (docker-compose.yml):**
- Includes volume mounts for hot reload
- Suitable for development and testing

**Production (docker-compose.prod.yml):**
- No development volumes for better performance
- Includes optional Nginx reverse proxy
- Suitable for production deployment

To use production configuration:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Service Architecture

### Backend Service
- **Base Image:** Python 3.11-slim
- **Port:** 8000
- **Health Check:** `/health` endpoint
- **Persistent Volumes:**
  - `chat_history_db` - Chat history storage
  - `uploads` - File upload storage

### Frontend Service
- **Base Image:** Node.js 18 Alpine
- **Port:** 3000
- **Build:** Multi-stage build for optimized production image
- **Depends on:** Backend service health

## Common Commands

### Manual Docker Commands

```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f
docker-compose logs backend
docker-compose logs frontend

# Stop services
docker-compose down

# Remove everything (including volumes)
docker-compose down -v

# Update dependencies
docker-compose exec backend pip install --upgrade -r requirements.txt
docker-compose exec frontend npm update
```

### Health Checks

```bash
# Check service status
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Make sure ports 3000 and 8000 are not in use
   - Modify ports in docker-compose.yml if needed

2. **Permission errors:**
   - On Linux/Mac, you might need to fix permissions:
   ```bash
   sudo chown -R $USER:$USER ./backend/chat_history_db
   sudo chown -R $USER:$USER ./backend/uploads
   ```

3. **Hugging Face Token errors:**
   - Ensure your HF_TOKEN is valid in .env file
   - Check if the token has proper permissions

4. **Build failures:**
   - Clear Docker cache: `docker system prune -a`
   - Rebuild: `docker-compose build --no-cache`

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f

# Enter container for debugging
docker-compose exec backend sh
docker-compose exec frontend sh
```

## Production Considerations

1. **Security:**
   - Use strong API secrets
   - Enable HTTPS (configure in Nginx)
   - Don't expose backend directly to internet

2. **Performance:**
   - Use docker-compose.prod.yml
   - Consider Redis for session management
   - Use external database instead of file storage

3. **Monitoring:**
   - Add monitoring and logging
   - Set up alerts for health checks
   - Monitor resource usage

4. **Backup:**
   - Regularly backup chat history data
   - Backup uploaded files
   - Document backup and restore procedures

## Next Steps

After successful deployment:

1. Test the application by visiting http://localhost:3000
2. Create an account or use demo credentials
3. Test file upload functionality
4. Verify AI model integration works
5. Set up proper backup procedures
6. Configure monitoring for production use