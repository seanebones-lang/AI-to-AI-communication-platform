#!/bin/bash

# Enterprise AI Integration Platform - Installation Verification Script
# This script validates the complete installation and configuration

set -e

echo "Enterprise AI Integration Platform - Installation Verification"
echo "============================================================="
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
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗${NC} $message"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    else
        echo -e "${BLUE}ℹ${NC} $message"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        local version=$(python3 --version 2>&1 | cut -d' ' -f2)
        local major=$(echo $version | cut -d'.' -f1)
        local minor=$(echo $version | cut -d'.' -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
            print_status "PASS" "Python $version (meets requirement 3.8+)"
            return 0
        else
            print_status "FAIL" "Python $version (requires 3.8+)"
            return 1
        fi
    else
        print_status "FAIL" "Python3 not found"
        return 1
    fi
}

# Function to check Node.js version
check_node_version() {
    if command_exists node; then
        local version=$(node --version | cut -d'v' -f2)
        local major=$(echo $version | cut -d'.' -f1)
        
        if [ "$major" -ge 16 ]; then
            print_status "PASS" "Node.js v$version (meets requirement 16+)"
            return 0
        else
            print_status "FAIL" "Node.js v$version (requires 16+)"
            return 1
        fi
    else
        print_status "WARN" "Node.js not found (frontend will not be available)"
        return 1
    fi
}

# Function to check npm
check_npm() {
    if command_exists npm; then
        local version=$(npm --version)
        print_status "PASS" "npm v$version"
        return 0
    else
        print_status "WARN" "npm not found (frontend setup will fail)"
        return 1
    fi
}

echo "1. System Requirements Check"
echo "-----------------------------"

check_python_version
PYTHON_OK=$?

check_node_version
NODE_OK=$?

check_npm
NPM_OK=$?

echo ""

echo "2. Project Structure Check"
echo "--------------------------"

# Check if we're in the right directory
if [ -d "backend" ] && [ -d "frontend" ] && [ -f "README.md" ]; then
    print_status "PASS" "Project structure is correct"
    STRUCTURE_OK=0
else
    print_status "FAIL" "Project structure is incorrect - missing backend/, frontend/, or README.md"
    STRUCTURE_OK=1
fi

# Check backend files
if [ -f "backend/requirements.txt" ] && [ -f "backend/main.py" ] && [ -f "backend/models.py" ]; then
    print_status "PASS" "Backend core files present"
else
    print_status "FAIL" "Backend core files missing"
    STRUCTURE_OK=1
fi

# Check frontend files
if [ -f "frontend/package.json" ] && [ -f "frontend/vite.config.ts" ] && [ -d "frontend/src" ]; then
    print_status "PASS" "Frontend core files present"
else
    print_status "FAIL" "Frontend core files missing"
    STRUCTURE_OK=1
fi

echo ""

echo "3. Backend Installation Check"
echo "-----------------------------"

if [ $PYTHON_OK -eq 0 ]; then
    cd backend
    
    # Check virtual environment
    if [ -d "venv" ]; then
        print_status "PASS" "Python virtual environment exists"
        
        # Activate and test
        source venv/bin/activate
        
        # Check if dependencies are installed
        if python3 -c "import fastapi, anthropic, pydantic" 2>/dev/null; then
            print_status "PASS" "Backend dependencies installed"
        else
            print_status "FAIL" "Backend dependencies not installed - run: pip install -r requirements.txt"
        fi
        
        # Check environment file
        if [ -f ".env" ]; then
            if grep -q "ANTHROPIC_API_KEY" .env && ! grep -q "your_anthropic_api_key_here" .env; then
                print_status "PASS" "Environment configuration complete"
            else
                print_status "WARN" "Environment configuration incomplete - update .env with your API key"
            fi
        else
            if [ -f ".env.example" ]; then
                print_status "WARN" "Environment file missing - copy .env.example to .env and configure"
            else
                print_status "FAIL" "Environment configuration files missing"
            fi
        fi
        
        # Test imports
        if python3 -c "import models, main" 2>/dev/null; then
            print_status "PASS" "Backend modules import successfully"
        else
            print_status "FAIL" "Backend module imports failed"
        fi
        
        deactivate
    else
        print_status "WARN" "Python virtual environment not found - run: python3 -m venv venv"
    fi
    
    cd ..
else
    print_status "FAIL" "Backend check skipped - Python not available"
fi

echo ""

echo "4. Frontend Installation Check"
echo "------------------------------"

if [ $NODE_OK -eq 0 ] && [ $NPM_OK -eq 0 ]; then
    cd frontend
    
    # Check if node_modules exists
    if [ -d "node_modules" ]; then
        print_status "PASS" "Frontend dependencies installed"
        
        # Test package.json
        if python3 -c "import json; json.load(open('package.json'))" 2>/dev/null; then
            print_status "PASS" "package.json is valid"
        else
            print_status "FAIL" "package.json is invalid"
        fi
        
        # Test TypeScript config
        if [ -f "tsconfig.json" ]; then
            print_status "PASS" "TypeScript configuration present"
        else
            print_status "FAIL" "TypeScript configuration missing"
        fi
        
        # Test if build works
        if npm run build >/dev/null 2>&1; then
            print_status "PASS" "Frontend builds successfully"
        else
            print_status "WARN" "Frontend build failed - check for errors"
        fi
    else
        print_status "WARN" "Frontend dependencies not installed - run: npm install"
    fi
    
    cd ..
else
    print_status "WARN" "Frontend check skipped - Node.js/npm not available"
fi

echo ""

echo "5. Integration Test"
echo "-------------------"

if [ $PYTHON_OK -eq 0 ] && [ $STRUCTURE_OK -eq 0 ]; then
    cd backend
    source venv/bin/activate
    
    # Test API endpoints
    python3 -c "
from fastapi.testclient import TestClient
from main import app
import sys

try:
    client = TestClient(app)
    
    # Test health endpoint
    response = client.get('/api/health')
    if response.status_code == 200:
        print('✓ Health endpoint: PASS')
    else:
        print('✗ Health endpoint: FAIL')
        sys.exit(1)
    
    # Test conversation endpoint
    response = client.post('/api/start-conversation', json={
        'user_input': 'Test request',
        'request_type': 'procurement'
    })
    if response.status_code == 200:
        print('✓ Conversation endpoint: PASS')
    else:
        print('✗ Conversation endpoint: FAIL')
        sys.exit(1)
        
    print('✓ API endpoints: PASS')
except Exception as e:
    print(f'✗ Integration test: FAIL - {e}')
    sys.exit(1)
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_status "PASS" "Integration tests passed"
    else
        print_status "FAIL" "Integration tests failed"
    fi
    
    deactivate
    cd ..
else
    print_status "WARN" "Integration test skipped - requirements not met"
fi

echo ""

echo "6. Summary"
echo "----------"

# Calculate overall status
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Count checks (simplified)
if [ $PYTHON_OK -eq 0 ]; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

if [ $STRUCTURE_OK -eq 0 ]; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

if [ $NODE_OK -eq 0 ]; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

echo "Installation Status: $PASSED_CHECKS/$TOTAL_CHECKS core requirements met"

if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✓ Installation verification complete - System ready for demo${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure your Anthropic API key in backend/.env"
    echo "2. Run: ./start-demo.sh"
    echo "3. Open: http://localhost:5173"
else
    echo -e "${YELLOW}⚠ Installation incomplete - Please address the issues above${NC}"
    echo ""
    echo "Common fixes:"
    echo "1. Install missing dependencies: pip install -r backend/requirements.txt"
    echo "2. Set up frontend: cd frontend && npm install"
    echo "3. Configure API key: cp backend/.env.example backend/.env"
fi

echo ""
