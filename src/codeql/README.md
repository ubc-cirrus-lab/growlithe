### Taint Analysis with CodeQL

- Follow main README.md to setup codeql and create a database using codeql.py

- Understand `modules/Growlithe` for abstractions for the analysis
- Model new libraries in `modules/Concepts` following structures defined in `modules/Core` for modelling
- Add new data sources/sinks in `modules/Sources` or `modules/Sinks`
- Modify `queries/Config` to restrict to required files
- Run required queries from `queries` directory

#### Code Standard Practices
- Add reusable functions to utils and reuse
- Avoid adding path checks separately in each module. Add all hard coded strings in Config
- Write independent modules and call them in test query files, then import and reuse the same in integrated queries

Run queries using `codeql.py` using 
```python
from src.codeql.codeql import CodeQL

benchmarks_root_path = "D:\\Code\\serverless-compliance\\benchmarks"
benchmark = "test"
benchmark_path = f'{benchmarks_root_path}\\{benchmark}\\'
codeql_db_path = f'{benchmarks_root_path}\\{benchmark}\\testdb\\'
codeql_output_path = f'{benchmarks_root_path}\\{benchmark}\\output\\'

# Creates database and analyzes functions
# CodeQL.analyze(benchmark_path) 
CodeQL._analyze_functions(benchmark_path, codeql_db_path, codeql_output_path)

```