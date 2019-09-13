import asyncio
import time
import traceback
import signal

import aiohttp

from . import request_client, settings


class QueueServiceWorker:
    def __init__(self, queue_name, handler, logger, liveness_callback=None):
        self.queue_name = queue_name
        self.handler = handler
        self.logger = logger
        self.liveness_callback = liveness_callback

        if settings.QUEUE_SERVICE_HOST is None:
            raise Exception(
                "aws-sqs-worker is missing a 'QUEUE_SERVICE_HOST' environment variable"
            )

        self.async_ = asyncio.iscoroutinefunction(handler)

        self.client = request_client.Client(settings.QUEUE_SERVICE_HOST)
        self.aiohttp_session = None

        self.run = True
        signal.signal(signal.SIGINT, self._handle_kill)
        signal.signal(signal.SIGTERM, self._handle_kill)

    def _handle_kill(self, signum, frame):
        self.logger.info("Got kill signal, stopping run...")
        self.run = False

    async def _get_queue_message(self):
        async with self.aiohttp_session.get(
            settings.QUEUE_SERVICE_HOST + "/get", params={"queue": self.queue_name}
        ) as response:
            response_data = await response.json()

            if response.status == 200:
                return response_data
            else:
                message_type = response_data["type"]
                if message_type == "NO_MESSAGES_ON_QUEUE":
                    self.logger.info(
                        "No messages in queue, sleeping",
                        extra=dict(sleep=settings.NO_MESSAGE_SLEEP_INTERVAL),
                    )
                    await asyncio.sleep(settings.NO_MESSAGE_SLEEP_INTERVAL)
                else:
                    raise Exception("Unhandled error {}", message_type)

    async def _delete_message(self, id):
        async with self.aiohttp_session.delete(
            settings.QUEUE_SERVICE_HOST + "/delete",
            params={"queue": self.queue_name, "id": id},
        ):
            return

    async def _work(self):
        self.aiohttp_session = aiohttp.ClientSession()
        try:
            while self.run:
                response_data = await self._get_queue_message()
                if response_data is not None:
                    await self._handle_queue_message(response_data)

                if self.liveness_callback is not None:
                    self.liveness_callback()

            self.logger.info("Work loop exited")
        finally:
            await self.aiohttp_session.close()
            self.aiohttp_session = None


    async def _handle_queue_message(self, response_data):
        message_receive_time = time.time()

        payload = response_data["payload"]
        if self.async_:
            await self.handler(payload)
        else:
            # todo: this will run a slow sync method in the event loop, the event loop might complain.
            # todo: consider moving it into a thread.
            self.handler(payload)

        process_time = time.time() - message_receive_time
        await self._delete_message(response_data["id"])

        if process_time > 15 * 60:
            self.logger.error(
                "Queue message took too long to process",
                extra=dict(
                    type=payload.get("type", "not set"),
                    queue=self.queue_name,
                    process_time=process_time,
                ),
            )
        else:
            self.logger.info(
                "Queue message processed",
                extra=dict(
                    type=payload.get("type", "not set"),
                    queue=self.queue_name,
                    process_time=process_time,
                ),
            )

    def start(self):
        while True:
            try:
                asyncio.run(self._work())
            # todo: an exception in an async task probably shouldn't kill the work loop without awaiting the
            # pending tasks
            except Exception as e:
                restart_delay = 1
                self.logger.error(
                    "Worker crashed, restarting in {}s".format(restart_delay),
                    extra=dict(
                        exception_type=type(e),
                        exception=str(e),
                        traceback=traceback.format_exc(),
                    ),
                )
                time.sleep(restart_delay)
            else:
                return
