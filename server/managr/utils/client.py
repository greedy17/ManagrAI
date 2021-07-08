import requests
import time
import logging
import httpx

from urllib.parse import urlencode, quote_plus
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


logger = logging.getLogger("managr")
########
# general usage
# client = HttpClient().client
#
# configuration
# retry_total (int) number of retries when connection timesout default 3
# backoff_factor (int) factor for backoff on retry (this is exponential)
#    {backoff factor} * (2 ** ({number of total retries} - 1)) default is 1
#    ** to remove retry make backoff_factor 0
# status_forcelist (arr[int]) an array with statuses to retry on
# method_whitelist (arr[str]) protected methods to attempt retry (post) by default is not included
# timeout (int) timeout unresponsive calls default 5
#
#######


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = 10
        if "timeout" in kwargs:
            # if the user has specified a timeout override default
            timeout = kwargs.get("timeout", None)
            if timeout:
                self.timeout = kwargs["timeout"]
            del kwargs["timeout"]

        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


# TimeoutHTTPAdapter(timeout=2.5)


class HttpClient:
    def __init__(self, *args, **kwargs):
        # retries default set to 10 but disabled because default backoff is set to 0
        self.retry_total = kwargs.get("retry_total", 3)
        self.backoff_factor = kwargs.get("backoff_factor", 1)
        self.status_forcelist = kwargs.get("status_forcelist", [429, 500, 502, 503, 504])
        self.method_whitelist = kwargs.get("method_whitelist", ["HEAD", "GET", "OPTIONS"])
        self.timeout = kwargs.get("timeout", None)

    @property
    def retries(self):
        return Retry(
            total=self.retry_total,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            method_whitelist=self.method_whitelist,
        )

    @property
    def client(self):
        client = requests.Session()
        adapter = TimeoutHTTPAdapter(timeout=self.timeout, max_retries=self.retries)
        client.mount("https://", adapter)
        client.mount("http://", adapter)
        return client


Client = httpx.Client(timeout=20)
