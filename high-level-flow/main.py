import requests
import boto3
from urllib.request import urlopen
import socket

def main():
    response = requests.get('https://www.google.com', data={'q': 'python'})
    response2 = requests.post('https://www.google2.com')
    print(response.status_code)
    with urlopen("https://www.example.com") as response:
        body = response.read()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("123.23.23.23", 8888))
        s.sendall(b"Test")
    
    l = boto3.client('lambda')
    l.invoke(FunctionName='test', InvocationType='Event', Payload='{"key1": "value1", "key2": "value2", "key3": "value3"}')

    s3 = boto3.resource('s3')
    bucket = s3.Bucket('mybucket')
    for obj in bucket.objects.all():
        print(obj.key, obj.last_modified)
    
    with open('test.txt', 'rb') as data:
        s3.Bucket('mybucket').put_object(Key='test.txt', Body=data)
    
    with open('test.txt', 'wb') as data:
        s3.Bucket('mybucket').download_fileobj('test.txt', data)

    session = boto3.Session(region_name = 'us-west-2')
    backup_s3 = session.resource('s3')
    lam = session.client('lambda')