import subprocess
import click

def deploy(config):
    """Run 'sam deploy' in the current directory."""
    command = ['sam', 'deploy']
    click.echo("Deploying the application with SAM...")
    
    try:
        # Run the sam deploy command
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        
        # Print the output
        click.echo(result.stdout)
        
        if result.stderr:
            click.echo("Warnings/Errors:", err=True)
            click.echo(result.stderr, err=True)
        
        click.echo("Deployment completed successfully!", color='green')
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during deployment: {e}", color='red')
        if e.output:
            click.echo("Deployment output:", err=True)
            click.echo(e.output, err=True)
        if e.stderr:
            click.echo("Error output:", err=True)
            click.echo(e.stderr, err=True)
        exit(1)
    except FileNotFoundError:
        click.echo("Error: 'sam' command not found. Make sure AWS SAM CLI is installed and in your PATH.", color='red')
        exit(1)