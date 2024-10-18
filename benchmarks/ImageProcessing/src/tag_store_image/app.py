import boto3
from PIL import Image, ImageFilter
import os


def lambda_handler(event, context):
    """
    AWS Lambda function handler for processing images stored in S3.

    This function is triggered by an event containing information about an image in S3.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - SourceBucket (str): The name of the S3 bucket where the original image is stored.
            - ObjectKey (str): The key of the original image object in S3.
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code (200 for success).
            - SourceBucket (str): The name of the S3 bucket where the processed image is stored.
            - ObjectKey (str): The key of the processed image in S3.

    Note:
        - This function uses the /tmp directory for temporary file storage, which is the only
          writable directory in the Lambda execution environment.
    """
    print(event)

    # Retrieve image object from S3
    s3 = boto3.resource("s3")
    bucket_name = event["SourceBucket"]
    bucket = s3.Bucket(bucket_name)
    object_key = event["ObjectKey"]

    print(f"Received request for {bucket_name} : {object_key}")

    tempFile = "/tmp/" + object_key
    os.makedirs(os.path.dirname(tempFile), exist_ok=True)

    bucket.download_file(object_key, tempFile)

    final_bucket_name = bucket_name + "-processed"
    final_bucket = s3.Bucket(final_bucket_name)
    final_object_key = os.path.basename(object_key)

    final_bucket.upload_file(tempFile, final_object_key)

    ret = {
        "statusCode": 200,
        "SourceBucket": final_bucket_name,
        "ObjectKey": final_object_key,
    }
    return ret
