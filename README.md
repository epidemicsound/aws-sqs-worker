# aws-sqs-worker
This repository represents worker interaction with Amazon SQS. A worker encapsulates a piece of code written to perform a specific task. In this model, the worker receives the task to perform in form of a message from a queue. This is a very common form of architecture where the sender gets decoupled from the worker through an asynchronous messaging queue.

This module exposes the necessary API to create a worker which starts polling messages from a specific queue in Amazon SQS.

## Installation:
We can install the library through github by writing the dependency in `requirements.txt` as:

```
https://github.com/epidemicsound/aws-sqs-worker/releases/download/v0.0.2/aws_sqs_worker-0.0.2-py3-none-any.whl
```

Replace 0.0.2 with the desired version, on both places in the url!

If using pipenv, you can also run `pipenv install https://github.com/epidemicsound/aws-sqs-worker/releases/download/v0.0.2/aws_sqs_worker-0.0.2-py3-none-any.whl`.

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

#### Liveness callback
As an option (as of v0.0.2) it is possible to add a liveless callback function to the worker.
```python
import worker
from pathlib import Path

mylogger = logging.get_logger(__name__)

myworker = SpecificWorker()
queue_name = 'queue_to_pull_messages_from'
    
def my_liveness_callback():
    Path('/worker/alive.txt').touch()

queue_worker = worker.QueueServiceWorker(
    queue_name=queue_name,
    logger=mylogger,
    handler=myworker.handle_payload,
    liveness_callback=my_liveness_callback
)  
```

If added, the liveness callback will be triggered last in each of the workers cycles of checking and processing
an available message in the connected queue. The liveness probe also triggers even if the connected queue happens
to be empty. In this case the liveness probe will be triggered after the `NO_MESSAGE_SLEEP_INTERVAL`, just before a 
new cycle of checking and processing messages in the queue begins. 

## Release

Use semantic versioning for this library. When bumping the version, please update the version in:

* setup.py
* this readme

Merge into master.

Generate a new wheel (after bumping the version and being on the new master) by running `make build-release`.

Make sure that there is a new wheel named `aws_sqs_worker-<version>-py3-none-any.whl` and is in the `dist` folder.

Create a github release and upload the wheel file to the release.