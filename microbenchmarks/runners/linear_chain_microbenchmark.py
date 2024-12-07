import boto3
import time
from botocore.config import Config

# Configure the AWS client with retry settings and connection pooling
config = Config(
    retries = {'max_attempts': 10, 'mode': 'adaptive'},
    max_pool_connections=200  # Adjust based on your needs
)
lambda_client = boto3.client('lambda', config=config)

def invoke_lambda(function_name, payload):
    """
    Invoke a Lambda function and return its response.
    
    Args:
    function_name (str): The name of the Lambda function to invoke (currently not used).
    payload (str): The payload to send to the invoked Lambda function.
    
    Returns:
    bytes: The payload returned by the invoked Lambda function.
    """
    response = lambda_client.invoke(
        FunctionName='debug_remote_baseline',  # Note: This is hardcoded and doesn't use the function_name parameter
        InvocationType='RequestResponse',
        Payload=payload
    )
    
    return response['Payload'].read()

def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    This function sequentially invokes multiple Lambda functions based on the input event.
    
    Args:
    event (dict): The event dict containing 'microbenchmark', 'start', and 'end' keys.
    context (object): The context object provided by AWS Lambda (not used in this function).
    
    Returns:
    dict: A dictionary containing the 'time_taken' key with the total execution time in milliseconds.
    """
    microbenchmark = event['microbenchmark']
    start = int(event["start"])
    end = int(event["end"])

    payload = '{"body": "test"}'
    start_time = time.time()
    
    for i in range(start, end):
        payload = invoke_lambda(f'final-{microbenchmark}-{i}', payload)
        print(payload)
    
    end_time = time.time()

    return {
        'time_taken': (end_time - start_time)*1000
    }