- Use `<benchmark_path>/output` directory to store dataflows.sarif after running `src/codeql/run.py`
- Define edge based policies in `<benchmark_path>/output/edge_policies.json`
```policies.json
[
    {
        "source_function": "LambdaFunctions/ImageProcessingRotate/lambda_function.py",
        "source": "LOCAL_FILE:tempfs",
        "read_policy": "allow",
        "sink_function": "LambdaFunctions/ImageProcessingRotate/lambda_function.py",
        "sink": "S3_BUCKET:imageprocessingbenchmark",
        "write_policy": "taintSetContains('imageprocessingbenchmark_sample_3.jpg')"
    },
    {
        "source_function": "LambdaFunctions/ImageProcessingRotate/lambda_function.py",
        "source": "S3_BUCKET:imageprocessingbenchmark",
        "read_policy": "isSuffix(PropDataObjectName, '.jpg')",
        "sink_function": "LambdaFunctions/ImageProcessingRotate/lambda_function.py",
        "sink": "LOCAL_FILE:tempfs",
        "write_policy": "isSuffix(PropDataObjectName, '.jpg')"
    }
]
```
- Run `src/graph/run.py` for the given benchmark to generate policy assertions