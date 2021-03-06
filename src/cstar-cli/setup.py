from setuptools import setup

setup(
   name='cstar-cli',
   version='0.0.1',
   description='Cstar Command Line Interface',
   author='CSTAR Team',
   author_email='cstar@pagopa.it',
   packages=['cstar.cli', 'cstar.cli.bpd', 'cstar.cli.rtd', 'cstar.cli.tae', 'cstar.cli.sender'],
   install_requires=['cstar-cli-core'], #external packages as dependencies
   scripts=[
      'cst',
   ]
)