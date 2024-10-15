"""
Cognito User Creation Script

This script creates users and adjusters in an AWS Cognito User Pool and saves their credentials to CSV files.

Requirements:
- boto3 library
- AWS credentials configured

Usage:
1. Set the USER_POOL_ID constant to your Cognito User Pool ID.
2. Adjust NUM_USERS, NUM_ADJUSTERS, and START_AT constants as needed.
3. Run the script.

The script will create users and adjusters in the specified Cognito User Pool and save their credentials
to 'user_credentials.csv' and 'adjuster_credentials.csv' respectively.
"""

import boto3
import csv
from botocore.exceptions import ClientError

# Constants
USER_POOL_ID = "<USER_POOL_ID>"
NUM_USERS = 5
NUM_ADJUSTERS = 2
START_AT = 1

# Create Cognito client
cognito_idp = boto3.client("cognito-idp")

def create_user(username, email, password):
    """
    Create a user in the Cognito User Pool and set a permanent password.

    Args:
    username (str): The username for the new user.
    email (str): The email address for the new user.
    password (str): The password for the new user.

    Returns:
    str: The username of the created user.

    Raises:
    ClientError: If there's an error creating the user or setting the password.
    """
    try:
        response = cognito_idp.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=username,
            UserAttributes=[{"Name": "email", "Value": email}],
            TemporaryPassword=password,
            MessageAction="SUPPRESS",
        )
        
        cognito_idp.admin_set_user_password(
            UserPoolId=USER_POOL_ID,
            Username=username,
            Password=password,
            Permanent=True
        )
        
        return response["User"]["Username"]
    except ClientError as e:
        print(f"Error creating user {username}: {e}")
        return None

def create_users(num_users, user_type, start_at):
    """
    Create multiple users and save their credentials to a CSV file.

    Args:
    num_users (int): The number of users to create.
    user_type (str): The type of user ('user' or 'adjuster').
    start_at (int): The starting number for user creation.

    Returns:
    None
    """
    filename = f"{user_type}_credentials.csv"
    
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Email", "Password"])
        
        for i in range(num_users):
            username = f"{user_type}{i + start_at}"
            email = f"{username}@example.com"
            password = f"{user_type.capitalize()}123!{i + start_at}"
            
            created_username = create_user(username, email, password)
            
            if created_username:
                writer.writerow([username, email, password])
                print(f"Created {user_type}: {username}")

def main():
    """
    Main function to create users and adjusters.
    """
    print("Creating users...")
    create_users(NUM_USERS, "user", START_AT)
    
    print("\nCreating adjusters...")
    create_users(NUM_ADJUSTERS, "adjuster", START_AT)
    
    print("\nUser creation complete. Check the CSV files for credentials.")

if __name__ == "__main__":
    main()