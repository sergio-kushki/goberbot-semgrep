"""Sample vulnerable Python code for testing Semgrep rules"""

import os
import hashlib
import random
from subprocess import call

# SHOULD TRIGGER: hardcoded-password
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin123',
    'database': 'production_db'
}

# SHOULD TRIGGER: exec-command-injection
def execute_system_command(user_input):
    """Dangerous: executes arbitrary commands"""
    os.system(f"ls {user_input}")
    return True

# SHOULD TRIGGER: sql-injection-risk
def get_user(username):
    """Vulnerable to SQL injection"""
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    # execute(query)  # Simulated
    return query

# SHOULD TRIGGER: weak-crypto-md5
def hash_user_password(password):
    """Using weak MD5 hashing"""
    return hashlib.md5(password.encode()).hexdigest()

# SHOULD TRIGGER: insecure-random
def generate_session_token():
    """Using insecure random for security-sensitive operation"""
    return str(random.random())

# SHOULD TRIGGER: no-print-statements
def debug_function(data):
    """Debug prints that shouldn't be in production"""
    print(f"Debug: {data}")
    print("Processing data...")
    return data

# SHOULD TRIGGER: hardcoded-api-key
API_KEY = "sk_test_1234567890abcdefghijklmnopqrstuvwxyz"
SECRET_KEY = "secret_key_9876543210zyxwvutsrqponmlkjihgfedcba"

# SHOULD TRIGGER: todo-comment
def calculate_discount(price, customer_type):
    # TODO: Implement tiered discount system
    # FIXME: This doesn't work for enterprise customers
    if customer_type == 'premium':
        return price * 0.9
    return price

# Safe code (should NOT trigger)
def safe_password_handling():
    """Example of secure password handling"""
    password = os.getenv('DB_PASSWORD')
    return password

def safe_random():
    """Using cryptographically secure random"""
    import secrets
    return secrets.token_hex(16)

def safe_sql_query(username):
    """Using parameterized queries"""
    query = "SELECT * FROM users WHERE username = ?"
    params = (username,)
    return query, params

if __name__ == "__main__":
    # SHOULD TRIGGER: no-print-statements
    print("Running vulnerable code examples")
    debug_function({"test": "data"})

