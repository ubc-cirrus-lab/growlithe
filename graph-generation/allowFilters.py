import policyLib

def isEndUser(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return subject_attributes.end_user == policyConstants[0]

def userHasRole(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return subject_attributes.role == policyConstants[0]

def hasLocation(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return environment_attributes.location == policyConstants[0]

def inTimeRange(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return policyConstants[0] <= environment_attributes.time <= policyConstants[1]

def isTeacher(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return policyLib.is_teacher(subject_attributes.username, subject_attributes.login_token)

def isRecordOwner(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return policyLib.is_record_owner(subject_attributes.username, subject_attributes.login_token, subject_attributes.requested_username)
