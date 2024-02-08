# Session properties are retrieved at runtime
# Retrieved values are set for the required datalog variable
# in the policy assertion at runtime
def getSessionProp(prop):
    import time
    if prop == "SessionTime":
        return round(time.time())

