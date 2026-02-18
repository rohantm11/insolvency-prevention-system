#!/bin/bash

# =============================================================================
# Insolvency Prevention System - Deployment Script
# =============================================================================
# Usage:
#   ./deploy.sh [command] [options]
#
# Commands:
#   dev       - Start development environment with hot-reload
#   prod      - Start production environment
#   build     - Build Docker images
#   stop      - Stop all containers
#   restart   - Restart all containers
#   logs      - View container logs
#   status    - Show container status
#   clean     - Remove containers and images
#   backup    - Backup data directory
#   health    - Check system health
#
# Examples:
#   ./deploy.sh dev              # Start development
#   ./deploy.sh prod             # Start production
#   ./deploy.sh logs backend     # View backend logs
#   ./deploy.sh clean --all      # Remove everything
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="insolvency-prevention-system"
COMPOSE_DEV="docker-compose.dev.yml"
COMPOSE_PROD="docker-compose.prod.yml"
COMPOSE_DEFAULT="docker-compose.yml"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "Created .env file. Please review and update settings."
        else
            log_error ".env.example not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Development environment
cmd_dev() {
    log_info "Starting development environment..."
    check_docker
    docker-compose -f $COMPOSE_DEV up --build "${@}"
}

# Production environment
cmd_prod() {
    log_info "Starting production environment..."
    check_docker
    check_env
    docker-compose -f $COMPOSE_PROD up -d --build "${@}"
    log_success "Production environment started!"
    echo ""
    log_info "Services:"
    echo "  - Frontend: http://localhost:${FRONTEND_PORT:-80}"
    echo "  - Backend API: http://localhost:${BACKEND_PORT:-8000}"
    echo "  - API Docs: http://localhost:${BACKEND_PORT:-8000}/docs"
}

# Build images
cmd_build() {
    log_info "Building Docker images..."
    check_docker

    local tag="${1:-latest}"

    log_info "Building backend image..."
    docker build -t insolvency-backend:$tag ./backend

    log_info "Building frontend image..."
    docker build -t insolvency-frontend:$tag ./frontend --build-arg VITE_API_URL=/api

    log_success "Images built successfully!"
    docker images | grep insolvency
}

# Stop containers
cmd_stop() {
    log_info "Stopping containers..."
    check_docker

    docker-compose -f $COMPOSE_DEV down 2>/dev/null || true
    docker-compose -f $COMPOSE_PROD down 2>/dev/null || true
    docker-compose -f $COMPOSE_DEFAULT down 2>/dev/null || true

    log_success "All containers stopped."
}

# Restart containers
cmd_restart() {
    log_info "Restarting containers..."
    cmd_stop

    if [ "$1" == "dev" ]; then
        cmd_dev -d
    else
        cmd_prod
    fi
}

# View logs
cmd_logs() {
    check_docker
    local service="${1:-}"
    local compose_file="${2:-$COMPOSE_PROD}"

    if [ -z "$service" ]; then
        docker-compose -f $compose_file logs -f --tail=100
    else
        docker-compose -f $compose_file logs -f --tail=100 $service
    fi
}

# Show status
cmd_status() {
    log_info "Container Status:"
    echo ""
    docker ps -a --filter "name=insolvency" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    log_info "Images:"
    docker images | grep insolvency || echo "No images found"
    echo ""

    log_info "Volumes:"
    docker volume ls | grep insolvency || echo "No volumes found"
}

# Clean up
cmd_clean() {
    log_warning "This will remove containers, images, and volumes."

    if [ "$1" != "--force" ] && [ "$1" != "-f" ]; then
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Cancelled."
            exit 0
        fi
    fi

    log_info "Stopping containers..."
    cmd_stop

    log_info "Removing images..."
    docker rmi insolvency-backend insolvency-frontend 2>/dev/null || true
    docker rmi $(docker images -q --filter "reference=insolvency-*") 2>/dev/null || true

    if [ "$1" == "--all" ]; then
        log_info "Removing volumes..."
        docker volume rm $(docker volume ls -q --filter "name=insolvency") 2>/dev/null || true

        log_info "Pruning system..."
        docker system prune -f
    fi

    log_success "Cleanup complete."
}

# Backup data
cmd_backup() {
    local backup_dir="./backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/backup_${timestamp}.tar.gz"

    mkdir -p $backup_dir

    log_info "Creating backup..."
    tar -czvf $backup_file ./data ./ml_models/trained_models 2>/dev/null || true

    log_success "Backup created: $backup_file"
}

# Health check
cmd_health() {
    log_info "Checking system health..."
    echo ""

    # Check backend
    log_info "Backend API:"
    if curl -s -f "http://localhost:${BACKEND_PORT:-8000}/api/health" > /dev/null 2>&1; then
        local health=$(curl -s "http://localhost:${BACKEND_PORT:-8000}/api/health")
        echo -e "  Status: ${GREEN}Healthy${NC}"
        echo "  Response: $health"
    else
        echo -e "  Status: ${RED}Unhealthy${NC}"
    fi
    echo ""

    # Check frontend
    log_info "Frontend:"
    if curl -s -f "http://localhost:${FRONTEND_PORT:-80}" > /dev/null 2>&1; then
        echo -e "  Status: ${GREEN}Healthy${NC}"
    else
        echo -e "  Status: ${RED}Unhealthy${NC}"
    fi
    echo ""

    # Docker stats
    log_info "Container Resources:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep insolvency || echo "  No running containers"
}

# Show help
cmd_help() {
    echo "Usage: ./deploy.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  dev       Start development environment with hot-reload"
    echo "  prod      Start production environment"
    echo "  build     Build Docker images (optionally specify tag)"
    echo "  stop      Stop all containers"
    echo "  restart   Restart containers (dev|prod)"
    echo "  logs      View logs (optionally specify service: backend|frontend)"
    echo "  status    Show container and image status"
    echo "  clean     Remove containers and images (--all to include volumes)"
    echo "  backup    Create backup of data directory"
    echo "  health    Check system health"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh dev                    # Start development"
    echo "  ./deploy.sh prod                   # Start production"
    echo "  ./deploy.sh build v1.0.0           # Build with specific tag"
    echo "  ./deploy.sh logs backend           # View backend logs"
    echo "  ./deploy.sh clean --all            # Full cleanup"
}

# Main entry point
main() {
    local command="${1:-help}"
    shift || true

    case $command in
        dev)
            cmd_dev "$@"
            ;;
        prod)
            cmd_prod "$@"
            ;;
        build)
            cmd_build "$@"
            ;;
        stop)
            cmd_stop "$@"
            ;;
        restart)
            cmd_restart "$@"
            ;;
        logs)
            cmd_logs "$@"
            ;;
        status)
            cmd_status "$@"
            ;;
        clean)
            cmd_clean "$@"
            ;;
        backup)
            cmd_backup "$@"
            ;;
        health)
            cmd_health "$@"
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            log_error "Unknown command: $command"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
