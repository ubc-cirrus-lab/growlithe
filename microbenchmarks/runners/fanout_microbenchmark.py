import boto3
import time
import concurrent.futures
import os
from botocore.config import Config

# Configure the AWS client with retry settings and connection pooling
config = Config(
    retries = {'max_attempts': 10, 'mode': 'adaptive'},
    max_pool_connections=200  # Adjust based on your needs
)
lambda_client = boto3.client('lambda', config=config)

def invoke_lambda(function_name, client):
    """
    Invoke a Lambda function and return its response.
    
    Args:
    function_name (str): The name of the Lambda function to invoke.
    client (boto3.client): The boto3 Lambda client to use for invocation.
    
    Returns:
    bytes: The payload returned by the invoked Lambda function.
    """
    payload = f'{{"body": "test"}}'
    
    response = client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=payload
    )
    return response['Payload'].read()

def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    This function invokes multiple Lambda functions concurrently based on the input event.
    
    Args:
    event (dict): The event dict containing 'microbenchmark', 'start', and 'end' keys.
    context (object): The context object provided by AWS Lambda.
    
    Returns:
    dict: A dictionary containing the 'time_taken' key with the total execution time in milliseconds.
    """
    microbenchmark = event['microbenchmark']
    start = int(event["start"])
    end = int(event["end"])
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=end-start) as executor:
        futures = [
            executor.submit(invoke_lambda, f'final-{microbenchmark}-{i}', lambda_client)
            for i in range(start, end)
        ]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()

    return {
        'time_taken': (end_time - start_time)*1000
    }