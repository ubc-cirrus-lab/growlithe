- Use `<benchmark_path>/output` directory to store dataflows.sarif after running `src/codeql/run.py`
- Define edge based policies in `<benchmark_path>/output/edge_policies.json`
```policies.json
[
    {
        "source": "RESOURCE:LOCAL_FILE:tempfs",
        "read_policy": "allow",
        "sink": "RESOURCE:S3_BUCKET:imageprocessingbenchmark",
        "write_policy": "taintSetContains('RESOURCE:S3_BUCKET:imageprocessingbenchmark')"
    },
    {
        "source": "RESOURCE:S3_BUCKET:imageprocessingbenchmark",
        "read_policy": "isSuffix(PropDataObjectName, '.jpg')",
        "sink": "RESOURCE:LOCAL_FILE:tempfs",
        "write_policy": "isSuffix(PropDataObjectName, '.jpg')"
    }
]
```
- Run `src/graph/run.py` for the given benchmark to generate policy assertions