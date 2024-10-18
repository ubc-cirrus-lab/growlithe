import random
import boto3

dynamodb = boto3.resource("dynamodb")
claims_table = dynamodb.Table("Claims")
adjusters_table = dynamodb.Table("Adjusters")
claim_adjuster_mapping_table = dynamodb.Table("ClaimAdjusterMapping")


def lambda_handler(event, context):
    """
    AWS Lambda function handler for assigning an adjuster to a claim.

    This function is triggered after a new claim is validated. It randomly selects an adjuster
    from the Adjusters table and creates a mapping between the claim and the selected adjuster
    in the ClaimAdjusterMapping table.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - claimId (str): The ID of the claim to be assigned an adjuster.
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        None: This function doesn't return a value, but it creates a new item in the
              ClaimAdjusterMapping table and prints log messages.
    """
    claim_id = event["claimId"]
    print(claim_id)

    # Get a random adjuster from the Adjusters table
    adjusters = adjusters_table.scan()["Items"]
    print(adjusters)
    adjuster = random.choice(adjusters)

    # Store the claim-adjuster mapping
    item = {"id": claim_id, "AdjusterId": adjuster["id"]["S"]}
    claim_adjuster_mapping_table.put_item(Item=item)

    print(f"Assigned adjuster {adjuster} to claim {claim_id}")
