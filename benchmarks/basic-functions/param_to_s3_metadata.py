import json
import boto3

def lambda_handler(event, context):
    # Extract the filename from the parameter
    filename = json.loads(event['body']).get('user_id')

    # Constant string data
    data_object = "This is a constant string."

    # Write the object to a file in /tmp directory with the specified filename
    file_path = f'/tmp/{filename}.json'
    with open(file_path, 'w') as file:
        json.dump(data_object, file)

    # Upload the file to the "Data" S3 bucket with the specified filename
    s3_bucket = 'Data'
    s3_key = f'{filename}.json'

    s3_resource = boto3.resource('s3')
    s3_resource.Bucket(s3_bucket).upload_file(file_path, s3_key)

    response = {
        'statusCode': 200,
        'body': json.dumps(f"Uploaded to S3://{s3_bucket}/{s3_key}")
    }
    return response