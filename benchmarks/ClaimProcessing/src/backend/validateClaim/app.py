import json
import boto3

dynamodb = boto3.resource("dynamodb")
claims_table = dynamodb.Table("Claims")
user_plan_table = dynamodb.Table("UserPlan")
lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    """
    AWS Lambda function handler for validating claims when they are added or updated.

    This function is triggered by DynamoDB streams on the Claims table. It validates newly inserted
    or modified claims against the user's plan to ensure the claim type is supported. If valid and new,
    it triggers the adjuster assignment process.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - Records (list): A list of DynamoDB stream records, each containing:
                - eventName (str): The type of operation ('INSERT' or 'MODIFY')
                - dynamodb (dict): Contains the new image of the item, including:
                    - NewImage (dict): The attributes of the new/modified item
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        None: This function doesn't return a value, but it may invoke another Lambda function
              and print messages to CloudWatch Logs.
    """
    record = event["Records"][0]
    if record["eventName"] == "INSERT" or record["eventName"] == "MODIFY":
        claim = record["dynamodb"]["NewImage"]
        print(claim)

        claim_id = claim["id"]["S"]
        claim_type = claim["ClaimType"]["S"]
        user_id = claim["ClaimUserId"]["S"]

        # Check if the claim type is supported by the user's coverage
        user_plan = user_plan_table.get_item(Key={"id": user_id})["Item"]
        payload = json.dumps({"claimId": claim_id})

        if claim_type in user_plan["SupportedClaimTypes"]:
            if record["eventName"] == "INSERT":
                # Invoke AssignAdjusterFunction
                # This is the lambda function name generated when deployed
                lambda_client.invoke(
                    FunctionName="ClaimProcessing-AssignAdjusterFunction-D2B89MEqaZiN",
                    InvocationType="Event",
                    Payload=payload,
                )
        else:
            # Handle invalid claim
            print(f"Claim {claim_id} is invalid")
