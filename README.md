# serverless-compliance


## Installing CodeQL
Follow the CodeQL setup guide in [here](https://docs.github.com/en/code-security/codeql-cli/using-the-codeql-cli/getting-started-with-the-codeql-cli).


## Creating CodeQL Database
Create the CodeQL database by running this command:
```bash
codeql database create <database-name> --language=<language>
```
`language` is the programming language of the source code, e.g. `python`. Running the command will create a folder with the provided name containing the CodeQL's database. Note that if there exists a folder with the same name, the command will fail. So to update the database, you need to use the `--overwrite` flag while creating the database. For more information refer to [Creating CodeQL databases documentation](https://docs.github.com/en/code-security/codeql-cli/using-the-codeql-cli/creating-codeql-databases)

## Installing Query Dependencies
Queries rely on CodeQL packages to run. These packages should be defined in a specific file named `qlpack.yml`. For more information refer to [CodeQL packs documentation](https://docs.github.com/en/code-security/codeql-cli/codeql-cli-reference/about-codeql-packs). To install dependencies for the queries, run this command:
```bash
codeql pack install
```
This will install all the dependencies stated in the `qlpack.yml` file.

## Running CodeQL Queries
> For testing purposes it is easier to work with CodeQL [integration with VSCode](#codeql-vscode-integration).

If you want to use the CLI, use this command to run a query on the database you just created:
```bash
codeql database analyze <database-name> --format=csv --output=<output-file-name> <query-file-path>
```

## CodeQL VSCode Integration
You first need to install the [CodeQL extension](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-codeql) on VSCode. You can then choose the folder containing the CodeQL database you created in the previous sections in VSCode. Then you can simply run the queries by right-clicking on the query files and selecting the "CodeQL: Run Queries in Selected Files" option.

### Setup Keybinding for faster testing
You can create a custom keybinding in VSCode to run the queries with more ease. To do so, press `Ctrl+Shift+P` (`Cmd+Shift+P` on Mac) in VSCode to open the Command Palette. Type "CodeQL: Run Query on Selected Databases". A command should appear which you can use to run the command. By clicking the gear icon beside the command you can define a custom keybinding (e.g., `Ctrl+Shift+Enter`) to run it in the future.