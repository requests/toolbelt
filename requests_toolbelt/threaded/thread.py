"""Module containing the SessionThread class."""
import threading
import uuid

import requests.exceptions as exc


class SessionThread(object):
    def __init__(self, initialized_session, job_queue, response_queue,
                 exception_queue):
        self._session = initialized_session
        self._jobs = job_queue
        self._create_worker()
        self._responses = response_queue
        self._exceptions = exception_queue

    def _create_worker(self):
        self._worker = threading.Thread(
            target=self._make_request,
            name=uuid.uuid4(),
        )
        self._worker.daemon = True
        self._worker._state = 0
        self._worker.start()

    def _make_request(self):
        method, kwargs = self._jobs.get()
        try:
            response = self._session.request(method, **kwargs)
        except exc.RequestException as e:
            self._exceptions.put((method, kwargs, e))
        else:
            self._responses.put((method, kwargs, response))
        finally:
            self._jobs.task_done()
