"""
Test script for Document Information Extractor
Run this after starting the main API server
"""

import requests
import json
from pathlib import Path

# API Configuration
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if the API is running"""
    print("=" * 60)
    print("Testing Health Check...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the server is running.")
        print("   Run: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_extract_from_file(file_path):
    """Test extracting information from a file"""
    print("\n" + "=" * 60)
    print(f"Testing File Extraction: {file_path}")
    print("=" * 60)
    
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        return
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
            response = requests.post(f"{API_BASE_URL}/extract", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            print("\nExtracted Information:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_extract_from_text():
    """Test extracting information from sample text"""
    print("\n" + "=" * 60)
    print("Testing Text Extraction (Sample Data)")
    print("=" * 60)
    
    sample_text = """
    Insurance Policy Document
    
    Policy Holder: John Doe
    Policy Number: P/123456/01/2023/001234
    Email: john.doe@email.com
    
    Policy Details:
    Policy Name: Family Health Optima Insurance Plan
    Plan Type: 2A
    Sum Assured: Rs. 500000
    Room Rent Limit: Single Private AC Room
    Waiting Period: 30 days for specified diseases
    
    This is a sample insurance document for testing purposes.
    """
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/extract-text",
            params={"text": sample_text}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            print("\nExtracted Information:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n" + "=" * 60)
    print("Testing Root Endpoint...")
    print("=" * 60)
    
    try:
        response = requests.get(API_BASE_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def display_menu():
    """Display test menu"""
    print("\n" + "=" * 60)
    print("Document Information Extractor - Test Menu")
    print("=" * 60)
    print("1. Health Check")
    print("2. Test Root Endpoint")
    print("3. Extract from File (PDF/TXT/DOCX)")
    print("4. Extract from Sample Text")
    print("5. Run All Tests")
    print("6. Exit")
    print("=" * 60)

def run_all_tests(file_path=None):
    """Run all tests"""
    print("\n" + "🚀 Running All Tests...\n")
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n⚠️  API is not healthy. Please check your setup.")
        return
    
    # Test 2: Root Endpoint
    test_root_endpoint()
    
    # Test 3: Sample Text Extraction
    test_extract_from_text()
    
    # Test 4: File Extraction (if file provided)
    if file_path:
        test_extract_from_file(file_path)
    
    print("\n" + "=" * 60)
    print("✅ All Tests Completed!")
    print("=" * 60)

def main():
    """Main test function"""
    print("\n" + "🔬 Document Information Extractor - Test Suite")
    print("Make sure the API server is running on http://localhost:8000\n")
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-6): ").strip()