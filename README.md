# Growlithe
Growlithe is tool that integrates with the serverless application development lifecycle to enable compliance with data policies.
Growlithe allows specifying declarative policies on an application's  dataflow graph, and enforces them with static and runtime checks.

Our 2025 IEEE S&P paper provides more details about the design of Growlithe:
- [Growlithe: A Developer-Centric Compliance Tool for Serverless Applications](https://cirrus.ece.ubc.ca/papers/sp25_growlithe.pdf)

## Setup
- Create a [new virtual environment](https://docs.python.org/3/library/venv.html) with python v3.10, and activate it.
```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

- Install CodeQL and dependencies by following [/growlithe/graph/codeql/README.md](/growlithe/graph/codeql/README.md)
- Install Growlithe by running `pip install -e .` in the root directory.
> Note: You may be prompted to install Microsoft Visual C++ Build Tools if using Windows. Download from [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/).

- If using JavaScript functions, ensure Node.js is installed and install dependencies by running:
`npm install --prefix growlithe/graph/adg/js`


## Usage
Activate the virtual environment, then:
- Navigate to your serverless application, create a file `growlithe_config.yaml` with the following configuration:
```yaml
app_path: <Relative path to the main application>
app_name: <Name of the application>
src_dir: <Source code of the application relative to app_path>
app_config_path: <Relative path to the application configuration>
app_config_type: <Type of application config - [SAM, Terraform]>
cloud_provider: <cloud provider of the application - [AWS, GCP]>
```

Use Growlithe CLI on the application:
- `growlithe analyze` to analyze the source code.
- Configure `<app_path>/growlithe_<app_name>/policy_spec.json` with the required policies.
- `growlithe apply` to regenerate the source code with the applied policies.

## Acknowledgments

This work was supported in part by the Natural Sciences and Engineering Research Council of Canada (NSERC)
[DGDND-2021-02961, GPIN-2021-03714, DGECR-202100462], the funding from the Innovation for Defence Excellence and Security (IDEaS) Program of
the Department of National Defense [MN3-011], and the UBC STAIR (Support for Teams to Advance Interdisciplinary Research) Program.
