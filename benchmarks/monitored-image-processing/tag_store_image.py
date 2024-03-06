import boto3
from PIL import Image, ImageFilter
import os

def lambda_handler(event, context):
    print(event)

    # Retrieve image object from S3
    s3 = boto3.resource('s3')
    bucket_name = event['SourceBucket']
    bucket = s3.Bucket(bucket_name)
    object_key = event['ObjectKey']

    print(f"Received request for {bucket_name} : {object_key}")

    tempFile = '/tmp/' + object_key    
    os.makedirs(os.path.dirname(tempFile), exist_ok=True)

    bucket.download_file(object_key, tempFile)
    
    # TODO: Add some meaningful tag operation before storing

    # BUG: This is the intended bug.
    # Step function does additional blur for user images but ends
    # up storing the image in the wrong bucket
    final_bucket_name = 'mip-processed-stock-images'
    final_bucket = s3.Bucket(final_bucket_name)
    final_object_key = os.path.basename(object_key)

    final_bucket.upload_file(tempFile, final_object_key)

    return {
        'statusCode': 200,
        'SourceBucket': final_bucket_name,
        'ObjectKey': final_object_key
    }