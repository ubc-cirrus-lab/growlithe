# Growlithe

### Config
- Change app configuration in `common/app_config.py`.
- Change growlithe configuration in `common/tasks_config.py`.
    - For the first run, set `CREATE_CODEQL_DB` and `RUN_CODEQL_QUERIES` to `True`.

### Usage
- Install dependencies: `pip install -r requirements.txt`.

- Run main.py

### Using Docker Image
- Build the docker image using:
`docker build -t your-image-name .`

- Run an interactive session using:
`docker run -it growlithe bash`