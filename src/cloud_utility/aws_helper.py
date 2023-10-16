import boto3


def get_account_id(profile):
    session = boto3.Session(profile_name=profile)
    sts = session.client('sts')
    return sts.get_caller_identity()['Account']


def get_region(profile):
    session = boto3.Session(profile_name=profile)
    return session.region_name


def generate_iam_policy(policy):
    # TODO: implement
    pass
