#!/usr/bin/env python3
"""
Test script to verify MCP server connectivity
"""
import requests
import json

def test_mcp_endpoint(url="http://localhost:8000"):
    """Test various MCP endpoints"""
    
    print(f"Testing MCP server at {url}")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        resp = requests.get(f"{url}/")
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.text[:200] if resp.text else '(empty)'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: MCP list tools
    print("\n2. Testing MCP tools/list endpoint...")
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    for endpoint in ["/mcp", "/mcp/", "/mcp/messages", "/"]:
        try:
            resp = requests.post(
                f"{url}{endpoint}",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Endpoint {endpoint}: Status {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
                break
        except Exception as e:
            print(f"   Endpoint {endpoint}: Error - {e}")
    
    # Test 3: Check FastMCP-specific endpoints
    print("\n3. Testing FastMCP-specific endpoints...")
    for endpoint in ["/health", "/docs", "/openapi.json", "/mcp/v1/"]:
        try:
            resp = requests.get(f"{url}{endpoint}")
            print(f"   {endpoint}: Status {resp.status_code}")
            if resp.status_code == 200 and len(resp.text) < 200:
                print(f"   Response: {resp.text}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")

if __name__ == "__main__":
    test_mcp_endpoint()

