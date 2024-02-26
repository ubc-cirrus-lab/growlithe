import json
import boto3
import uuid
from datetime import datetime
from PIL import Image
import os

s3 = boto3.resource("s3")


def lambda_handler(event, context):
    # Get input
    print("Flip function")

    if event == {}:
        fileName = "sample_3.jpg"
        reqID = "111"
    else:
        fileName = json.loads(event["body"])["data"]["imageName"]
        reqID = json.loads(event["body"])["data"]["reqID"]

    bucket = s3.Bucket("imageprocessingbenchmarktest")
    tempFile = "/tmp/" + fileName
    bucket.download_file(fileName, tempFile)
    image = Image.open(tempFile)

    # Perform flip
    path = "/tmp/flip-left-right-" + fileName
    upPath = reqID + "flip-left-right-" + fileName
    img = image.transpose(Image.FLIP_LEFT_RIGHT)
    img = image.transpose(Image.FLIP_LEFT_RIGHT)
    img.save(path)

    # Upload results
    bucket.upload_file(path, upPath)

    # Clean up
    os.remove(path)
    os.remove(tempFile)

    # Return
    return {
        "statusCode": 200,
        "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "body": json.dumps(
            {
                "data": {"imageName": upPath, "reqID": reqID},
            }
        ),
    }
