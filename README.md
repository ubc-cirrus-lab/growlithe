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
`docker build -t growlithe .`

- Run an interactive session using:
`docker run -it growlithe bash`

### Docker with SSH
- Build the docker image using:
`docker build -t growlithe-study .`

- Run an interactive session using:
`docker run -it -p 2222:22 --name growlithe-study-1 growlithe-study`

- SSH to the docker container using the credentials in the docker image and the port used for forwarding:
`ssh participant1@localhost -p 2222`