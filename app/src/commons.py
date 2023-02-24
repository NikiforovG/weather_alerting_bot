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
    url: str, params: dict[str, Any], request_timeout: int = 2, max_tries: int = 5
) -> requests.Response:
    retry_strategy = Retry(
        total=max_tries,
        backoff_factor=0.1,
        status_forcelist=[408, 429, 500, 503, 504, 520, 522, 523, 524],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as session:
        session.mount("https://", adapter)  # type:ignore
        session.mount("http://", adapter)  # type:ignore
        resp = requests.get(url, params, timeout=request_timeout)

    try:
        resp.raise_for_status()
    except HTTPError:
        log.critical(resp.text)

    return resp


def get_tomorrow_9am_cet() -> datetime:
    """
    Returns a datetime object representing 9am Central European Time (CET) tomorrow.
    """
    now = datetime.now()
    cet_tz = pytz.timezone('CET')
    tomorrow = now.date() + timedelta(days=1)
    # Create a datetime object representing 9am CET tomorrow
    tomorrow_9am: datetime = cet_tz.localize(datetime.combine(tomorrow, datetime.min.time()).replace(hour=9))
    return tomorrow_9am
