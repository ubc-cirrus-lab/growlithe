import json
import boto3
import uuid
from datetime import datetime
import os
import base64
import logging
from PIL import Image, ImageFilter

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    
    # Get input
    print("GrayScale function")
    if event == {}:
        fileName = 'sample_2.png'
        reqID = '111'
    else:
        fileName = json.loads(event['body'])['data']['imageName']
        reqID = json.loads(event['body'])['data']['reqID']
    
    bucket = s3.Bucket('imageprocessingbenchmark')
    tempFile = '/tmp/' + fileName
    bucket.download_file(fileName, tempFile)
    image = Image.open(tempFile)
   
    # Perform filter
    img = image.convert('L')
    path = "/tmp/" + "gray-scale-" + fileName
    upPath = reqID + "gray-scale-" + fileName
    img.save(path)

    # Upload results
    bucket.upload_file(path, upPath)
    
    # Clean up
    os.remove(path)
    os.remove(tempFile)
    
    # Return
    return {
        'statusCode': 200,
        'timestamp': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        'body': json.dumps({
            'data': {'imageName': upPath, 'reqID':reqID}
        })
    }