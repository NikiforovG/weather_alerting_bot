from datetime import datetime, timedelta
from typing import Any

import pytz
from requests.exceptions import JSONDecodeError
from telegram.ext import ContextTypes

from src import getLogger
from src.commons import request_with_retries

log = getLogger(__name__)

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: Light intensity",
    53: "Drizzle: Moderate intensity",
    55: "Drizzle: Dense intensity",
    56: "Freezing Drizzle: Light intensity",
    57: "Freezing Drizzle: Dense intensity",
    61: "Rain: Slight intensity",
    63: "Rain: Moderate intensity",
    65: "Rain: Heavy intensity",
    66: "Freezing Rain: Light intensity",
    67: "Freezing Rain: Heavy intensity",
    71: "Snow fall: Slight intensity",
    73: "Snow fall: Moderate intensity",
    75: "Snow fall: Heavy intensity",
    77: "Snow grains",
    80: "Rain showers: Slight intensity",
    81: "Rain showers: Moderate intensity",
    82: "Rain showers: Violent intensity",
    85: "Snow showers: Slight intensity",
    86: "Snow showers: Heavy intensity",
    95: "Thunderstorm: Slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_weather(date: datetime) -> dict[str, Any]:
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=52.37"
        "&longitude=4.84"
        "&hourly=temperature_2m,precipitation_probability,precipitation,windspeed_10m,weathercode"
        "&timezone=CET"
        f"&start_date={date.strftime('%Y-%m-%d')}"
        f"&end_date={(date + timedelta(days=1)).strftime('%Y-%m-%d')}"
    )
    resp = request_with_retries(url)
    try:
        res: dict[str, Any] = resp.json()
    except JSONDecodeError as e:
        res = {}
        log.warning(e)
    return res


def message_for_current_weather(weather: dict[str, Any]) -> str:
    timezone = pytz.timezone(weather["timezone"])
    now = datetime.now(timezone)
    if now.minute > 30:
        now += timedelta(hours=1)
    now_str = now.strftime("%Y-%m-%dT%H:00")
    idx = weather["hourly"]["time"].index(now_str)
    message = (
        "Location: Amsterdam\n"
        f"Date: {now_str.split('T')[0]}\n"
        f"Time: {now_str.split('T')[1]}\n"
        f"Temperature: {weather['hourly']['temperature_2m'][idx]}{weather['hourly_units']['temperature_2m']}\n"
        f"Precipitation: {weather['hourly']['precipitation'][idx]}mm\n"
        f"Precipitation probability: {weather['hourly']['precipitation_probability'][idx]}%\n"
        f"Wind speed: {weather['hourly']['windspeed_10m'][idx]}\n"
        f"Weather code: {WMO_CODES[weather['hourly']['weathercode'][idx]]}\n"
    )
    return message


async def report_weather(chat_id: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    weather_dict = get_weather(datetime.now())
    if len(weather_dict.keys()) == 0:
        message = "Sorry we could not get weather for you"
    else:
        message = message_for_current_weather(weather_dict)
    await context.bot.send_message(chat_id=chat_id, text=message)
    log.info("id %s: weather update sent", chat_id)
