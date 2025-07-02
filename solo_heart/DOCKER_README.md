This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# Docker Setup for Narrative Engine

This document explains how to containerize and run the Narrative Engine backend using Docker.

## 🐳 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

### 1. Environment Setup

First, create your environment file:

```bash
# Copy the template
cp .env.template .env

# Edit the file with your actual values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `FLASK_SECRET_KEY`: A secure secret key for Flask sessions
- `FLASK_ENV`: Set to `production` for production use

### 2. Build and Run

#### Option A: Using Docker Utils Script (Recommended)
```bash
# Make the script executable (if not already)
chmod +x docker-utils.sh

# Build and run
./docker-utils.sh run

# Or use docker-compose
./docker-utils.sh compose
```

#### Option B: Manual Docker Commands
```bash
# Build the image
docker build -t narrative-engine:latest .

# Run the container
docker run -d \
  --name narrative-engine \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd)/campaign_saves:/app/campaign_saves \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  narrative-engine:latest
```

#### Option C: Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Verify Setup

Run the test script to verify everything is working:

```bash
python test_docker_setup.py
```

## 📁 File Structure

```
dnd_game/
├── Dockerfile              # Development Dockerfile
├── Dockerfile.prod         # Production Dockerfile with Gunicorn
├── docker-compose.yml      # Docker Compose configuration
├── docker-utils.sh         # Utility script for Docker operations
├── requirements.txt        # Python dependencies
├── .env.template          # Environment variables template
├── .dockerignore          # Files to exclude from Docker build
├── web_interface.py       # Main Flask application
└── test_docker_setup.py   # Docker setup verification script
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `FLASK_SECRET_KEY` | Flask session secret | - | Yes |
| `FLASK_ENV` | Flask environment | production | No |
| `DEBUG` | Enable debug mode | False | No |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 5001 | No |
| `CAMPAIGN_DATA_PATH` | Campaign data directory | /app/campaign_saves | No |
| `LOG_PATH` | Log directory | /app/logs | No |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3000,http://localhost:5001 | No |

### Volume Mounts

The following directories are mounted as volumes:
- `./campaign_saves` → `/app/campaign_saves` (Campaign data)
- `./logs` → `/app/logs` (Application logs)
- `./data` → `/app/data` (General data)

## 🚀 Production Deployment

### Using Production Dockerfile

For production, use the optimized Dockerfile:

```bash
# Build production image
docker build -f Dockerfile.prod -t narrative-engine:prod .

# Run with production settings
docker run -d \
  --name narrative-engine-prod \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd)/campaign_saves:/app/campaign_saves \
  -v $(pwd)/logs:/app/logs \
  narrative-engine:prod
```

### Production Considerations

1. **Security:**
   - Use strong `FLASK_SECRET_KEY`
   - Set `SESSION_COOKIE_SECURE=True` for HTTPS
   - Use non-root user (already configured)

2. **Performance:**
   - Production Dockerfile uses Gunicorn with multiple workers
   - Configure appropriate worker count based on CPU cores
   - Use reverse proxy (nginx) for SSL termination

3. **Monitoring:**
   - Health checks are configured
   - Logs are available via Docker logs
   - Consider adding monitoring tools

## 🛠️ Development

### Development vs Production

- **Development:** Uses Flask development server
- **Production:** Uses Gunicorn with multiple workers

### Hot Reloading

For development with hot reloading:

```bash
# Run with volume mount for code changes
docker run -d \
  --name narrative-engine-dev \
  -p 5001:5001 \
  --env-file .env \
  -v $(pwd):/app \
  -v $(pwd)/campaign_saves:/app/campaign_saves \
  narrative-engine:latest
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using port 5001
   lsof -i :5001
   
   # Stop existing container
   docker stop narrative-engine
   ```

2. **Environment variables not loaded:**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify environment variables in container
   docker exec narrative-engine env | grep OPENAI
   ```

3. **Permission issues:**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER campaign_saves logs data
   ```

### Useful Commands

```bash
# View container logs
docker logs -f narrative-engine

# Access container shell
docker exec -it narrative-engine /bin/bash

# Check container health
docker inspect narrative-engine | grep Health -A 10

# Clean up Docker resources
./docker-utils.sh cleanup
```

## 📊 Health Monitoring

The container includes health checks:

```bash
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Manual health check
curl http://localhost:5001/api/health
```

## 🔐 Security Best Practices

1. **Never commit .env files** - They're already in .gitignore
2. **Use secrets management** in production (Docker Secrets, Kubernetes Secrets)
3. **Regular security updates** - Keep base images updated
4. **Network security** - Use Docker networks and firewalls
5. **Resource limits** - Set memory and CPU limits in production

## 📝 Logs

Logs are available in multiple ways:

```bash
# Docker logs
docker logs narrative-engine

# Application logs (if mounted)
tail -f logs/app.log

# Docker Compose logs
docker-compose logs -f
```

## 🎯 Next Steps

1. Set up your `.env` file with actual values
2. Build and run the container
3. Test the setup with `python test_docker_setup.py`
4. Access the application at http://localhost:5001
5. Consider production deployment options
