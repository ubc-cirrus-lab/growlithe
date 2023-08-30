import argparse
import logging

from src.cloud_utility import step_function_helper, cloudformation_helper
from src.growlithe import Growlithe
from src.logger import logger


def main():
    parser = argparse.ArgumentParser()
    required_names = parser.add_argument_group('required named arguments')
    required_names.add_argument("-p", "--path", help="Application Directory Path", required=True)
    parser.add_argument("--sfn", help="State Machine Definition Path")
    parser.add_argument("--cfn", help="CloudFormation Template Path")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(level=logging.DEBUG)

    sfn = args.sfn
    cfn = args.cfn
    app_path = args.path

    growlithe = Growlithe(app_path)

    if sfn:
        growlithe.resource_extractor = step_function_helper.handler_extractor
        growlithe.template_path = sfn
    elif cfn:
        growlithe.resource_extractor = cloudformation_helper.handler_extractor
        growlithe.template_path = cfn
    else:
        logger.critical("A CloudFormation or state machine template is necessary")
        exit(1)

    growlithe.run()
