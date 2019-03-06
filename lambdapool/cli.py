import click
import os

from .function import LambdaFunction

@click.group()
def cli():
    pass

@cli.command()
@click.option('--requirements', '-r', type=click.Path(exists=True))
@click.argument('function_name', nargs=1)
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
def create(function_name, paths, requirements):
    click.echo('=== Creating lambdapool function ===')
    func = LambdaFunction(function_name, paths, requirements)
    func.create()
    click.echo(f'=== Succesfully created lambdapool function {function_name} ===')

@cli.command()
def list():
    click.echo('Listing all lambdapool functions...')

@cli.command()
@click.option('--requirements', '-r', required=True)
@click.argument('function_name', nargs=1)
@click.argument('paths', nargs=-1)
def update(function_name, paths, requirements):
    click.echo('Updating lambdapool function...')
    click.echo(f'Function: {function_name}')
    click.echo(f'Paths: {paths}')
    click.echo(f'Requirements: {requirements}')

@cli.command()
@click.argument('function_name', nargs=1)
def delete(function_name):
    click.echo('Deleting lambdapool function...')
    click.echo(f'Function: {function_name}')
