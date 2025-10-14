#!/bin/bash

# Enterprise AI Integration Platform - Deployment Script
# Supports Docker, Docker Compose, and Kubernetes deployments

set -e

echo "🚀 Enterprise AI Integration Platform Deployment"
echo "================================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "SUCCESS" ]; then
        echo -e "${GREEN}✅${NC} $message"
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}❌${NC} $message"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️${NC} $message"
    else
        echo -e "${BLUE}ℹ️${NC} $message"
    fi
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_status "ERROR" "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "SUCCESS" "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_status "ERROR" "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_status "SUCCESS" "Docker Compose is installed"
}

# Create environment file if it doesn't exist
setup_environment() {
    if [ ! -f .env ]; then
        print_status "INFO" "Creating .env file from template"
        cp .env.example .env
        print_status "WARNING" "Please edit .env file with your API keys before deployment"
    else
        print_status "SUCCESS" ".env file exists"
    fi
}

# Deploy with Docker Compose
deploy_docker_compose() {
    print_status "INFO" "Deploying with Docker Compose..."
    
    # Build and start services
    docker-compose up --build -d
    
    print_status "SUCCESS" "Services started successfully"
    print_status "INFO" "Application available at: http://localhost"
    print_status "INFO" "API available at: http://localhost:8000"
    print_status "INFO" "Health check: http://localhost/api/health"
}

# Deploy with Docker (single container)
deploy_docker() {
    print_status "INFO" "Deploying with Docker..."
    
    # Build the image
    docker build -t enterprise-ai-platform .
    
    # Run the container
    docker run -d \
        --name enterprise-ai-platform \
        -p 80:80 \
        -p 8000:8000 \
        --env-file .env \
        enterprise-ai-platform
    
    print_status "SUCCESS" "Container started successfully"
    print_status "INFO" "Application available at: http://localhost"
    print_status "INFO" "API available at: http://localhost:8000"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    print_status "INFO" "Deploying to Kubernetes..."
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        print_status "ERROR" "kubectl is not installed"
        exit 1
    fi
    
    # Create namespace
    kubectl create namespace enterprise-ai --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply configurations
    kubectl apply -f k8s/ -n enterprise-ai
    
    print_status "SUCCESS" "Kubernetes deployment completed"
    print_status "INFO" "Check deployment status: kubectl get pods -n enterprise-ai"
}

# Health check
health_check() {
    print_status "INFO" "Performing health check..."
    
    # Wait for services to start
    sleep 10
    
    # Check API health
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        print_status "SUCCESS" "API health check passed"
    else
        print_status "ERROR" "API health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost/ > /dev/null 2>&1; then
        print_status "SUCCESS" "Frontend health check passed"
    else
        print_status "ERROR" "Frontend health check failed"
    fi
}

# Show logs
show_logs() {
    print_status "INFO" "Showing application logs..."
    docker-compose logs -f
}

# Stop services
stop_services() {
    print_status "INFO" "Stopping services..."
    docker-compose down
    print_status "SUCCESS" "Services stopped"
}

# Clean up
cleanup() {
    print_status "INFO" "Cleaning up..."
    docker-compose down -v
    docker system prune -f
    print_status "SUCCESS" "Cleanup completed"
}

# Main deployment logic
main() {
    case "${1:-docker-compose}" in
        "docker-compose")
            check_docker
            check_docker_compose
            setup_environment
            deploy_docker_compose
            health_check
            ;;
        "docker")
            check_docker
            setup_environment
            deploy_docker
            health_check
            ;;
        "kubernetes"|"k8s")
            deploy_kubernetes
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop_services
            ;;
        "cleanup")
            cleanup
            ;;
        "health")
            health_check
            ;;
        *)
            echo "Usage: $0 {docker-compose|docker|kubernetes|logs|stop|cleanup|health}"
            echo ""
            echo "Commands:"
            echo "  docker-compose  Deploy with Docker Compose (default)"
            echo "  docker         Deploy with single Docker container"
            echo "  kubernetes     Deploy to Kubernetes"
            echo "  logs           Show application logs"
            echo "  stop           Stop all services"
            echo "  cleanup        Stop services and clean up volumes"
            echo "  health         Perform health check"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
