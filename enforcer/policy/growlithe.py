from pyDatalog import pyDatalog
from collections import defaultdict
import os

default_value = lambda: {os.environ["AWS_LAMBDA_FUNCTION_NAME"]}
GROWLITHE_TAINTS = defaultdict(default_value)

##==================================================================#
# Arithemtic predicates for numerical operations
pyDatalog.load(
    """
    add(X, Y, Z) <= (X == Y + Z)
    sub(X, Y, Z) <= (X == Y - Z)
               
    mul(X, Y, Z) <= (X == Y * Z)
    div(X, Y, Z) <= (X == Y / Z)
"""
)

# Comparison predicates for numerical operations
pyDatalog.load(
    """
    eq(X, Y) <= (X == Y)
    lt(X, Y) <= (X < Y)
    le(X, Y) <= (X <= Y)
    gt(X, Y) <= (X > Y)
    ge(X, Y) <= (X >= Y)
"""
)


@pyDatalog.predicate()
def not_2(X, Y):
    if X.is_const():
        yield (X.id, not (X.id))
    elif Y.is_const():
        yield (not (Y.id), Y.id)


##==================================================================#
# String predicates
@pyDatalog.predicate()
def isPrefix2(str, pre):
    if str.id.startswith(pre.id):
        yield (str, pre)


@pyDatalog.predicate()
def isSuffix2(str, suf):
    if str.id.endswith(suf.id):
        yield (str, suf)


@pyDatalog.predicate()
def hasSubstr2(str, substr):
    if str.id.startswith(substr.id):
        yield (str, substr)


##==================================================================#
# """Taint predicates"""
@pyDatalog.predicate()
def taintSetIncludes(node_id, label):
    global GROWLITHE_TAINTS
    if node_id.id in GROWLITHE_TAINTS and label.id in GROWLITHE_TAINTS[node_id.id]:
        yield True


@pyDatalog.predicate()
def taintSetExcludes(node_id, label):
    global GROWLITHE_TAINTS
    if node_id.id in GROWLITHE_TAINTS:
        if label.id in GROWLITHE_TAINTS[node_id.id]:
            yield False
        yield True
    # FIXME: Decide what to do if node id not in taint set, so cannot check label


##==================================================================#
# Session properties are retrieved at runtime
# Retrieved values are set for the required datalog variable
# in the policy assertion at runtime
def getSessionVar(prop):
    if prop == "SessionTime":
        import time

        return round(time.time())
    elif prop == "SessionRegion":
        import os

        return os.environ["AWS_REGION"]


def getMetaProp(prop, resource_type, resource_name):
    if prop == "MetaConduitRegion":
        if resource_type == "S3_BUCKET":
            import boto3

            client = boto3.client("s3")
            return client.get_bucket_location(Bucket=resource_name)[
                "LocationConstraint"
            ]
        elif resource_type == "DYNAMODB_TABLE":
            import boto3

            client = boto3.client("dynamodb")
            return client.describe_table(TableName=resource_name)["Table"][
                "TableArn"
            ].split(":")[3]

    elif prop == "MetaConduitResourceName":
        return resource_name


@pyDatalog.predicate()
def getItemVal5(val, table_name, key_name, key, prop):
    print("Getting Value")
    import boto3

    dynamodb = boto3.resource("dynamodb")
    print(table_name.id, key_name.id, key.id, prop.id)
    table = dynamodb.Table(table_name.id)
    print(table)
    response = table.get_item(Key={f"{key_name.id}": key.id})["Item"]
    print(response)
    yield (response[prop.id], table_name, key_name, key, prop)


@pyDatalog.predicate()
def ipToCountry(ip, out):
    import urllib.request
    import json

    endpoint = f"https://ipinfo.io/{ip.id}/json"

    try:
        with urllib.request.urlopen(endpoint) as response:
            data = json.load(response)
            yield (ip, data["country"])
    except urllib.error.URLError:
        pass


def getUserAttribute(event, attr):
    import json

    return json.loads(event["requestContext"]["authorizer"]["claims"][attr])[
        "formatted"
    ]


def getDictNestedKeyVal(dictionary, nestedKeys):
    inner = dictionary
    for key in nestedKeys:
        inner = inner[key]
    return inner
