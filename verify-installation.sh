#!/bin/bash

# Enterprise AI Integration Platform - Installation Verification Script
# This script verifies the complete installation and configuration of the Enterprise AI Integration Platform

set -e

echo "================================================================"
echo "ENTERPRISE AI INTEGRATION PLATFORM - INSTALLATION VERIFICATION"
echo "================================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}[PASS]${NC} $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}[FAIL]${NC} $message"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}[WARN]${NC} $message"
    elif [ "$status" = "INFO" ]; then
        echo -e "${BLUE}[INFO]${NC} $message"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is open
check_port() {
    local port=$1
    if command_exists nc; then
        nc -z localhost "$port" 2>/dev/null
    elif command_exists telnet; then
        timeout 3 telnet localhost "$port" 2>/dev/null | grep -q "Connected"
    else
        return 1
    fi
}

# Function to check if service is running
check_service() {
    local service=$1
    if command_exists systemctl; then
        systemctl is-active --quiet "$service" 2>/dev/null
    elif command_exists service; then
        service "$service" status >/dev/null 2>&1
    else
        return 1
    fi
}

echo "VERIFICATION STARTED: $(date)"
echo ""

# Check system requirements
echo "SYSTEM REQUIREMENTS VERIFICATION"
echo "================================"

# Check operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "PASS" "Operating System: Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "PASS" "Operating System: macOS detected"
else
    print_status "WARN" "Operating System: $OSTYPE (may not be fully supported)"
fi

# Check available memory
if command_exists free; then
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$MEMORY_GB" -ge 8 ]; then
        print_status "PASS" "Memory: ${MEMORY_GB}GB available (minimum 8GB required)"
    else
        print_status "WARN" "Memory: ${MEMORY_GB}GB available (minimum 8GB recommended)"
    fi
else
    print_status "INFO" "Memory check skipped (free command not available)"
fi

# Check available disk space
if command_exists df; then
    DISK_GB=$(df -BG . | awk 'NR==2{gsub(/[^0-9]/,"",$4); print $4}')
    if [ "$DISK_GB" -ge 50 ]; then
        print_status "PASS" "Disk Space: ${DISK_GB}GB available (minimum 50GB required)"
    else
        print_status "WARN" "Disk Space: ${DISK_GB}GB available (minimum 50GB recommended)"
    fi
else
    print_status "INFO" "Disk space check skipped (df command not available)"
fi

echo ""

# Check required software
echo "REQUIRED SOFTWARE VERIFICATION"
echo "=============================="

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "PASS" "Python: Version $PYTHON_VERSION installed"
else
    print_status "FAIL" "Python: Python 3 not found"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version 2>&1 | cut -d'v' -f2)
    print_status "PASS" "Node.js: Version $NODE_VERSION installed"
else
    print_status "FAIL" "Node.js: Node.js not found"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version 2>&1)
    print_status "PASS" "npm: Version $NPM_VERSION installed"
else
    print_status "FAIL" "npm: npm not found"
    exit 1
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version 2>&1 | cut -d' ' -f3 | cut -d',' -f1)
    print_status "PASS" "Docker: Version $DOCKER_VERSION installed"
else
    print_status "FAIL" "Docker: Docker not found"
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version 2>&1 | cut -d' ' -f3 | cut -d',' -f1)
    print_status "PASS" "Docker Compose: Version $COMPOSE_VERSION installed"
else
    print_status "FAIL" "Docker Compose: Docker Compose not found"
    exit 1
fi

# Check Git
if command_exists git; then
    GIT_VERSION=$(git --version 2>&1 | cut -d' ' -f3)
    print_status "PASS" "Git: Version $GIT_VERSION installed"
else
    print_status "FAIL" "Git: Git not found"
    exit 1
fi

echo ""

# Check project structure
echo "PROJECT STRUCTURE VERIFICATION"
echo "=============================="

# Check if we're in the right directory
if [ -f "README.md" ] && [ -d "backend" ] && [ -d "frontend" ]; then
    print_status "PASS" "Project Structure: Enterprise AI Integration Platform detected"
else
    print_status "FAIL" "Project Structure: Not in the correct project directory"
    exit 1
fi

# Check backend structure
if [ -d "backend" ]; then
    if [ -f "backend/main.py" ] || [ -f "backend/ibm_scale_main.py" ]; then
        print_status "PASS" "Backend: Main application file found"
    else
        print_status "FAIL" "Backend: Main application file not found"
    fi
    
    if [ -f "backend/requirements.txt" ]; then
        print_status "PASS" "Backend: Requirements file found"
    else
        print_status "FAIL" "Backend: Requirements file not found"
    fi
    
    if [ -d "backend/agents" ]; then
        print_status "PASS" "Backend: AI agents directory found"
    else
        print_status "FAIL" "Backend: AI agents directory not found"
    fi
    
    if [ -d "backend/enterprise" ]; then
        print_status "PASS" "Backend: Enterprise features directory found"
    else
        print_status "FAIL" "Backend: Enterprise features directory not found"
    fi
else
    print_status "FAIL" "Backend: Backend directory not found"
fi

# Check frontend structure
if [ -d "frontend" ]; then
    if [ -f "frontend/package.json" ]; then
        print_status "PASS" "Frontend: Package.json found"
    else
        print_status "FAIL" "Frontend: Package.json not found"
    fi
    
    if [ -d "frontend/src" ]; then
        print_status "PASS" "Frontend: Source directory found"
    else
        print_status "FAIL" "Frontend: Source directory not found"
    fi
else
    print_status "FAIL" "Frontend: Frontend directory not found"
fi

# Check Docker configuration
if [ -f "Dockerfile" ]; then
    print_status "PASS" "Docker: Dockerfile found"
else
    print_status "FAIL" "Docker: Dockerfile not found"
fi

if [ -f "docker-compose.yml" ]; then
    print_status "PASS" "Docker: Docker Compose file found"
else
    print_status "FAIL" "Docker: Docker Compose file not found"
fi

echo ""

# Check environment configuration
echo "ENVIRONMENT CONFIGURATION VERIFICATION"
echo "======================================"

# Check environment file
if [ -f ".env" ]; then
    print_status "PASS" "Environment: .env file found"
    
    # Check for required environment variables
    if grep -q "ANTHROPIC_API_KEY" .env; then
        print_status "PASS" "Environment: Anthropic API key configured"
    else
        print_status "WARN" "Environment: Anthropic API key not configured"
    fi
    
    if grep -q "OPENAI_API_KEY" .env; then
        print_status "PASS" "Environment: OpenAI API key configured"
    else
        print_status "WARN" "Environment: OpenAI API key not configured"
    fi
    
    if grep -q "GOOGLE_API_KEY" .env; then
        print_status "PASS" "Environment: Google API key configured"
    else
        print_status "WARN" "Environment: Google API key not configured"
    fi
    
    if grep -q "DATABASE_URL" .env; then
        print_status "PASS" "Environment: Database URL configured"
    else
        print_status "WARN" "Environment: Database URL not configured"
    fi
    
    if grep -q "REDIS_URL" .env; then
        print_status "PASS" "Environment: Redis URL configured"
    else
        print_status "WARN" "Environment: Redis URL not configured"
    fi
else
    print_status "WARN" "Environment: .env file not found (copy from .env.example)"
fi

echo ""

# Check Docker services
echo "DOCKER SERVICES VERIFICATION"
echo "============================"

# Check if Docker is running
if docker info >/dev/null 2>&1; then
    print_status "PASS" "Docker: Docker daemon is running"
else
    print_status "FAIL" "Docker: Docker daemon is not running"
    exit 1
fi

# Check if Docker Compose can read the file
if docker-compose config >/dev/null 2>&1; then
    print_status "PASS" "Docker Compose: Configuration file is valid"
else
    print_status "FAIL" "Docker Compose: Configuration file is invalid"
    exit 1
fi

# Check if services can be started
if docker-compose up -d --no-deps backend >/dev/null 2>&1; then
    print_status "PASS" "Docker: Backend service started successfully"
    docker-compose down >/dev/null 2>&1
else
    print_status "WARN" "Docker: Backend service failed to start (check logs)"
fi

if docker-compose up -d --no-deps frontend >/dev/null 2>&1; then
    print_status "PASS" "Docker: Frontend service started successfully"
    docker-compose down >/dev/null 2>&1
else
    print_status "WARN" "Docker: Frontend service failed to start (check logs)"
fi

echo ""

# Check Python dependencies
echo "PYTHON DEPENDENCIES VERIFICATION"
echo "================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "PASS" "Python: Virtual environment found"
    
    # Activate virtual environment and check dependencies
    if command_exists python3; then
        # Check if requirements can be installed
        if python3 -m pip install --dry-run -r backend/requirements.txt >/dev/null 2>&1; then
            print_status "PASS" "Python: Requirements can be installed"
        else
            print_status "WARN" "Python: Some requirements may fail to install"
        fi
    fi
else
    print_status "WARN" "Python: Virtual environment not found (run 'python3 -m venv venv')"
fi

echo ""

# Check Node.js dependencies
echo "NODE.JS DEPENDENCIES VERIFICATION"
echo "================================="

# Check if node_modules exists
if [ -d "frontend/node_modules" ]; then
    print_status "PASS" "Node.js: Dependencies installed"
else
    print_status "WARN" "Node.js: Dependencies not installed (run 'npm install' in frontend directory)"
fi

# Check if package.json is valid
if [ -f "frontend/package.json" ]; then
    if node -e "JSON.parse(require('fs').readFileSync('frontend/package.json', 'utf8'))" >/dev/null 2>&1; then
        print_status "PASS" "Node.js: Package.json is valid"
    else
        print_status "FAIL" "Node.js: Package.json is invalid"
    fi
fi

echo ""

# Check enterprise features
echo "ENTERPRISE FEATURES VERIFICATION"
echo "==============================="

# Check multi-tenant platform
if [ -d "backend/enterprise/multi_tenant" ]; then
    print_status "PASS" "Enterprise: Multi-tenant platform found"
else
    print_status "WARN" "Enterprise: Multi-tenant platform not found"
fi

# Check global infrastructure
if [ -d "backend/enterprise/global_infrastructure" ]; then
    print_status "PASS" "Enterprise: Global infrastructure management found"
else
    print_status "WARN" "Enterprise: Global infrastructure management not found"
fi

# Check compliance framework
if [ -d "backend/enterprise/compliance" ]; then
    print_status "PASS" "Enterprise: Compliance framework found"
else
    print_status "WARN" "Enterprise: Compliance framework not found"
fi

# Check security architecture
if [ -d "backend/agents/security" ]; then
    print_status "PASS" "Enterprise: Security architecture found"
else
    print_status "WARN" "Enterprise: Security architecture not found"
fi

# Check vector database integration
if [ -d "backend/agents/vector_db" ]; then
    print_status "PASS" "Enterprise: Vector database integration found"
else
    print_status "WARN" "Enterprise: Vector database integration not found"
fi

# Check AI observability
if [ -d "backend/agents/observability" ]; then
    print_status "PASS" "Enterprise: AI observability found"
else
    print_status "WARN" "Enterprise: AI observability not found"
fi

# Check semantic caching
if [ -d "backend/agents/caching" ]; then
    print_status "PASS" "Enterprise: Semantic caching found"
else
    print_status "WARN" "Enterprise: Semantic caching not found"
fi

# Check streaming AI
if [ -d "backend/agents/streaming" ]; then
    print_status "PASS" "Enterprise: Streaming AI found"
else
    print_status "WARN" "Enterprise: Streaming AI not found"
fi

echo ""

# Check documentation
echo "DOCUMENTATION VERIFICATION"
echo "=========================="

# Check main documentation files
if [ -f "README.md" ]; then
    print_status "PASS" "Documentation: README.md found"
else
    print_status "FAIL" "Documentation: README.md not found"
fi

if [ -f "TECHNICAL_ARCHITECTURE.md" ]; then
    print_status "PASS" "Documentation: Technical architecture documentation found"
else
    print_status "WARN" "Documentation: Technical architecture documentation not found"
fi

if [ -f "DEMO_GUIDE.md" ]; then
    print_status "PASS" "Documentation: Demo guide found"
else
    print_status "WARN" "Documentation: Demo guide not found"
fi

if [ -f "SETUP_COMPLETE.md" ]; then
    print_status "PASS" "Documentation: Setup completion documentation found"
else
    print_status "WARN" "Documentation: Setup completion documentation not found"
fi

if [ -f "LICENSE" ]; then
    print_status "PASS" "Documentation: License file found"
else
    print_status "WARN" "Documentation: License file not found"
fi

echo ""

# Final summary
echo "VERIFICATION SUMMARY"
echo "==================="
echo ""

# Count passes and failures
PASS_COUNT=$(grep -c "\[PASS\]" <<< "$(cat $0)")
FAIL_COUNT=$(grep -c "\[FAIL\]" <<< "$(cat $0)")
WARN_COUNT=$(grep -c "\[WARN\]" <<< "$(cat $0)")

echo "VERIFICATION COMPLETED: $(date)"
echo ""
echo "RESULTS SUMMARY:"
echo "- Passed: $PASS_COUNT checks"
echo "- Failed: $FAIL_COUNT checks"
echo "- Warnings: $WARN_COUNT checks"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    print_status "PASS" "Enterprise AI Integration Platform verification completed successfully"
    echo ""
    echo "NEXT STEPS:"
    echo "1. Configure API keys in .env file"
    echo "2. Run 'docker-compose up -d' to start the platform"
    echo "3. Access the platform at http://localhost:8000"
    echo "4. Review documentation for deployment options"
    echo ""
    echo "PLATFORM STATUS: READY FOR ENTERPRISE DEPLOYMENT"
else
    print_status "FAIL" "Enterprise AI Integration Platform verification failed"
    echo ""
    echo "Please address the failed checks before proceeding with deployment."
    exit 1
fi

echo "================================================================"
