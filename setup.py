import os

from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

base = os.path.dirname(os.path.realpath(__file__))
requirement_path = base + '/requirements.txt'

install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = list(f.read().splitlines())

setup(
    name='aws-sqs-worker',
    version='0.0.1',
    description='AWS SQS Worker Module',
    license='MIT',
    long_description=long_description,
    url='https://github.com/epidemicsound/aws-sqs-worker.git',
    packages=['worker'],
    install_requires=install_requires
)
