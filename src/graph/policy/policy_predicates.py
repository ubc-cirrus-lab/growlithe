from pyDatalog import pyDatalog
from collections import defaultdict
import os

default_value = lambda: {os.environ['AWS_LAMBDA_FUNCTION_NAME']}
GROWLITHE_TAINTS = defaultdict(default_value)

# """
# Arithmetic/Relational predicates
# """
# def add(a, b, c) -> bool:
#     return a == b + c

# def sub(a, b, c) -> bool:
#     return a == b - c

# def mul(a, b, c) -> bool:
#     return a == b * c

# def div(a, b, c) -> bool:
#     return a == b / c

# def rem(a, b, c) -> bool:
#     return a == b % c

pyDatalog.load("""
    eq(X, Y) <= (X == Y)
    gt(X, Y) <= (X > Y)
    lt(X, Y) <= (X < Y)
""")
"""
String predicates
"""
@pyDatalog.predicate()
def isPrefix(x, y):
    if x.id.startswith(y.id):
        yield (x, y)

@pyDatalog.predicate()
def isSuffix(x, y):
    if x.id.endswith(y.id):
        yield (x, y)

# """Taint predicates"""
@pyDatalog.predicate()
def taintSetContains(node_id, label):
    global GROWLITHE_TAINTS
    if node_id.id in GROWLITHE_TAINTS:
        if label.id in GROWLITHE_TAINTS[node_id.id]:
            yield True

# Session properties are retrieved at runtime
# Retrieved values are set for the required datalog variable
# in the policy assertion at runtime
def getSessionProp(prop):
    if prop == "SessionTime":
        import time
        return round(time.time())
    elif prop == "SessionRegion":
        import os
        return os.environ['AWS_REGION']

def getMetaProp(prop, resource_type, resource_name):
    if prop == "MetaConduitRegion":
        if resource_type == "S3_BUCKET":
            import boto3
            client = boto3.client('s3')
            return client.get_bucket_location(Bucket=resource_name)['LocationConstraint']
    elif prop == "MetaConduitResourceName":
        return resource_name