# Growlithe
Growlithe is tool that integrates with the serverless application development lifecycle to enable compliance with data policies.
Growlithe allows specifying declarative policies on an application's  dataflow graph, and enforces them with static and runtime checks.

Our 2025 IEEE S&P paper provides more details about the design of Growlithe:
- [Growlithe: A Developer-Centric Compliance Tool for Serverless Applications](#)

## Setup
- Create a new virtual environment with python v3.10.
- Install Growlithe as a pip package by running `pip install .` in the root directory. Refer to [CONTRIBUTING.md](/CONTRIBUTING.md) for installing an editable version instead.


## Usage
- Navigate to your serverless application, create a file `growlithe_config.yaml` with the following configuration:
```yaml
app_path: <Relative path to the main application>
app_name: <Name of the application>
src_dir: <Source code of the application relative to app_path>
app_config_path: <Relative path to the application configuration>
app_config_type: <Type of application config like SAM, Terraform>
cloud_provider: <cloud provider of the application like AWS, GCP>
```
- Use cli to run Growlithe on the application.
- `growlithe analyze` to analyze the source code.
- Configure `<app>/growlithe/policy_spec.json` with the required policies.
- `growlithe apply` to regenerate the source code with the applied policies.
