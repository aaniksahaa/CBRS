import json

# File path
file_path = 'users.json'

def read_users():
    """Read the users from the JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def write_users(users):
    """Write the users back to the JSON file."""
    with open(file_path, 'w') as file:
        json.dump(users, file, indent=4)

def search_user(username):
    """Search for a user by username."""
    users = read_users()
    for user in users:
        if user['username'] == username:
            return user
    return None

def update_user(username, **kwargs):
    """Update user information."""
    users = read_users()
    for user in users:
        if user['username'] == username:
            for key, value in kwargs.items():
                if key in user:
                    user[key] = value
            write_users(users)
            return True
    return False

# Example usage
if __name__ == "__main__":
    # Search for a user
    user = search_user('john_doe')
    if user:
        print(f"User found: {user}")
    else:
        print("User not found.")
    
    # Update a user
    updated = update_user('john_doe', blood_group='B+', lat=40.730610, lon=-73.935242)
    if updated:
        print("User updated successfully.")
    else:
        print("User not found or update failed.")
