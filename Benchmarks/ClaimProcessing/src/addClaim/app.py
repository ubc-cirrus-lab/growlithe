import json
import boto3
import uuid

# Initialize DynamoDB resource and table
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Claims")


def lambda_handler(event, context):
    """
    AWS Lambda function handler for processing claim submission requests.

    This function is triggered by an API Gateway event. It processes incoming POST requests to
    add new claims to a DynamoDB table. The claim information is extracted from the request body,
    a unique ID for the claim is generated, and the claim data is stored in the 'Claims' table.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - body (str): A JSON string with the claim details (Name and ClaimType).
            - requestContext (dict): Automatically added by API Gateway when using Cognito authorizer. Contains:
                - authorizer (dict): Information from the Cognito authorizer, including:
                    - claims (dict): User claims from Cognito, including 'sub' which is the user ID.
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code (201 for success).
            - body (str): A JSON string with a success message and the generated claim ID.
    """

    # Parse the claim data from the request body
    claim = json.loads(event["body"])

    # Generate a unique ID for the claim
    claim_id = str(uuid.uuid4())

    # Extract the user ID from the Cognito authorizer
    claim_user_id = event["requestContext"]["authorizer"]["claims"]["sub"]

    # Prepare the item to be inserted into DynamoDB
    item = {
        "id": claim_id,
        "ClaimUserId": claim_user_id,
        "Name": claim["Name"],
        "ClaimType": claim["ClaimType"],
        "Status": "PENDING",
    }

    # Insert the item into the DynamoDB table
    table.put_item(Item=item)

    # Prepare and return the success response
    response = {
        "statusCode": 201,
        "body": json.dumps({"message": "Claim submitted successfully", "id": claim_id}),
    }

    return response
