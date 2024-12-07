import json
import time
import os
import boto3


def lambda_handler(event, context):
    body = event["body"]

    s3 = boto3.resource("s3")
    bucket_name = "sensitivity-test-gr"
    bucket = s3.Bucket(bucket_name)
    object_key = os.getenv("AWS_LAMBDA_FUNCTION_NAME")

    tempFile = "/tmp/" + object_key
    os.makedirs(os.path.dirname(tempFile), exist_ok=True)

    bucket.download_file(object_key, tempFile)

    time.sleep(0.065)

    output_key = f"output/{object_key}"
    bucket.upload_file(tempFile, output_key)

    response = {"statusCode": 200, "body": body}
    return response
