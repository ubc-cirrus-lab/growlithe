import boto3
import json

dynamodb = boto3.resource("dynamodb")
claim_adjuster_mapping_table = dynamodb.Table("ClaimAdjusterMapping")


def lambda_handler(event, context):
    """
    AWS Lambda function handler for retrieving claims assigned to an adjuster.

    This function is triggered by an API Gateway GET event. It retrieves all claims
    assigned to the authenticated adjuster from the DynamoDB 'ClaimAdjusterMapping' table.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - requestContext (dict): Contains the authorizer information, including:
                - authorizer (dict): Contains claims from the authenticated user, specifically:
                    - claims (dict): User claims, including 'sub' which is the adjuster ID.
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code (200 for success).
            - headers (dict): Contains 'Content-Type' set to 'application/json'.
            - body (str): A JSON string containing an array of assigned claims.
    """
    # Get the adjuster ID from the authorizer claims
    adjuster_id = event["requestContext"]["authorizer"]["claims"]["sub"]

    # Scan the ClaimAdjusterMapping table for claims assigned to the adjuster
    response = claim_adjuster_mapping_table.scan(
        FilterExpression="adjId = :adjuster_id",
        ExpressionAttributeValues={":adjuster_id": adjuster_id},
    )
    assigned_claims = response["Items"]

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(assigned_claims),
    }
