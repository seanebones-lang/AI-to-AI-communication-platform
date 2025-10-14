#!/usr/bin/env python3
"""
Simple test script to verify the backend is working
"""

import requests
import json
import time

def test_backend():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Enterprise AI Integration Demo Backend")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Start conversation
    print("\n2. Testing conversation start...")
    try:
        response = requests.post(
            f"{base_url}/api/start-conversation",
            json={
                "user_input": "Order 500 units of SKU-1234 from our supplier",
                "request_type": "procurement",
                "priority": "normal"
            }
        )
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Conversation started successfully")
            print(f"   📊 Session ID: {data['session_id']}")
            return data['session_id']
        else:
            print(f"   ❌ Conversation start failed: {response.status_code}")
            print(f"   📊 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Conversation start failed: {e}")
        return False

def main():
    print("🚀 Starting backend test...")
    print("   Make sure the backend is running: cd backend && python main.py")
    print("   Waiting 2 seconds for you to start the backend if needed...\n")
    
    time.sleep(2)
    
    session_id = test_backend()
    
    if session_id:
        print(f"\n✅ Backend is working correctly!")
        print(f"   Session ID: {session_id}")
        print(f"   You can now test the WebSocket connection manually")
        print(f"   WebSocket URL: ws://localhost:8000/ws/{session_id}")
    else:
        print(f"\n❌ Backend test failed!")
        print(f"   Make sure to:")
        print(f"   1. Install dependencies: pip install -r backend/requirements.txt")
        print(f"   2. Set ANTHROPIC_API_KEY in backend/.env")
        print(f"   3. Start backend: cd backend && python main.py")

if __name__ == "__main__":
    main()
