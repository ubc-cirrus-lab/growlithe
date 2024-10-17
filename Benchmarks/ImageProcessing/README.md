# Moderated Image Processing Application

## Overview

This application is an AWS Step Functions-based workflow for processing and moderating images. It uses a series of Lambda functions to transform, filter, and optionally blur images before tagging and storing them.

The benchmark is originally from [Serverless FaaS Workbench](https://github.com/ddps-lab/serverless-faas-workbench), and was converted to a workflow in [Unfaasener](https://github.com/ubc-cirrus-lab/unfaasener/tree/main/benchmarks/ImageProcessingWorkflow)

## Deployment

1. Install the AWS SAM CLI:
```
pip install aws-sam-cli
```

2. Update resources with custom names as required in `src`, `image_processing_sf.json` and `template.yaml`.

3. Replace the `template.yaml` and source code files with the provided ones.

4. Build the SAM application:
```
sam build
```

5. Deploy the SAM application:
```
sam deploy --guided
```

## Usage

To use this application:

1. Upload an image to the designated S3 bucket by updating and running the `scripts/upload_s3.py` script.
2. The state machine will automatically process the image, and store the output in the desired S3 bucket.