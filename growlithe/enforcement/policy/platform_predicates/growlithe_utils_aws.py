from pyDatalog import pyDatalog
from collections import defaultdict
import os, time, boto3, json
import urllib.request

s3_client = boto3.client("s3")
dynamo_client = boto3.client("dynamodb")

default_value = lambda: {os.environ["AWS_LAMBDA_FUNCTION_NAME"]}
GROWLITHE_TAINTS = defaultdict(default_value)
GROWLITHE_INVOCATION_ID = ""
GROWLITHE_FILE_TAINTS = defaultdict(default_value)

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


# Binary not where Y == not(X)
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


@pyDatalog.predicate()
def concat3(concatenated_string, str1, str2):
    yield (str1.id + str2.id, str1, str2)


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


@pyDatalog.predicate()
def getItemVal5(val, table_name, key_name, key, prop):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name.id)
    response = table.get_item(Key={f"{key_name.id}": key.id})["Item"]
    yield (response[prop.id], table_name, key_name, key, prop)


def ipToCountryHelper(ip):
    endpoint = f"https://ipinfo.io/{ip.id}/json"
    with urllib.request.urlopen(endpoint) as response:
        data = json.load(response)
        return data["country"]


@pyDatalog.predicate()
def ipToCountry(ip, out):
    country = ipToCountryHelper(ip.id)
    yield (ip, country)


def getDictNestedKeyVal(dictionary, nestedKeys):
    inner = dictionary
    for key in nestedKeys:
        inner = inner[key]
    return inner


##==================================================================#
# Instance properties are retrieved at function runtime
def getInstProp(prop):
    if prop == "InstTime":
        return round(time.time())
    elif prop == "InstRegion":
        return os.environ["AWS_REGION"]


def getResourceProp(prop, resource_type, resource_name):
    if prop == "ResourceRegion":
        if resource_type == "S3_BUCKET":
            return s3_client.get_bucket_location(Bucket=resource_name)[
                "LocationConstraint"
            ]
        elif resource_type == "DYNAMODB_TABLE":
            return dynamo_client.describe_table(TableName=resource_name)["Table"][
                "TableArn"
            ].split(":")[3]

    elif prop == "ResourceName":
        return resource_name


def getSessionProp(event, prop):
    if prop == "SessionProfileRegion":
        return json.loads(event["requestContext"]["authorizer"]["claims"]["address"])[
            "formatted"
        ]
    elif prop == "SessionEndRegion":
        return ipToCountryHelper(event["requestContext"]["identity"]["sourceIp"])


##==================================================================#
# Taint Tracking
def growlithe_extract_param_taint(taint_label, event):
    global GROWLITHE_INVOCATION_ID
    if "detail" in event.keys() and "bucket" in event["detail"]:
        default_id = (
            event["detail"]["bucket"]["name"]
            + event["detail"]["object"]["key"]
            + event["time"]
        )
    elif "Records" in event.keys():
        default_id = event["Records"][0]["eventSourceARN"]
    else:
        default_id = json.dumps(event)
    GROWLITHE_INVOCATION_ID = event.get("GROWLITHE_INVOCATION_ID", default_id)

    GROWLITHE_TAINTS[taint_label] = set(event.get("GROWLITHE_TAINTS", "").split(","))
    # dynamodb trigger
    if "Records" in event.keys():
        GROWLITHE_TAINTS[taint_label].add(
            f"DYNAMODB_TABLE:{event['Records'][0]['dynamodb']['Keys'][list(event['Records'][0]['dynamodb']['Keys'].keys())[0]]['S']}"
        )
    # S3 trigger
    if "detail" in event.keys() and "bucket" in event["detail"]:
        GROWLITHE_TAINTS[taint_label].add(
            f"S3_BUCKET:{event['detail']['bucket']['name']}:{event['detail']['object']['key']}"
        )
    # Extend taint labels for other trigger sources here


def growlithe_add_self_taint(taint_label):
    GROWLITHE_TAINTS[taint_label].update(taint_label, GROWLITHE_INVOCATION_ID)


def growlithe_add_file_taint(taint_label, file_name):
    GROWLITHE_TAINTS[taint_label].update(GROWLITHE_FILE_TAINTS[file_name])


def growlithe_add_s3_object_taint(taint_label, bucket, object_key):
    GROWLITHE_TAINTS[taint_label].update(
        set(bucket.Object(object_key).metadata.get("growlithe_taints", "").split(","))
    )


def growlithe_update_file_taint(file_name, taint_label):
    GROWLITHE_FILE_TAINTS[file_name].update(GROWLITHE_TAINTS[taint_label])


def growlithe_add_source_taint(sink_taint_label, source_taint_label):
    GROWLITHE_TAINTS[sink_taint_label].update(GROWLITHE_TAINTS[source_taint_label])


def growlithe_save_s3_taint(taint_label, bucket, object_key):
    object = bucket.Object(object_key)
    object.metadata.update(
        {"growlithe_taints": ",".join(GROWLITHE_TAINTS[taint_label])}
    )
    object.copy_from(
        CopySource={"Bucket": bucket.name, "Key": object_key},
        Metadata=object.metadata,
        MetadataDirective="REPLACE",
    )
