import os
import time
import traceback
import signal
import gc

from util.request_client import Client


QUEUE_SERVICE_HOST = os.getenv('QUEUE_SERVICE_HOST')
INTERVAL = int(os.getenv('INTERVAL', 10))


class QueueServiceWorker:
    def __init__(self, queue_name, handler, logger):
        self.queue_name = queue_name
        self.handler = handler
        self.logger = logger
        self.client = Client(QUEUE_SERVICE_HOST)

        self.run = True
        signal.signal(signal.SIGINT, self._handle_kill)
        signal.signal(signal.SIGTERM, self._handle_kill)

        self.working_loops = 0

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
            message = self._get_message()
            response = message.json()

            message_receive_time = time.time()
            if message.status_code == 200:
                id = response['id']
                payload = response['payload']
                self.handler(payload)
                self._delete_message(id)

                process_time = time.time() - message_receive_time
                if process_time > 15*60:
                    self.logger.error(
                        'Queue message took too long to process',
                        type=payload.get('type', 'not set'),
                        queue=self.queue_name,
                        process_time=process_time,
                    )
                else:
                    self.logger.info(
                        'Queue message processed',
                        type=payload.get('type', 'not set'),
                        queue=self.queue_name,
                        process_time=process_time,
                    )

            else:
                message_type = response['type']
                if message_type == 'NO_MESSAGES_ON_QUEUE':
                    self.logger.info(f'No messages in queue, sleeping for {INTERVAL}s')
                    time.sleep(INTERVAL)
                else:
                    raise Exception('Unhandled error {}', message_type)

            self.working_loops += 1
            if self.working_loops % 1000 == 0:
                # Trigger GC to clean up before hard memory limit is triggered
                self.logger.info('Invoking garbage collect', loop=self.working_loops)
                gc.collect()

        self.logger.info('Work loop exited')

    def start(self):
        try:
            self._work()
        except Exception as e:
            restart_delay = 1
            self.logger.error(
                'Worker crashed, restarting in {}s'.format(restart_delay),
                exception_type=type(e),
                exception=str(e),
                traceback=traceback.format_exc()
            )
            time.sleep(restart_delay)
            self.start()
