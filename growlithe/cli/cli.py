import click
from growlithe.cli.build import build as build_command
from growlithe.cli.deploy import deploy as deploy_command
from growlithe.cli.analyze import analyze as analyze_command
from growlithe.cli.apply import apply as apply_command
from growlithe.config import get_config


@click.group()
@click.option(
    "--config", default="growlithe_config.yaml", help="Path to the configuration file"
)
@click.pass_context
def cli(ctx, config):
    """Growlithe CLI for building, deploying, and managing applications."""
    ctx.obj = get_config(config)


@cli.command()
@click.pass_obj
def build(config):
    """Build the application."""
    click.echo("Building the application...")
    build_command(config)


@cli.command()
@click.pass_obj
def deploy(config):
    """Deploy the application."""
    click.echo("Deploying the application...")
    if click.confirm("Do you want to proceed with deployment?"):
        deploy_command(config)
    else:
        click.echo("Deployment cancelled.")


@cli.command()
@click.pass_obj
def analyze(config):
    """Analyze the application and generate dataflow graphs and policy templates."""
    click.echo(
        f"Analyzing the application {config.app_name} with Growlithe path {config.growlithe_path}."
    )
    analyze_command(config)


@cli.command()
@click.pass_obj
def apply(config):
    """Apply Growlithe policies to the application."""
    click.echo("Applying Growlithe policies...")
    apply_command(config)


if __name__ == "__main__":
    cli()
