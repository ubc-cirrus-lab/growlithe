import policyLib

def is_end_user(subject_attributes, object_attributes, environment_attributes, policy_constants):
    return subject_attributes.end_user == policy_constants[0]

def user_has_role(subject_attributes, object_attributes, environment_attributes, policy_constants):
    return subject_attributes.role == policy_constants[0]

def has_location(subject_attributes, object_attributes, environment_attributes, policy_constants):
    return environment_attributes.location == policy_constants[0]

def in_time_range(subject_attributes, object_attributes, environment_attributes, policy_constants):
    return policy_constants[0] <= environment_attributes.time <= policy_constants[1]
  
def isTeacher(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return policyLib.is_teacher(subject_attributes.username, subject_attributes.login_token)

def isRecordOwner(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return policyLib.is_record_owner(subject_attributes.username, subject_attributes.login_token, subject_attributes.requested_username)
