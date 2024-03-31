import click


@click.command()
@click.option("-n", "--name", prompt="Your name", help="Name to greet")
def clifunction(name):
    """Greets a user who gives his name as input"""
    click.echo(f"Hello {name}!")
