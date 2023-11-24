import json
import boto3

def lambda_handler(event, context):
    # Extract the object from the 'data' key in the JSON body
    data_object = json.loads(event['body']).get('data')

    # Write the object to a file in /tmp directory
    file_path = '/tmp/data_object.json'
    with open(file_path, 'w') as file:
        json.dump(data_object, file)

    # Upload the file to the "Data" S3 bucket
    s3_bucket = 'Data'
    s3_key = 'data_object.json'

    s3_resource = boto3.resource('s3')
    s3_resource.Bucket(s3_bucket).upload_file(file_path, s3_key)

    response = {
        'statusCode': 200,
        'body': json.dumps(f"Uploaded to S3://{s3_bucket}/{s3_key}")
    }

    return response