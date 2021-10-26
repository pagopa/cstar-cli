from setuptools import setup

setup(
   name='cstar-cli',
   version='0.0.1',
   description='Cstar Command Line Interface',
   author='Giovanni Mancini',
   author_email='giovanni.mancini@pagopa.it',
   packages=['cstar'],  #same as name
   install_requires=[''], #external packages as dependencies
   scripts=[
            'cst',
           ]
)