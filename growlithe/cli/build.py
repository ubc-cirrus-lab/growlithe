import os
import subprocess
import click


def build(config):
    """Run 'sam build' in the current directory."""
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
