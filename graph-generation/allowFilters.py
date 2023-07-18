def isEndUser(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return subject_attributes.end_user == policyConstants[0]

def userHasRole(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return subject_attributes.role == policyConstants[0]

def hasLocation(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return environment_attributes.location == policyConstants[0]

def inTimeRange(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return policyConstants[0] <= environment_attributes.time <= policyConstants[1]