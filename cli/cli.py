import click
from .build import build as build_command
from .deploy import deploy as deploy_command
from .analyze import analyze as analyze_command
from .apply import apply as apply_command
from .config import Config


@click.group()
@click.option(
    "--config", default="growlithe_config.yaml", help="Path to the configuration file"
)
@click.pass_context
def cli(ctx, config):
    """Growlithe CLI for building, deploying, and managing applications."""
    ctx.obj = Config(config)


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
    analyze_command(config)


@cli.command()
@click.pass_obj
def apply(config):
    """Apply Growlithe policies to the application."""
    click.echo("Applying Growlithe policies...")
    apply_command(config)


if __name__ == "__main__":
    cli()
