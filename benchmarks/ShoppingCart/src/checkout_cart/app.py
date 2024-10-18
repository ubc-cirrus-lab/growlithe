import json
import os
from http.cookies import SimpleCookie

import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(
    "aws-serverless-shopping-cart-benchmark3-shoppingcart-service-DynamoDBShoppingCartTable-QTTPEO3E3L4W"
)
product_service_url = "https://n6sp477ne0.execute-api.us-west-1.amazonaws.com/Prod"


def lambda_handler(event, context):
    """
    Update cart table to use user identifier instead of anonymous cookie value as a key. This will be called when a user
    is logged in.
    """

    cookie = SimpleCookie()
    cart_id = ""
    try:
        cookie.load(event["headers"]["cookie"])
        cart_id = cookie["cartId"].value
    except KeyError:
        cart_id = str(uuid.uuid4())

    cookie = SimpleCookie()
    cookie["cartId"] = cart_id
    cookie["cartId"]["max-age"] = (60 * 60) * 24  # 1 day
    cookie["cartId"]["secure"] = True
    cookie["cartId"]["httponly"] = True
    cookie["cartId"]["samesite"] = "None"
    cookie["cartId"]["path"] = "/"

    headers = {
        "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        "Access-Control-Allow-Credentials": True,
        "Set-Cookie": cookie["cartId"].OutputString(),
    }

    try:
        # Because this method is authorized at API gateway layer, we don't need to validate the JWT claims here
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    except KeyError:
        return {
            "statusCode": 400,
            # "headers": get_headers(cart_id), # INLINED_2
            "headers": headers,
            "body": json.dumps({"message": "Invalid user"}),
        }

    # Define expression attribute values
    expr_attr_values = {":user_id": f"user#{user_id}", ":product_prefix": "product#"}
    # key_condition = Key("pk").eq(f"user#{user_id}") & Key("sk").begins_with("product#")
    # Construct the key condition expression as a string
    key_condition_expression = f"#pk = :user_id and begins_with(#sk, :product_prefix)"

    # Execute the query
    response = table.query(
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeNames={"#pk": "pk", "#sk": "sk"},
        ExpressionAttributeValues=expr_attr_values,
        ConsistentRead=True,
    )

    cart_items = response.get("Items")
    # batch_writer will be used to update status for cart entries belonging to the user
    with table.batch_writer() as batch:
        for item in cart_items:
            key = {"pk": item["pk"], "sk": item["sk"]}
            # Delete ordered items
            batch.delete_item(Key=key)

    ret = {
        "statusCode": 200,
        # "headers": get_headers(cart_id), # INLINED_2
        "headers": headers,
        "body": json.dumps(
            {"products": response.get("Items")},
        ),
    }

    # Dummy API for payment
    payment_url = "https://api.payment-provider.com/v1/checkout/ca-west-1/"
    # Use the payment API for payment as required

    return ret
