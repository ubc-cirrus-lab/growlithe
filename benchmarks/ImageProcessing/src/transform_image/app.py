import boto3
from PIL import Image
import os


def lambda_handler(event, context):
    """
    AWS Lambda function handler for processing images uploaded to S3.

    This function is triggered by S3 events when a new image is uploaded. It downloads the image,
    resizes it to 500x500 pixels, and uploads the transformed image back to S3 in a 'transformed/' prefix.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - detail (dict): Contains information about the S3 event, including:
                - bucket (dict): Information about the S3 bucket:
                    - name (str): The name of the S3 bucket.
                - object (dict): Information about the S3 object:
                    - key (str): The key of the uploaded object (image).
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code (200 for success).
            - SourceBucket (str): The name of the S3 bucket where the original image is stored.
            - ObjectKey (str): The key of the transformed image in S3.

    Note:
        This function uses the /tmp directory for temporary file storage, which is the only
        writable directory in the Lambda execution environment.
    """
    # Retrieve image object from S3
    s3 = boto3.resource("s3")

    bucket_name = event["detail"]["bucket"]["name"]
    object_key = event["detail"]["object"]["key"]

    bucket = s3.Bucket(bucket_name)
    print(f"Received request for {bucket_name} : {object_key}")

    tempFile = "/tmp/" + object_key
    os.makedirs(os.path.dirname(tempFile), exist_ok=True)

    bucket.download_file(object_key, tempFile)
    image = Image.open(tempFile)

    # Perform transformations on the image
    image = image.resize((500, 500))

    transformed_temp_file = "/tmp/transformed/" + object_key
    output_key = f"transformed/{object_key}"

    os.makedirs(os.path.dirname(transformed_temp_file), exist_ok=True)

    print(f"Transformed image will be saved to {bucket_name} : {output_key}")
    image.save(transformed_temp_file)
    # Save transformed image to a temporary S3 location
    bucket.upload_file(transformed_temp_file, output_key)

    ret = {"statusCode": 200, "SourceBucket": bucket_name, "ObjectKey": output_key}
    return ret
