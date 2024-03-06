import boto3
from PIL import Image
import os

def lambda_handler(event, context):
    print(event)

    # Retrieve image object from S3
    s3 = boto3.resource('s3')
    # bucket_name = event['Records'][0]['s3']['bucket']['name']
    # object_key = event['Records'][0]['s3']['object']['key']

    bucket_name = event['detail']['bucket']['name']
    object_key = event['detail']['object']['key']

    bucket = s3.Bucket(bucket_name)
    print(f"Received request for {bucket_name} : {object_key}")

    tempFile = '/tmp/' + object_key    
    os.makedirs(os.path.dirname(tempFile), exist_ok=True)

    bucket.download_file(object_key, tempFile)
    image = Image.open(tempFile)

    # Perform transformations on the image
    image = image.resize((500, 500))  # Example: Resize to 500x500    
    # Add other transformations as needed...

    transformed_temp_file = '/tmp/transformed/' + object_key
    output_key = f"transformed/{object_key}"

    os.makedirs(os.path.dirname(transformed_temp_file), exist_ok=True)

    print(f"Transformed image will be saved to {bucket_name} : {output_key}")
    image.save(transformed_temp_file) 
    # Save transformed image to a temporary S3 location
    bucket.upload_file(transformed_temp_file, output_key)

    return {
        'statusCode': 200,
        'SourceBucket': bucket_name,
        'ObjectKey': output_key
    }
