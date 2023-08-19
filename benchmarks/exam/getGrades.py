import boto3

dynamodb = boto3.client('dynamodb')
table_name = 'GradesDB'

def lambda_handler(event, context):
    print(event)
    username = event['username']

    # Retrieve grade from DynamoDB
    response = dynamodb.get_item(
        TableName=table_name,
        Key={'username': {'S': username}}
    )
    
    grade_item = response.get('Item')

    if not grade_item:
        return {
            'statusCode': 404,
            'body': 'Grade not found for the given username'
        }

    grade = grade_item['grade']['N']

    return {
        'statusCode': 200,
        'body': f"The grade for {username} is {grade}"
    }
