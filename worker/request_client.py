import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(
        retries=3,
        # Will sleep for {backoff factor} * (2 ^ ({number of total retries} - 1))
        backoff_factor=1,
        status_forcelist=(500, 502, 504),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session


class Client:
    def __init__(self, base_url, default_headers={}, timeout=None):
        self.base_url = base_url
        self.default_headers = default_headers
        self.timeout = self.timeout

    def get(self, path):
        return requests_retry_session().get(
            url='{}{}'.format(self.base_url, path),
            headers=self.default_headers,
            timeout=self.timeout
        )

    def post(self, path, json):
        return requests_retry_session().post(
            url='{}{}'.format(self.base_url, path),
            json=json,
            headers=self.default_headers,
            timeout=self.timeout
        )

    def put(self, path, json):
        return requests_retry_session().put(
            url='{}{}'.format(self.base_url, path),
            json=json,
            headers=self.default_headers,
            timeout=self.timeout
        )

    def delete(self, path, json):
        return requests_retry_session().delete(
            url='{}{}'.format(self.base_url, path),
            json=json,
            headers=self.default_headers,
            timeout=self.timeout
        )
