import boto3
import hashlib
import uuid

dynamodb = boto3.client('dynamodb')
table_name = 'UsersDB'

def lambda_handler(event, context):
    username = event['username']
    password = event['password']

    # Retrieve user data from DynamoDB
    response = dynamodb.get_item(
        TableName=table_name,
        Key={'username': {'S': username}}
    )
    user_item = response.get('Item')

    if not user_item:
        return {
            'statusCode': 401,
            'body': 'Invalid credentials'
        }

    stored_password_hash = user_item['password']['B'].decode('ascii')

    # Hash the provided password and compare
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    if password_hash != stored_password_hash:
        return {
            'statusCode': 401,
            'body': 'Invalid credentials'
        }

    # Generate a token (for demonstration purposes)
    token = str(uuid.uuid4())

    # Store the token in the user's record
    dynamodb.update_item(
        TableName=table_name,
        Key={'username': {'S': username}},
        UpdateExpression='SET loginToken = :token',
        ExpressionAttributeValues={':token': {'S': token}}
    )

    return {
        'statusCode': 200,
        'body': token
    }
