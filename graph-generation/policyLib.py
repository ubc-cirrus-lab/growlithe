import boto3

users_db = boto3.client("dynamodb", region_name='us-east-2')
table_name = "UsersDB"

def is_teacher(username, login_token):
    user = users_db.get_item(TableName="UsersDB", Key={"username": {"S": username}})[
        "Item"
    ]
    if user["loginToken"]["S"] != login_token:
        raise Exception("Login token mismatch")
    return user["role"]["S"] == "teacher"


def is_record_owner(username, login_token, requested_username):
    user = users_db.get_item(TableName="UsersDB", Key={"username": {"S": username}})[
        "Item"
    ]
    if user["loginToken"]["S"] != login_token:
        raise Exception("Login token mismatch")
    return user["username"]["S"] == requested_username
