from enforcer.policy.template.growlithe import *

# Example usage
print(pyDatalog.ask("X == 1"))
assert pyDatalog.ask("X == 1") == set([(1,)])

print(pyDatalog.ask("(X == 1) & (Y == 2)"))
assert pyDatalog.ask("(X == 1) & (Y == 2)") == set([(1, 2)])

print(pyDatalog.ask('concat3(X, "hel", "lo")'))
assert pyDatalog.ask('concat3(X, "hel", "lo")') == set([("hello",)])

print(pyDatalog.ask("eq(Y, 1) & eq(Z, 3) & add(X, Y, Z)"))

# Listed in the order of occurence in the query
assert pyDatalog.ask("eq(Y, 1) & eq(Z, 3) & add(X, Y, Z)") == set([(1, 3, 4)])

print(pyDatalog.ask("eq(X, False) & not_(X, Y)"))
assert pyDatalog.ask("eq(X, False) & not_(X, Y)") == set([(False, True)])
