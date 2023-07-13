def isEndUser(subject_attributes, object_attributes, environment_attributes, policyConstants):
    return subject_attributes.end_user == policyConstants.end_user