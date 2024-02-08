- Use `<benchmark_path>/output` directory to store dataflows.sarif after running `src/codeql/run.py`
- Define edge based policies in `<benchmark_path>/output/edge_policies.json`
```policies.json
[
    {
        "flow_from": "RESOURCE:LOCAL_FILE:tempfs",
        "flow_from_policy": "allow",
        "flow_to": "RESOURCE:S3_BUCKET:imageprocessingbenchmark",
        "flow_to_policy": "taintSetContains('RESOURCE:S3_BUCKET:imageprocessingbenchmark')"
    },
    {
        "flow_from": "RESOURCE:S3_BUCKET:imageprocessingbenchmark",
        "flow_from_policy": "isSuffix(PropDataObjectName, '.jpg')",
        "flow_to": "RESOURCE:LOCAL_FILE:tempfs",
        "flow_to_policy": "isSuffix(PropDataObjectName, '.jpg')"
    }
]
```
- Run `src/graph/run.py` for the given benchmark to generate policy assertions