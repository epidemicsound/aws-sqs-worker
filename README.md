# aws-sqs-worker
This repository represents worker interaction with Amazon SQS. A worker encapsulates a piece of code written to perform a specific task. In this model, the worker receives the task to perform in form of a message from a queue. This is a very common form of architecture where the sender gets decoupled from the worker through an asynchronous messaging queue.

This module exposes the necessary API to create a worker which starts polling messages from a specific queue in Amazon SQS.

## Installation:
We can install the library through github by writing the dependency in `requirements.txt` as:

```
https://raw.githubusercontent.com/epidemicsound/aws-sqs-worker/master/wheels/aws_sqs_worker-0.0.1-py3-none-any.whl
```

Replace 0.0.1 with the desired version!

If using pipenv, you can also run `pipenv install https://raw.githubusercontent.com/epidemicsound/aws-sqs-worker/master/wheels/aws_sqs_worker-0.0.1-py3-none-any.whl`.

## Steps necessary to create a worker for the process:

1. Create a worker class with a method to handle the payload from the queue that the worker is created for. An example is as follows:

```python
class SpecificWorker(object):
  
  def __init__(self):
    pass

  def handle_payload(self, payload):
    # code to handle the payload received from SQS

```

2. Once we have created our specific worker, we need to attach it to an instance of `QueueServiceWorker` which handles all the code of connecting to the queue and polling messages from the queue.

```python

import worker

mylogger = logging.get_logger(__name__)

myworker = SpecificWorker()
queue_name = 'queue_to_pull_messages_from'

queue_worker = worker.QueueServiceWorker(
  queue_name=queue_name,
  logger=mylogger,
  handler=myworker.handle_payload)

queue_worker.start()
```

This will then start the queue polling mechanism by the `queue_worker`. As soon as message appears on the `queue_name`, it invokes the `handle_payload` function of `myworker` instance.

## Release

Use semantic versioning for this library. When bumping the version, please update the version in:

* setup.py
* this readme

Make sure you generate a new wheel (after bumping the version) by running `make build-release`.

Make sure that the new wheel is named `aws_sqs_worker-<version>-py3-none-any.whl` and is in the `wheels` folder..

Include the wheel in git.