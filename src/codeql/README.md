### Taint Analysis with CodeQL

- Follow main README.md to setup codeql and create a database
- Add new sources in [Sources.qll](Sources.qll) by adding another function within the module and add as a OR separated function in `get_sources()`
- Similarly add new sinks in [Sinks.qll](Sinks.qll)
- Change filepaths and configuration in [Config.qll](utils/Config.qll)
- Run [dataflows.ql](./dataflows.ql) to get valid dataflows from defined sources to sinks. Similarly run [flowPaths.ql](flowPaths.ql) to get valid paths with intermediate nodes

#### Code Standard Practices
- Add reusable functions to utils and reuse
- Avoid adding path checks separately in each module. Add all hard coded strings in Config
- Write independent modules and call them in test query files, then import and reuse the same in integrated queries