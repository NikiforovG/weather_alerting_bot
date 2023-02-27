from datetime import datetime, timedelta
from typing import Any

import pytz
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util.retry import Retry

from src import getLogger

log = getLogger(__name__)


def request_with_retries(
    url: str, params: dict[str, Any] | None = None, request_timeout: int = 2, max_tries: int = 5
) -> requests.Response:
    retry_strategy = Retry(
        total=max_tries,
        backoff_factor=0.1,
        status_forcelist=[408, 429, 500, 503, 504, 520, 522, 523, 524],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as session:
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        resp = requests.get(url, params, timeout=request_timeout)

    try:
        resp.raise_for_status()
    except HTTPError:
        log.critical(resp.text)

    return resp


def get_next_9am_cet() -> datetime:
    """
    Returns a datetime object representing next 9am Central European Time (CET).
    """
    now = datetime.now(pytz.timezone('CET'))
    today_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now < today_9am:
        return today_9am
    return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
