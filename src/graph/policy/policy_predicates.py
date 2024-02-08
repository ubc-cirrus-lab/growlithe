from pyDatalog import pyDatalog

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
    global taints
    if node_id.id in taints:
        if label.id in taints[node_id.id]:
            yield True