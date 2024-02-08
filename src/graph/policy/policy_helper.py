def getSessionProp(prop):
    import time
    if prop == "SessionTime":
        return round(time.time())

