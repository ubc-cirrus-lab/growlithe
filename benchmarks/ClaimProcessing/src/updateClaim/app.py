import json
import boto3

dynamodb = boto3.resource("dynamodb")
claims_table = dynamodb.Table("Claims")
claim_adjuster_mapping_table = dynamodb.Table("ClaimAdjusterMapping")


def lambda_handler(event, context):
    """
    AWS Lambda function handler for updating claim status.

    This function is triggered by an API Gateway PUT event. It updates the status of a specific claim
    in the DynamoDB 'Claims' table based on the claim ID provided in the path parameters and the new
    status provided in the request body.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - pathParameters (dict): Contains the 'id' of the claim to update.
            - body (str): A JSON string containing the new 'status' for the claim.
            - requestContext (dict): Contains the authorizer information, including:
                - authorizer (dict): Contains claims from the authenticated user, specifically:
                    - claims (dict): User claims, including 'sub' which is the user ID.
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code (200 for success).
            - body (str): A JSON string with the updated claim ID and status.
    """
    claim_id = event["pathParameters"]["id"]
    status = json.loads(event["body"])["status"]

    # Update the claim status
    claims_table.update_item(
        Key={"id": claim_id},
        UpdateExpression="SET #s = :status",
        ExpressionAttributeNames={"#s": "Status"},
        ExpressionAttributeValues={":status": status},
    )

    response = {
        "statusCode": 200,
        "body": json.dumps({"id": claim_id, "Status": status}),
    }
    return response
