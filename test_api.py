"""
API Testing Examples - Save as test_api.py or use with Postman/Insomnia
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# ============================================================================
# AUTHENTICATION EXAMPLES
# ============================================================================

def test_register_student():
    """Test registering a new student."""
    payload = {
        "email": "alice@example.com",
        "password": "password123",
        "role": "STUDENT"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print("Register Student:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()


def test_register_parent():
    """Test registering a new parent."""
    payload = {
        "email": "bob@example.com",
        "password": "password123",
        "role": "PARENT"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print("\nRegister Parent:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()


def test_login(email, password):
    """Test user login."""
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print(f"\nLogin ({email}):", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()


def test_get_current_user(token):
    """Test getting current user info."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print("\nGet Current User:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()


def test_invalid_credentials():
    """Test login with invalid credentials."""
    payload = {
        "email": "alice@example.com",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print("\nLogin with Invalid Password:", response.status_code)
    print(json.dumps(response.json(), indent=2))


def test_invalid_role():
    """Test registration with invalid role."""
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "role": "ADMIN"  # Invalid role
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print("\nRegister with Invalid Role:", response.status_code)
    print(json.dumps(response.json(), indent=2))


def test_duplicate_email():
    """Test registering with duplicate email."""
    # First registration
    payload1 = {
        "email": "duplicate@example.com",
        "password": "password123",
        "role": "STUDENT"
    }
    requests.post(f"{BASE_URL}/auth/register", json=payload1)
    
    # Duplicate registration
    payload2 = {
        "email": "duplicate@example.com",
        "password": "password456",
        "role": "PARENT"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload2)
    print("\nRegister with Duplicate Email:", response.status_code)
    print(json.dumps(response.json(), indent=2))


def test_short_password():
    """Test registration with password too short."""
    payload = {
        "email": "shortpass@example.com",
        "password": "short",  # Less than 8 characters
        "role": "STUDENT"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print("\nRegister with Short Password:", response.status_code)
    print(json.dumps(response.json(), indent=2))


def test_invalid_email():
    """Test registration with invalid email."""
    payload = {
        "email": "not-an-email",  # Invalid email format
        "password": "password123",
        "role": "STUDENT"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print("\nRegister with Invalid Email:", response.status_code)
    print(json.dumps(response.json(), indent=2))


def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print("\nHealth Check:", response.status_code)
    print(json.dumps(response.json(), indent=2))


def test_root():
    """Test root endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print("\nRoot Endpoint:", response.status_code)
    print(json.dumps(response.json(), indent=2))


# ============================================================================
# TEST FLOW
# ============================================================================

def run_all_tests():
    """Run all tests in sequence."""
    print("=" * 70)
    print("MATHSTEP AI - AUTHENTICATION API TESTS")
    print("=" * 70)
    
    # Health checks
    print("\n--- Health Checks ---")
    test_health_check()
    test_root()
    
    # Happy path
    print("\n--- Happy Path ---")
    student_response = test_register_student()
    student_token = student_response.get("access_token")
    
    parent_response = test_register_parent()
    parent_token = parent_response.get("access_token")
    
    # Test logins
    print("\n--- Login Tests ---")
    login_response = test_login("alice@example.com", "password123")
    
    # Test get current user
    print("\n--- Get Current User ---")
    if student_token:
        test_get_current_user(student_token)
    
    # Error cases
    print("\n--- Error Cases ---")
    test_invalid_credentials()
    test_invalid_role()
    test_duplicate_email()
    test_short_password()
    test_invalid_email()
    
    print("\n" + "=" * 70)
    print("TESTS COMPLETED")
    print("=" * 70)


# ============================================================================
# CURL COMMAND EXAMPLES
# ============================================================================

curl_examples = """
# CURL Examples - Copy and paste these commands in your terminal

# 1. Health Check
curl -X GET "http://localhost:8000/health"

# 2. Register Student
curl -X POST "http://localhost:8000/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "student@example.com",
    "password": "password123",
    "role": "STUDENT"
  }'

# 3. Register Parent
curl -X POST "http://localhost:8000/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "parent@example.com",
    "password": "password123",
    "role": "PARENT"
  }'

# 4. Login
curl -X POST "http://localhost:8000/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'

# 5. Get Current User (replace YOUR_TOKEN with actual token)
curl -X GET "http://localhost:8000/auth/me" \\
  -H "Authorization: Bearer YOUR_TOKEN"

# 6. Get Google Login URL (opens in browser)
http://localhost:8000/auth/google/login

# 7. Invalid Credentials
curl -X POST "http://localhost:8000/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "student@example.com",
    "password": "wrongpassword"
  }'

# 8. Invalid Role
curl -X POST "http://localhost:8000/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "role": "ADMIN"
  }'

# 9. Duplicate Email
curl -X POST "http://localhost:8000/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "student@example.com",
    "password": "password456",
    "role": "PARENT"
  }'

# 10. Short Password
curl -X POST "http://localhost:8000/auth/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "short",
    "role": "STUDENT"
  }'
"""


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        print(curl_examples)
    else:
        try:
            run_all_tests()
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to server.")
            print("Make sure the server is running: uvicorn app.main:app --reload")
