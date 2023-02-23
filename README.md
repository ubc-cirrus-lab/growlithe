# serverless-compliance


## Installing CodeQL
Follow the CodeQL setup guide in [here](https://docs.github.com/en/code-security/codeql-cli/using-the-codeql-cli/getting-started-with-the-codeql-cli).


## Creating CodeQL Database
Create the CodeQL database by running this command:
```bash
codeql database create <database-name> --language=python
```
This will create a folder with the provided name containing the CodeQL's database. Note that if there exists a folder with the same name, the command will fail. So to update the database, you need to use the `--overwrite` flag while creating the database.

## Installing Query Dependencies
To install dependencies for the queries, run this command:
```bash
codeql pack install
```
This will install all the dependencies stated in the `qlpack.yml` file.

## Running CodeQL Queries
> For testing purposes it is easier to work with CodeQL integration with VSCode.

If you want to use the CLI, use this command to run a query on the database you just created:
```bash
codeql database analyze <database-name> --format=csv --output=<output-file-name> <query-file-path>
```
