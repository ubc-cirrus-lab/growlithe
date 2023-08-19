import boto3
import hashlib

dynamodb = boto3.client('dynamodb')
table_name = 'UsersDB'

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    role = event['role']

    # Hash the password
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Store user data in DynamoDB
    dynamodb.put_item(
        TableName=table_name,
        Item={
            'username': {'S': username},
            'password': {'B': password_hash},
            'role': {'S': role}
        }
    )

    return {
        'statusCode': 200,
        'body': 'User registered successfully'
    }
