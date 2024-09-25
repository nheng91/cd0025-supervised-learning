import signal

from contextlib import contextmanager

import requests

DELAY = INTERVAL = 4 * 60  # interval time in seconds
MIN_DELAY = MIN_INTERVAL = 2 * 60
KEEPALIVE_URL = "https://nebula.udacity.com/api/v1/remote/keep-alive"
TOKEN_URL = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/keep_alive_token"
TOKEN_HEADERS = {"Metadata-Flavor": "Google"}
def _request_handler(headers):
    def _handler(signum, frame):
        requests.request("POST", KEEPALIVE_URL, headers=headers)
    return _handler

@contextmanager
def active_session(delay=DELAY, interval=INTERVAL):
    """
    Example:
    from workspace_utils import active_session
    with active_session():
        # do long-running work here
    """
    try:
        response = requests.request("GET", TOKEN_URL, headers=TOKEN_HEADERS)
        response.raise_for_status()  # Ensure the request was successful
        token = response.text
        headers = {'Authorization': "STAR " + token}
    except requests.exceptions.RequestException as e:
        # Handle the error (log it, raise it, or set default headers)
        print(f"Failed to get token: {e}")
        headers = {'Authorization': "STAR default-token"}  # Fallback to a default
    delay = max(delay, MIN_DELAY)
    interval = max(interval, MIN_INTERVAL)
    original_handler = signal.getsignal(signal.SIGALRM)
    try:
        signal.signal(signal.SIGALRM, _request_handler(headers))
        signal.setitimer(signal.ITIMER_REAL, delay, interval)
        yield
    finally:
        signal.signal(signal.SIGALRM, original_handler)
        signal.setitimer(signal.ITIMER_REAL, 0)
 
 
def keep_awake(iterable, delay=DELAY, interval=INTERVAL):
    """
    Example:
 
    from workspace_utils import keep_awake
 
    for i in keep_awake(range(5)):
        # do iteration with lots of work here
    """
    with active_session(delay, interval): yield from iterable
