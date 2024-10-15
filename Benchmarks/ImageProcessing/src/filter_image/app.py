import boto3
from PIL import Image, ImageFilter
import os

def lambda_handler(event, context):
    """
    AWS Lambda function handler for applying a sharpening effect to images stored in S3.

    This function is triggered by an event containing information about an image in S3.
    It downloads the image, applies a sharpening filter, and uploads the enhanced image
    back to S3 in an 'enhanced/' prefix.

    Args:
        event (dict): The event data passed to the Lambda function. It should contain:
            - SourceBucket (str): The name of the S3 bucket where the original image is stored.
            - ObjectKey (str): The key of the original image object in S3.
        context (object): The context object provided by AWS Lambda, which contains runtime information.

    Returns:
        dict: A dictionary containing:
            - statusCode (int): HTTP status code (200 for success).
            - SourceBucket (str): The name of the S3 bucket where the enhanced image is stored.
            - ObjectKey (str): The key of the enhanced image in S3.

    Note:
        This function uses the /tmp directory for temporary file storage, which is the only
        writable directory in the Lambda execution environment.
    """
    # Retrieve image object from S3
    s3 = boto3.resource('s3')
    bucket_name = event['SourceBucket']
    bucket = s3.Bucket(bucket_name)
    object_key = event['ObjectKey']

    print(f"Received request for {bucket_name} : {object_key}")

    tempFile = '/tmp/' + object_key    
    os.makedirs(os.path.dirname(tempFile), exist_ok=True)

    bucket.download_file(object_key, tempFile)
    image = Image.open(tempFile)

    # Perform transformations on the image
    image = image.filter(ImageFilter.SHARPEN)

    transformed_temp_file = '/tmp/transformed/' + object_key
    output_key = f"enhanced/{object_key}"

    os.makedirs(os.path.dirname(transformed_temp_file), exist_ok=True)

    print(f"Transformed image will be saved to {bucket_name} : {output_key}")
    image.save(transformed_temp_file) 
    # Save transformed image to a temporary S3 location
    bucket.upload_file(transformed_temp_file, output_key)

    ret = {
        'statusCode': 200,
        'SourceBucket': bucket_name,
        'ObjectKey': output_key
    }
    return ret