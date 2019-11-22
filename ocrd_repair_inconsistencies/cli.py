import click

from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_repair_inconsistencies.ocrd_repair_inconsistencies import RepairInconsistencies


@click.command()
@ocrd_cli_options
def ocrd_repair_inconsistencies(*args, **kwargs):
    return ocrd_cli_wrap_processor(RepairInconsistencies, *args, **kwargs)
