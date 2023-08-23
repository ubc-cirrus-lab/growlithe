import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    announcement = event['body']
    table.put_item(Item={'announcement': announcement})
    return {
        'statusCode': 200,
        'body': json.dumps('Announcement written to db')
    }