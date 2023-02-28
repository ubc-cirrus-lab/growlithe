import boto3

client = boto3.client('dynamodb')

def lambda_handler(event, context):
    user_id = event['user_id']
    tweet_id = event['tweet_id']
    user_location = event['user_location']

    params = {'TableName': 'tweets', 'Key': {'userId': user_id, 'tweetId': tweet_id}}
    tweet = client.get_item(**params)
    expiration_time = tweet['Item']['expirationTime']

    return {
        'statusCode': 200,
        'body': tweet['Item']
    };