# Enterprise AI Integration Demo Guide

## Pre-Demo Preparation

### System Requirements Verification
Run the installation verification script before any demo:
```bash
./verify-installation.sh
```

Ensure all components show "PASS" status before proceeding with the demonstration.

### API Key Configuration
1. Obtain Anthropic API key from [Anthropic Console](https://console.anthropic.com/)
2. Configure the key in `backend/.env`:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

### Demo Environment Setup
1. **Backend Server**: Ensure backend is running on port 8000
2. **Frontend Server**: Ensure frontend is running on port 5173
3. **Network Access**: Verify demo environment has internet access for API calls
4. **Browser Requirements**: Use Chrome, Firefox, or Safari with WebSocket support

## Demo Scenarios

### Primary Demo: Procurement Workflow

**Objective**: Demonstrate AI-to-AI integration for enterprise procurement processes

**Duration**: 5-7 minutes

**Setup**:
1. Start both backend and frontend servers
2. Open browser to http://localhost:5173
3. Verify WebSocket connection is established (green status indicator)

**Demo Flow**:

1. **Introduction** (30 seconds)
   - Explain the business scenario: Corporate procurement request
   - Show the user input field with pre-filled example
   - Highlight the enterprise-grade security and compliance features

2. **User Input** (30 seconds)
   - Use the default input: "Order 500 units of SKU-1234 from our supplier"
   - Click "Start Demo" button
   - Point out the real-time status updates

3. **AI Analysis Phase** (60 seconds)
   - Show Corporate AI analyzing the request
   - Highlight the determination of external data requirements
   - Explain the business logic and validation process

4. **Authentication Handshake** (90 seconds)
   - Demonstrate the secure AI-to-AI authentication protocol
   - Show the session token generation and validation
   - Highlight enterprise security standards

5. **Data Exchange** (90 seconds)
   - Show ERP AI processing the request
   - Demonstrate real-time supplier data retrieval
   - Highlight pricing calculations and availability checks

6. **Business Outcome** (60 seconds)
   - Show the generated purchase order
   - Display supplier confirmation and delivery schedule
   - Review the complete audit trail and compliance logging

**Key Talking Points**:
- Real-time AI communication protocols
- Enterprise security and authentication
- Business process automation
- Compliance and audit requirements
- Scalability and integration capabilities

### Secondary Demo: Error Handling

**Objective**: Demonstrate system resilience and error recovery

**Duration**: 3-4 minutes

**Setup**: Use invalid or malformed input to trigger error scenarios

**Demo Flow**:
1. Input invalid data: "Invalid request format"
2. Show error detection and handling
3. Demonstrate graceful degradation
4. Highlight error logging and audit trail

### Technical Deep Dive Demo

**Objective**: Show technical implementation details for engineering audience

**Duration**: 10-15 minutes

**Setup**: Have browser developer tools open, backend logs visible

**Demo Flow**:
1. **Architecture Overview**
   - FastAPI backend with WebSocket support
   - React frontend with real-time updates
   - AI agent orchestration system

2. **API Documentation**
   - Show FastAPI automatic documentation at http://localhost:8000/docs
   - Demonstrate REST endpoints and WebSocket connections
   - Review request/response schemas

3. **Code Walkthrough**
   - Backend AI agent implementation
   - Frontend real-time communication
   - Security and authentication protocols

4. **Monitoring and Logging**
   - Show audit trail implementation
   - Demonstrate error handling and recovery
   - Review performance metrics

## Demo Environment Management

### Starting the Demo
```bash
# Automated startup (recommended)
./start-demo.sh

# Manual startup
# Terminal 1
cd backend && source venv/bin/activate && python main.py

# Terminal 2  
cd frontend && npm run dev
```

### Stopping the Demo
```bash
# Stop all processes
pkill -f "python main.py"
pkill -f "npm run dev"

# Or use Ctrl+C in each terminal
```

### Demo Data Reset
- Refresh the browser page to reset the UI state
- Each demo run creates a new session with unique identifiers
- No persistent data storage in demo mode

## Troubleshooting Common Demo Issues

### Backend Connection Failed
**Symptoms**: Frontend shows connection error, no WebSocket connection
**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check port 8000 is not in use: `lsof -i :8000`
3. Restart backend server

### Frontend Not Loading
**Symptoms**: Browser shows connection refused or blank page
**Solutions**:
1. Verify frontend is running: `curl http://localhost:5173`
2. Check Node.js installation: `node --version`
3. Reinstall dependencies: `cd frontend && rm -rf node_modules && npm install`

### AI Agent Errors
**Symptoms**: Demo stops at AI processing stage, error messages
**Solutions**:
1. Verify API key is configured: `grep ANTHROPIC_API_KEY backend/.env`
2. Check API key is valid and has sufficient credits
3. Verify internet connectivity for API calls

### WebSocket Connection Issues
**Symptoms**: Real-time updates not working, status stuck
**Solutions**:
1. Check browser console for WebSocket errors
2. Verify CORS configuration in backend
3. Try different browser or incognito mode

## Demo Customization

### Modifying Demo Scenarios
1. **Change Default Input**: Edit the default text in `frontend/src/components/Dashboard.tsx`
2. **Add New Scenarios**: Extend the AI agent logic in `backend/agents/`
3. **Customize UI**: Modify components in `frontend/src/components/`

### Adding Business Logic
1. **Extend Corp AI**: Add new business rules in `backend/agents/corp_ai.py`
2. **Enhance ERP AI**: Add new data sources in `backend/agents/erp_ai.py`
3. **Update Orchestrator**: Modify workflow logic in `backend/agents/orchestrator.py`

### Styling and Branding
1. **Update Colors**: Modify `frontend/tailwind.config.js`
2. **Change Logo/Branding**: Update `frontend/src/App.tsx`
3. **Custom Themes**: Extend CSS in `frontend/src/index.css`

## Post-Demo Follow-up

### Technical Questions
Be prepared to discuss:
- Scalability and performance characteristics
- Security and compliance implementations
- Integration with existing enterprise systems
- Customization and extension capabilities

### Business Value Discussion
Highlight:
- Reduced manual processing time
- Improved accuracy and compliance
- Real-time business intelligence
- Cost savings and efficiency gains

### Next Steps
Provide:
- Technical documentation and API references
- Integration planning and timeline
- Security and compliance review process
- Pilot program and testing recommendations

## Demo Metrics and Success Criteria

### Technical Metrics
- Response time for AI processing
- WebSocket connection stability
- Error rate and recovery time
- System resource utilization

### Business Metrics
- Process completion time
- Accuracy of business outcomes
- Compliance audit trail completeness
- User experience and interface usability

### Demo Success Indicators
- Smooth real-time AI communication flow
- Complete business process automation
- Professional UI and user experience
- Comprehensive audit and compliance logging
- Technical architecture demonstration

---

**Note**: This demo platform is designed for evaluation and proof-of-concept purposes. For production deployment, additional security, scalability, and compliance measures would be required.
