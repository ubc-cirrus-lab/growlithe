### [Alternative Setup] Using Docker Image
- Build the docker image using:
`docker build -t growlithe .`

- Run an interactive session using:
`docker run -it growlithe bash`

## Contributing
- Install Growlithe in edit mode using `pip install -e .`.
- Configure `common/dev_config.py` for development knobs.
- Update `get_defaults` in `growlithe/config.py` with required paths for debugging.
- Run `cli/analyze` or `cli/apply` directly or using a debugger.

## Style
Growlithe uses Black for automatic code formatting to maintain consistent style, Pylint for general linting, and pydocstyle for specific documentation checks.
Run the following before commits.

- Black: `black .`
- Pylint: `pylint growlithe`
- pydocstyle: `pydocstyle growlithe`

> Alternatively, install pre-commit to run automatically before commits:
`pre-commit install`