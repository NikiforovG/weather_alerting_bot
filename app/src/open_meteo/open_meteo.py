from datetime import datetime
from typing import Any

from requests.exceptions import JSONDecodeError

from src import getLogger
from src.commons import request_with_retries

log = getLogger(__name__)


def get_weather(date: str) -> dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 52.37,
        "longitude": 4.84,
        "hourly": "temperature_2m",
        "current_weather": True,
        "start_date": date,
        "end_date": date,
        "timezone": "CET",
    }
    resp = request_with_retries(url, params)
    try:
        res: dict[str, Any] = resp.json()
    except JSONDecodeError as e:
        res = {}
        log.warning(e)
    return res


def message_from_weather(weather: dict[str, Any]) -> str:
    message = (
        "Location: Amsterdam\n"
        f"Date: {weather['current_weather']['time'].split('T')[0]}\n"
        f"Time: {weather['current_weather']['time'].split('T')[1]}\n"
        f"Temperature: {weather['current_weather']['temperature']}{weather['hourly_units']['temperature_2m']}\n"
        f"Wind speed: {weather['current_weather']['windspeed']}\n"
    )
    return message


def report_weather() -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    weather_dict = get_weather(date)
    if len(weather_dict.keys()) == 0:
        message = "Sorry we could not get weather for you"
    else:
        message = message_from_weather(get_weather(date))
    return message
