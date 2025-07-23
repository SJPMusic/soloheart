#!/bin/bash

# Docker utilities for Narrative Engine
# ====================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f .env.template ]; then
            cp .env.template .env
            print_success ".env file created from template"
            print_warning "Please update .env with your actual values before running"
        else
            print_error ".env.template not found"
            exit 1
        fi
    fi
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t narrative-engine:latest .
    print_success "Docker image built successfully"
}

# Function to run the container
run_container() {
    print_status "Running container..."
    docker run -d \
        --name narrative-engine \
        -p 5001:5001 \
        --env-file .env \
        -v $(pwd)/campaign_saves:/app/campaign_saves \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/data:/app/data \
        narrative-engine:latest
    print_success "Container started successfully"
    print_status "Access the application at: http://localhost:5001"
}

# Function to stop the container
stop_container() {
    print_status "Stopping container..."
    docker stop narrative-engine || true
    docker rm narrative-engine || true
    print_success "Container stopped and removed"
}

# Function to view logs
view_logs() {
    print_status "Viewing container logs..."
    docker logs -f narrative-engine
}

# Function to run with docker-compose
run_compose() {
    print_status "Starting with docker-compose..."
    docker-compose up -d
    print_success "Services started successfully"
    print_status "Access the application at: http://localhost:5001"
}

# Function to stop docker-compose
stop_compose() {
    print_status "Stopping docker-compose services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Narrative Engine Docker Utilities"
    echo "================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     - Build the Docker image"
    echo "  run       - Run the container"
    echo "  stop      - Stop the container"
    echo "  logs      - View container logs"
    echo "  compose   - Run with docker-compose"
    echo "  stop-comp - Stop docker-compose services"
    echo "  cleanup   - Clean up Docker resources"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 compose"
}

# Main script logic
case "$1" in
    build)
        check_env_file
        build_image
        ;;
    run)
        check_env_file
        build_image
        run_container
        ;;
    stop)
        stop_container
        ;;
    logs)
        view_logs
        ;;
    compose)
        check_env_file
        run_compose
        ;;
    stop-comp)
        stop_compose
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
