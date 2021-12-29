class CstarCli():
  def __init__(self, cli_name, parser):
    return

def get_cli():
    from cstar.cli.core.parser import cstar_command_parser

    return CstarCli(cli_name='cst', parser=cstar_command_parser)