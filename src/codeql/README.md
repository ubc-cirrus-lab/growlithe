### Getting flows using CodeQL

- Follow main README.md to setup codeql and create a database using codeql.py

- Understand `modules/Growlithe` for abstractions for the analysis
- Model new libraries in `modules/Concepts` following structures defined in `modules/Core` for modelling
- Add new data sources/sinks in `modules/Sources` or `modules/Sinks`
- Modify `queries/Config` to restrict to required files
- Configure run.py to recreate_database, paths and queries to run

#### Code Standard Practices
- Add reusable functions to utils and reuse
- Avoid adding path checks separately in each module. Add all hard coded strings in Config
- Write independent modules and call them in test query files, then import and reuse the same in integrated queries
