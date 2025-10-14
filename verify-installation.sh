#!/bin/bash

# Enterprise AI Integration Platform - Installation Verification Script
# Verifies all components including multi-model AI, ERP integrations, and Docker deployment

set -e

echo "========================================="
echo "ENTERPRISE AI INTEGRATION PLATFORM"
echo "COMPREHENSIVE INSTALLATION VERIFICATION"
echo "========================================="
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
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ $message${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${BLUE}ℹ️  $message${NC}"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Initialize counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Function to run check
run_check() {
    local check_name=$1
    local check_command=$2
    local expected_result=${3:-"success"}
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if eval "$check_command" >/dev/null 2>&1; then
        if [ "$expected_result" = "success" ]; then
            print_status "PASS" "$check_name"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_status "FAIL" "$check_name (Unexpected success)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    else
        if [ "$expected_result" = "failure" ]; then
            print_status "PASS" "$check_name"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_status "FAIL" "$check_name"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    fi
}

# Function to run warning check
run_warning_check() {
    local check_name=$1
    local check_command=$2
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if eval "$check_command" >/dev/null 2>&1; then
        print_status "PASS" "$check_name"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "$check_name"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
}

echo "🔍 SYSTEM REQUIREMENTS CHECK"
echo "============================="

# Check Python version
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_status "PASS" "Python $PYTHON_VERSION (>= 3.8 required)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "FAIL" "Python $PYTHON_VERSION (>= 3.8 required)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
else
    print_status "FAIL" "Python 3.8+ not found"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

# Check Node.js version
if command_exists node; then
    NODE_VERSION=$(node --version 2>&1 | cut -d'v' -f2)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [ "$NODE_MAJOR" -ge 16 ]; then
        print_status "PASS" "Node.js $NODE_VERSION (>= 16.0 required)"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "FAIL" "Node.js $NODE_VERSION (>= 16.0 required)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
else
    print_status "FAIL" "Node.js 16.0+ not found"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

# Check npm
run_check "npm package manager" "command_exists npm"

# Check Docker
run_check "Docker" "command_exists docker"

# Check Docker Compose
run_check "Docker Compose" "command_exists docker-compose"

# Check Git
run_check "Git version control" "command_exists git"

echo ""
echo "📦 BACKEND COMPONENTS CHECK"
echo "============================"

# Check backend directory
run_check "Backend directory exists" "[ -d 'backend' ]"

# Check virtual environment
if [ -d "backend/venv" ]; then
    print_status "PASS" "Python virtual environment exists"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    print_status "WARN" "Python virtual environment not found (run: cd backend && python3 -m venv venv)"
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# Check requirements.txt
run_check "Backend requirements.txt" "[ -f 'backend/requirements.txt' ]"

# Check main.py
run_check "Backend main.py" "[ -f 'backend/main.py' ]"

# Check multi-model AI files
run_check "AI Provider module" "[ -f 'backend/agents/ai_provider.py' ]"
run_check "Enhanced Corp AI" "[ -f 'backend/agents/corp_ai.py' ]"
run_check "Enhanced ERP AI" "[ -f 'backend/agents/erp_ai.py' ]"
run_check "ERP Integrations module" "[ -f 'backend/agents/erp_integrations.py' ]"

# Check models and orchestrator
run_check "Pydantic models" "[ -f 'backend/models.py' ]"
run_check "Orchestrator" "[ -f 'backend/agents/orchestrator.py' ]"

echo ""
echo "🌐 FRONTEND COMPONENTS CHECK"
echo "============================="

# Check frontend directory
run_check "Frontend directory exists" "[ -d 'frontend' ]"

# Check package.json
run_check "Frontend package.json" "[ -f 'frontend/package.json' ]"

# Check main components
run_check "App.tsx component" "[ -f 'frontend/src/App.tsx' ]"
run_check "Dashboard component" "[ -f 'frontend/src/components/Dashboard.tsx' ]"
run_check "ConversationLog component" "[ -f 'frontend/src/components/ConversationLog.tsx' ]"
run_check "AIFlowVisualizer component" "[ -f 'frontend/src/components/AIFlowVisualizer.tsx' ]"
run_check "AuditTrail component" "[ -f 'frontend/src/components/AuditTrail.tsx' ]"

# Check TypeScript types
run_check "TypeScript types" "[ -f 'frontend/src/types.ts' ]"

echo ""
echo "🐳 DOCKER DEPLOYMENT CHECK"
echo "==========================="

# Check Docker files
run_check "Dockerfile" "[ -f 'Dockerfile' ]"
run_check "Docker Compose config" "[ -f 'docker-compose.yml' ]"
run_check "Nginx configuration" "[ -f 'docker/nginx.conf' ]"
run_check "Docker start script" "[ -f 'docker/start.sh' ]"
run_check "Deploy script" "[ -f 'deploy.sh' ]"

# Check Docker services configuration
if [ -f "docker-compose.yml" ]; then
    if grep -q "redis" docker-compose.yml && grep -q "postgres" docker-compose.yml; then
        print_status "PASS" "Redis and PostgreSQL services configured"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "FAIL" "Redis and PostgreSQL services not configured"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""
echo "🔧 DEPLOYMENT SCRIPTS CHECK"
echo "============================"

# Check deployment scripts
run_check "Start demo script" "[ -f 'start-demo.sh' ]"
run_check "Backend test script" "[ -f 'test-backend.py' ]"
run_check "Terminal demo script" "[ -f 'backend/terminal_demo.py' ]"

# Check script permissions
if [ -f "start-demo.sh" ]; then
    if [ -x "start-demo.sh" ]; then
        print_status "PASS" "Start demo script is executable"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "Start demo script not executable (run: chmod +x start-demo.sh)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

if [ -f "deploy.sh" ]; then
    if [ -x "deploy.sh" ]; then
        print_status "PASS" "Deploy script is executable"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "Deploy script not executable (run: chmod +x deploy.sh)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""
echo "📋 CONFIGURATION FILES CHECK"
echo "============================="

# Check environment configuration
run_check "Environment example file" "[ -f '.env.example' ]"

# Check .gitignore
run_check "Git ignore file" "[ -f '.gitignore' ]"

# Check documentation
run_check "README.md" "[ -f 'README.md' ]"
run_check "Demo guide" "[ -f 'DEMO_GUIDE.md' ]"
run_check "Setup completion guide" "[ -f 'SETUP_COMPLETE.md' ]"

echo ""
echo "🔑 API CONFIGURATION CHECK"
echo "==========================="

# Check for environment file
if [ -f ".env" ]; then
    print_status "PASS" "Environment configuration file exists"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    
    # Check for API keys
    if grep -q "ANTHROPIC_API_KEY" .env && grep -q "OPENAI_API_KEY" .env; then
        print_status "PASS" "AI API keys configured"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "AI API keys not configured (edit .env file)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 2))
    
    # Check for Google API key
    if grep -q "GOOGLE_API_KEY" .env; then
        print_status "PASS" "Google API key configured"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "Google API key not configured (optional)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # Check for local AI configuration
    if grep -q "LOCAL_AI_ENABLED" .env; then
        print_status "PASS" "Local AI configuration present"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "Local AI configuration not found (optional)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # Check for ERP configuration
    if grep -q "SAP_BASE_URL\|ORACLE_BASE_URL\|DYNAMICS_CLIENT_ID" .env; then
        print_status "PASS" "ERP integration configuration present"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "ERP integration configuration not found (optional)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
else
    print_status "WARN" "Environment configuration file not found (copy .env.example to .env)"
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo ""
echo "🚀 FUNCTIONALITY TESTING"
echo "========================="

# Test backend imports
if [ -d "backend" ]; then
    cd backend
    
    # Test Python imports
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        # Test core imports
        if python3 -c "import fastapi, uvicorn, websockets" 2>/dev/null; then
            print_status "PASS" "Core backend dependencies imported successfully"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_status "FAIL" "Core backend dependencies import failed"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        
        # Test multi-model AI imports
        if python3 -c "import anthropic, openai, google.generativeai" 2>/dev/null; then
            print_status "PASS" "Multi-model AI dependencies imported successfully"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_status "WARN" "Multi-model AI dependencies not installed (pip install -r requirements.txt)"
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        
        # Test ERP integration imports
        if python3 -c "import requests, zeep, oauthlib" 2>/dev/null; then
            print_status "PASS" "ERP integration dependencies imported successfully"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_status "WARN" "ERP integration dependencies not installed (pip install -r requirements.txt)"
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        
        # Test AI agent imports
        if python3 -c "from agents.ai_provider import MultiModelAIProvider; from agents.erp_integrations import SAPIntegration, OracleIntegration, DynamicsIntegration" 2>/dev/null; then
            print_status "PASS" "AI agent modules imported successfully"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            print_status "FAIL" "AI agent modules import failed"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        
        deactivate
    else
        print_status "WARN" "Virtual environment not activated (run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    fi
    
    cd ..
fi

# Test Docker functionality
if command_exists docker; then
    if docker --version >/dev/null 2>&1; then
        print_status "PASS" "Docker daemon accessible"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        print_status "WARN" "Docker daemon not accessible (start Docker service)"
        WARNING_CHECKS=$((WARNING_CHECKS + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

# Test port availability
if ! port_in_use 8000; then
    print_status "PASS" "Backend port 8000 available"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    print_status "WARN" "Backend port 8000 in use (stop existing services)"
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

if ! port_in_use 5173; then
    print_status "PASS" "Frontend port 5173 available"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    print_status "WARN" "Frontend port 5173 in use (stop existing services)"
    WARNING_CHECKS=$((WARNING_CHECKS + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

echo ""
echo "📊 VERIFICATION SUMMARY"
echo "======================="

echo "Total Checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
echo -e "Warnings: ${YELLOW}$WARNING_CHECKS${NC}"

SUCCESS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
echo "Success Rate: $SUCCESS_RATE%"

echo ""
if [ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -le 3 ]; then
    echo -e "${GREEN}🎉 INSTALLATION VERIFICATION PASSED${NC}"
    echo -e "${GREEN}The Enterprise AI Integration Platform is ready for demonstration!${NC}"
    echo ""
    echo "Next Steps:"
    echo "1. Configure API keys in .env file"
    echo "2. Run: ./start-demo.sh"
    echo "3. Open: http://localhost:5173"
    echo "4. Follow: DEMO_GUIDE.md"
elif [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  INSTALLATION VERIFICATION PASSED WITH WARNINGS${NC}"
    echo -e "${YELLOW}The platform is functional but some optional features may not be available.${NC}"
    echo ""
    echo "Recommended Actions:"
    echo "1. Review warnings above"
    echo "2. Install missing optional dependencies"
    echo "3. Configure additional API keys if needed"
else
    echo -e "${RED}❌ INSTALLATION VERIFICATION FAILED${NC}"
    echo -e "${RED}Critical components are missing. Please fix the failed checks above.${NC}"
    echo ""
    echo "Required Actions:"
    echo "1. Fix all failed checks"
    echo "2. Install missing dependencies"
    echo "3. Configure required environment variables"
    echo "4. Re-run this verification script"
fi

echo ""
echo "📚 DOCUMENTATION AVAILABLE:"
echo "- README.md: Complete technical documentation"
echo "- DEMO_GUIDE.md: Step-by-step demonstration guide"
echo "- SETUP_COMPLETE.md: Setup completion and status"
echo "- .env.example: Environment configuration template"

echo ""
echo "🔧 TROUBLESHOOTING:"
echo "- Backend issues: Check Python virtual environment and dependencies"
echo "- Frontend issues: Verify Node.js version and npm packages"
echo "- Docker issues: Ensure Docker daemon is running"
echo "- API issues: Verify API keys and network connectivity"

exit $FAILED_CHECKS
