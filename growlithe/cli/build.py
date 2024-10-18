"""
Module for building SAM (Serverless Application Model) applications.

This module provides functionality to build SAM applications using the AWS SAM CLI.
It includes error handling and output formatting for better user experience.
"""

import os
import subprocess
import click


def build(config):
    """
    Run 'sam build' command to build the SAM application.
    TODO: Extend this to make the interface build other types of application package

    This function executes the 'sam build' command in the appropriate directory,
    either the current directory or the Growlithe-generated template directory.
    It handles the build process, captures output, and provides formatted feedback.

    Args:
        config: Configuration object containing application settings.

    Raises:
        SystemExit: If the build process fails or if the SAM CLI is not installed.
    """
    command = ["sam", "build"]

    if os.path.isfile(os.path.join(config.growlithe_path, "template.yaml")):
        click.echo("Building the application with Growlithe-generated template...")
        os.chdir(config.growlithe_path)

    try:
        # Run the sam build command
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        # Print the output
        click.echo(result.stdout)

        if result.stderr:
            click.echo("Warnings/Errors:", color="yellow")
            click.echo(result.stderr)

        click.echo("Build completed successfully!", color="green")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during build: {e}", color="red")
        if e.output:
            click.echo("Build output:")
            click.echo(e.output)
        if e.stderr:
            click.echo("Error output:")
            click.echo(e.stderr)
        exit(1)
    except FileNotFoundError:
        click.echo(
            "Error: 'sam' command not found. Make sure AWS SAM CLI is installed and in your PATH.",
            color="red",
        )
        exit(1)
