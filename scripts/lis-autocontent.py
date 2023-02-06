"""Entry point executable for the CLI. Gets added to PATH on python setup.py install"""
#!/usr/bin/env python3

import click
import lis_cli


@click.group()
def cli():
    """CLI entry for LIS-autocontent"""


#    pass


cli.add_command(lis_cli.populate_jekyll)
cli.add_command(lis_cli.populate_jbrowse2)
cli.add_command(lis_cli.populate_blast)
cli.add_command(lis_cli.populate_dscensor)
cli()  # invoke cli
