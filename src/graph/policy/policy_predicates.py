from pyDatalog import pyDatalog
# pyDatalog.create_terms("sessionTimeIs, gt, lt, dynamoDbItemIs, dictHasKeyValue, add")

# """
# Arithmetic predicates
# """
# pyDatalog.create_terms("add, sub, mul, div, rem")

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


# """
# Relational predicates
# """

pyDatalog.load("""
    eq(X, Y) <= (X == Y)
    gt(X, Y) <= (X > Y)
    lt(X, Y) <= (X < Y)
""")
# @pyDatalog.predicate()
# def gt(a, b):
#     if a.id > b.id:
#         yield True


# @pyDatalog.predicate()
# def lt(a, b):
#     if a.id < b.id:
#         yield True

# # TODO: Add more relational predicates

"""
String predicates
"""
# pyDatalog.create_terms("isPrefix, isSuffix, hasSubstr")

# def isPrefix(str, pre) -> bool:
#     return str.startswith(pre)

@pyDatalog.predicate()
def isSuffix(x, y):
    if x.id.endswith(y.id):
        yield (x, y)

# def hasSubstr(str, substr) -> bool:
#     return str.find(substr) != -1

# """
# Dict predicates
# """
# pyDatalog.create_terms("dictHasKeyValue")
# def dictHasKeyValue(x, y, z) -> bool:
#     return x[y] == z

# """Session predicates"""
# pyDatalog.create_terms("sessionTimeIs")

# # TODO: Check how to use node information to retrieve properties like session time
    
# """Conduit predicates"""
# def conduitTypeIs(x):
#     pass

# """DynamoDB predicates"""
# def dynamoDbItemIs(x) -> bool:
#     pass
#     # return x == '{"allowedStartTimeStamp": "5"}'

# """Taint predicates"""
# def taintSetContains(x) -> bool:
#     pass
@pyDatalog.predicate()
def taintSetContains(node_id, label):
    global taints
    if node_id.id in taints:
        if label.id in taints[node_id.id]:
            yield True