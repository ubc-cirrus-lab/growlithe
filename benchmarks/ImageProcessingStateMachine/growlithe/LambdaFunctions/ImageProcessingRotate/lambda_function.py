from growlithe_utils import TAINTS
TAINTS['SourceCode_Dict'] = set()
TAINTS['imageprocessingbenchmark_upPath'] = set()
TAINTS['tempfs_path'] = set()
TAINTS['tempfs_tempFile'] = set()
TAINTS['imageprocessingbenchmark_sample_3.jpg'] = set()
import json
import boto3
import uuid
from datetime import datetime
import os
import base64
import logging
import pyDatalog

from PIL import Image, ImageFilter
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    TAINTS['SourceCode_event'] = event.get('GROWLITHE_TAINTS', set())
    TAINTS['SourceCode_context'] = event.get('GROWLITHE_TAINTS', set())
    print('Roatate function')
    if event == {}:
        fileName = 'sample_3.jpg'
        reqID = '111'
    else:
        fileName = json.loads(event['body'])['data']['imageName']
        reqID = json.loads(event['body'])['data']['reqID']
    bucket = s3.Bucket('imageprocessingbenchmark')
    tempFile = '/tmp/' + fileName
    TAINTS['tempfs_tempFile'] = TAINTS['tempfs_tempFile'].union(TAINTS['imageprocessingbenchmark_sample_3.jpg'])
    TAINTS['tempfs_tempFile'].add('tempfs_tempFile')
    assert pyDatalog.ask(f"(PropDataObjectName=={tempFile}) & isSuffix(PropDataObjectName, '.jpg')") != None, 'Policy evaluated to be false'
    bucket.download_file(fileName, tempFile)
    TAINTS['tempfs_tempFile'].add('tempfs_tempFile')
    TAINTS['imageprocessingbenchmark_sample_3.jpg'].add('imageprocessingbenchmark_sample_3.jpg')
    image = Image.open(tempFile)
    img = image.transpose(Image.ROTATE_90)
    path = '/tmp/' + 'rotate-90-' + fileName
    upPath = reqID + 'rotate-90-' + fileName
    TAINTS['tempfs_path'] = TAINTS['tempfs_path'].union(TAINTS['tempfs_tempFile'])
    TAINTS['tempfs_path'].add('tempfs_path')
    img.save(path)
    TAINTS['tempfs_path'].add('tempfs_path')
    if path.contains('rotate-90'):
        TAINTS['imageprocessingbenchmark_upPath'] = TAINTS['imageprocessingbenchmark_upPath'].union(TAINTS['tempfs_path'])
        TAINTS['imageprocessingbenchmark_upPath'].add('imageprocessingbenchmark_upPath')
        assert pyDatalog.ask(f"taintSetContains('RESOURCE:S3_BUCKET:imageprocessingbenchmark')") != None, 'Policy evaluated to be false'
        bucket.upload_file(path, upPath)
    os.remove(path)
    os.remove(tempFile)
    TAINTS['SourceCode_Dict'] = TAINTS['SourceCode_Dict'].union(TAINTS['SourceCode_event'])
    TAINTS['SourceCode_Dict'].add('SourceCode_Dict')
    return {'statusCode': 200, 'timestamp': datetime.now().strftime('%m/%d/%Y, %H:%M:%S'), 'body': json.dumps({'data': {'imageName': upPath, 'reqID': reqID}}), 'GROWLITHE_TAINTS': TAINTS['SourceCode_Dict']}