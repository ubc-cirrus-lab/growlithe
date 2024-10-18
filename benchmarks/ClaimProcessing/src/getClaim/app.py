import json
import boto3

dynamodb = boto3.resource("dynamodb")
claims_table = dynamodb.Table("Claims")
claim_adjuster_mapping_table = dynamodb.Table("ClaimAdjusterMapping")


def lambda_handler(event, context):
    """
    AWS Lambda function handler for retrieving claim details.

    This function is triggered by an API Gateway GET event. It retrieves the details of a specific claim
    from the DynamoDB 'Claims' table based on the claim ID provided in the path parameters.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - pathParameters (dict): Contains the 'id' of the claim to retrieve.
            - requestContext (dict): Would contain user authentication information.
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code (200 for success, 404 if claim not found).
            - body (str): A JSON string with either the claim details or an error message.
    """
    claim_id = event["pathParameters"]["id"]

    # Get the claim details
    claim = claims_table.get_item(Key={"id": claim_id})["Item"]

    if claim:
        response = {"statusCode": 200, "body": json.dumps(claim)}
    else:
        response = {
            "statusCode": 404,
            "body": json.dumps({"error": f"Claim {claim_id} not found"}),
        }
    return response
