from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='aws-sqs-worker',
    version='0.0.2',
    description='AWS SQS Worker Module',
    license='MIT',
    long_description=long_description,
    url='https://github.com/epidemicsound/aws-sqs-worker.git',
    packages=['worker'],
    install_requires=['requests']
)
