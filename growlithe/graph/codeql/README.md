### Setup CodeQL
- Download and [install CodeQL CLI](https://docs.github.com/en/code-security/codeql-cli/getting-started-with-the-codeql-cli/setting-up-the-codeql-cli)
- Ensure CodeQL is added to your system PATH in the instructions above. For example, on Windows, you can add it via System Properties > Environment Variables.
- Fetch CodeQL dependencies for each language by navigating to the respective directory for the language which contains `qlpack.yml`, and run `codeql pack analyze`
