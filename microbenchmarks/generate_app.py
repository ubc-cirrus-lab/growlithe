import os
import shutil
import json
import yaml
from tqdm import tqdm
from yaml import SafeDumper, dump

def create_directory(directory):
    """Create a directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)

def copy_lambda_functions(source_file, dest_dir, n):
    """
    Copy the Lambda function n times.
    
    Args:
    source_file (str): Path to the source Lambda function file.
    dest_dir (str): Directory to copy the files to.
    n (int): Number of copies to create.
    """
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Error: Source file '{source_file}' not found.")
    
    create_directory(dest_dir)
    
    for i in tqdm(range(1, n+1), desc="Copying files", unit="file"):
        dest_file = f'sens-remote-{i}.py'
        dest_path = os.path.join(dest_dir, dest_file)
        
        try:
            shutil.copy2(source_file, dest_path)
        except IOError as e:
            print(f"\nError copying file {dest_file}: {e}")

    print(f"\nSuccessfully created {n} copies in {dest_dir}")

def generate_state_machine(n):
    """
    Generate the state machine definition for a linear chain of Lambda functions.
    
    Args:
    n (int): Number of Lambda functions in the chain.
    
    Returns:
    dict: State machine definition.
    """
    state_machine = {
        "Comment": "A linear chain of Lambda functions",
        "StartAt": f"sens-remote-1",
        "States": {}
    }

    for i in range(1, n+1):
        state_name = f"sens-remote-{i}"
        state = {
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "OutputPath": "$.Payload",
            "Parameters": {
                "Payload.$": "$",
                "FunctionName": f"${{{state_name}FunctionArn}}"
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 1,
                    "MaxAttempts": 3,
                    "BackoffRate": 2
                }
            ],
            "Next": f"sens-remote-{i+1}" if i < n else None,
            "End": True if i == n else False
        }
        if state["Next"] is None:
            del state["Next"]
        state_machine["States"][state_name] = state

    return state_machine

def write_state_machine(state_machine, file_path):
    """
    Write the state machine definition to a JSON file.
    
    Args:
    state_machine (dict): State machine definition.
    file_path (str): Path to write the JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(state_machine, f, indent=2)
    print(f"State machine definition created in {file_path}")


class GetAtt:
    """Helper class for YAML representation of !GetAtt in CloudFormation."""
    def __init__(self, function_name):
        self.function_name = function_name

def generate_sam_template(n):
    """
    Generate the SAM template for the serverless application.
    
    Args:
    n (int): Number of Lambda functions.
    
    Returns:
    dict: SAM template definition.
    """
    sam_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Description": "Serverless State Machine App",
        "Resources": {
            "StateMachine": {
                "Type": "AWS::Serverless::StateMachine",
                "Properties": {
                    "DefinitionUri": "state_machine.asl.json",
                    "DefinitionSubstitutions": {},
                    "Policies": [
                        {
                            "LambdaInvokePolicy": {
                                "FunctionName": "*"
                            }
                        },
                        {
                            "S3CrudPolicy": {
                                "BucketName": "sensitivity-test-gr"
                            }
                        }
                    ]
                }
            }
        }
    }

    for i in range(1, n+1):
        function_name = f"SensRemoteFunction{i}"
        state_name = f"sens-remote-{i}"
        
        sam_template["Resources"][function_name] = {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "CodeUri": "src/",
                "Handler": f"sens-remote-{i}.lambda_handler",
                "Runtime": "python3.10",
                "Policies": [
                    {
                        "S3CrudPolicy": {
                            "BucketName": "sensitivity-test-gr"
                        }
                    }
                ],
                "Environment": {
                    "Variables": {
                        "BUCKET_NAME": "sensitivity-test-gr"
                    }
                }
            }
        }
        
        # Add DefinitionSubstitutions for each function's ARN
        sam_template["Resources"]["StateMachine"]["Properties"]["DefinitionSubstitutions"][f"{state_name}FunctionArn"] = GetAtt(f"{function_name}.Arn")

    return sam_template

def get_att_representer(dumper, data):
    """Custom YAML representer for GetAtt objects."""
    return dumper.represent_scalar('!GetAtt', data.function_name)

def write_sam_template(sam_template, file_path):
    """
    Write the SAM template to a YAML file.
    
    Args:
    sam_template (dict): SAM template definition.
    file_path (str): Path to write the YAML file.
    """
    SafeDumper.add_representer(GetAtt, get_att_representer)
    
    with open(file_path, 'w') as f:
        dump(sam_template, f, Dumper=SafeDumper, default_flow_style=False)
    
    print(f"SAM template updated in {file_path}")

def generate_app_n_copies(n):
    """
    Generate the complete serverless application with n copies of the Lambda function.
    
    Args:
    n (int): Number of Lambda function copies to create.
    """
    print(f"Generating application with {n} copies...")
    source_file = 'sens-remote.py'

    os.makedirs('SampleApp', exist_ok=True)
    functions_dir = os.path.join('SampleApp', 'src')
    state_machine_file = os.path.join('SampleApp', 'state_machine.asl.json')
    sam_template_file = os.path.join('SampleApp', 'template.yaml')

    copy_lambda_functions(source_file, functions_dir, n)

    state_machine = generate_state_machine(n)
    write_state_machine(state_machine, state_machine_file)

    sam_template = generate_sam_template(n)
    write_sam_template(sam_template, sam_template_file)

def main():
    """Main function to run the script."""
    try:
        n = int(input("Enter the number of copies to create: "))
        if n < 1:
            raise ValueError("Number of copies must be at least 1")
        generate_app_n_copies(n)

    except ValueError as e:
        print(f"Invalid input: {e}")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()