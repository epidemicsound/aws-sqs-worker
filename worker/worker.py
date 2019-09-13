import time
import traceback
import signal

from . import (
    request_client,
    settings
)


class QueueServiceWorker:
    def __init__(self, queue_name, handler, logger, liveness_callback=None):
        self.queue_name = queue_name
        self.handler = handler
        self.logger = logger
        self.liveness_callback = liveness_callback

        if settings.QUEUE_SERVICE_HOST is None:
            raise Exception("aws-sqs-worker is missing a 'QUEUE_SERVICE_HOST' environment variable")

        self.client = request_client.Client(settings.QUEUE_SERVICE_HOST)

        self.run = True
        signal.signal(signal.SIGINT, self._handle_kill)
        signal.signal(signal.SIGTERM, self._handle_kill)

    def _handle_kill(self, signum, frame):
        self.logger.info('Got kill signal, stopping run...')
        self.run = False

    def _get_message(self):
        return self.client.get('/get?queue={}'.format(self.queue_name))

    def _delete_message(self, id):
        return self.client.delete(
            '/delete', {
                'queue': self.queue_name,
                'id': id
            }
        )

    def _work(self):
        while self.run:
            response = self._get_message()
            response_data = response.json()

            if response.status_code == 200:
                self._handle_queue_message(response_data)
            else:
                message_type = response_data['type']
                if message_type == 'NO_MESSAGES_ON_QUEUE':
                    self.logger.info('No messages in queue, sleeping',
                                     extra=dict(sleep=settings.NO_MESSAGE_SLEEP_INTERVAL))
                    time.sleep(settings.NO_MESSAGE_SLEEP_INTERVAL)
                else:
                    raise Exception('Unhandled error {}', message_type)

            if self.liveness_callback is not None:
                self.liveness_callback()

        self.logger.info('Work loop exited')

    def _handle_queue_message(self, response_data):
        message_receive_time = time.time()

        id = response_data['id']
        payload = response_data['payload']
        self.handler(payload)
        self._delete_message(id)

        process_time = time.time() - message_receive_time
        if process_time > 15 * 60:
            self.logger.error(
                'Queue message took too long to process',
                extra=dict(
                    type=payload.get('type', 'not set'),
                    queue=self.queue_name,
                    process_time=process_time,
                )
            )
        else:
            self.logger.info(
                'Queue message processed',
                extra=dict(
                    type=payload.get('type', 'not set'),
                    queue=self.queue_name,
                    process_time=process_time,
                )
            )


    def start(self):
        try:
            self._work()
        except Exception as e:
            restart_delay = 1
            self.logger.error(
                'Worker crashed, restarting in {}s'.format(restart_delay),
                extra=dict(
                    exception_type=type(e),
                    exception=str(e),
                    traceback=traceback.format_exc()
                )
            )
            time.sleep(restart_delay)
            self.start()
