import json
import boto3
import os

dynamodb = boto3.client('dynamodb')
table_name = 'announcements'

def lambda_handler(event, context):
    announcement = event['body']
    dynamodb.put_item(
        TableName=table_name,
        Item={'announcement': {'S': announcement}})
    return {
        'statusCode': 200,
        'body': json.dumps('Announcement written to db')
    }