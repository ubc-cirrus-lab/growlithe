# Growlithe
Growlithe is tool that integrates with the serverless application development lifecycle to enable compliance with data policies.
Growlithe allows specifying declarative policies on an application's  dataflow graph, and enforces them with static and runtime checks.

Our 2025 IEEE S&P paper provides more details about the design of Growlithe:
- [Growlithe: A Developer-Centric Compliance Tool for Serverless Applications](#)

## Setup
- Install Growlithe as a pip package. In the root directory, run `pip install .`
- Navigate to your serverless application, create a file `growlithe_config.yaml` with the following configuration:
```yaml
app_path: <Relative path to the main application>
app_name: <Name of the application>
src_dir: <Source code of the application relative to app_path>
app_config_path: <Relative path to the application configuration>
app_config_type: <Type of application config like SAM, Terraform>
```
- Use cli to run Growlithe on the application.
- `growlithe analyze` to analyze the source code.
- Configure `<app>/growlithe/policy_spec.json` with the required policies.
- `growlithe apply` to regenerate the source code with the applied policies.

### [Alternatively] Using Docker Image
- Build the docker image using:
`docker build -t growlithe .`

- Run an interactive session using:
`docker run -it growlithe bash`
