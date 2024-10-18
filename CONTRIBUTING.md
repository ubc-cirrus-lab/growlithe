### [Alternative Setup] Using Docker Image
- Build the docker image using:
`docker build -t growlithe .`

- Run an interactive session using:
`docker run -it growlithe bash`

## Contributing
- Install Growlithe and CodeQL dependencies by following [README.md](/README.md)
- Configure `common/dev_config.py` for development knobs.
- Update `get_defaults` in `growlithe/config.py` with required paths for debugging.
- Run `cli/analyze` or `cli/apply` directly or using a debugger.

## Style
Growlithe uses Black for automatic code formatting to maintain consistent style.
Run the following before commits in the root directory.
- Black: `black .`

> Alternatively, install pre-commit to run automatically before commits:
`pre-commit install`