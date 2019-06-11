#!/usr/bin/env python
# -*- coding:utf-8 -*-

import functools
from datetime import datetime

from pyowm import OWM

import utils


# Decorators

def load_config(func):
    @functools.wraps(func)
    def wrapper_load_config(string, entities):
        payload = dict()
        payload["string"] = string
        payload["entities"] = entities

        api_key = utils.config("api_key")
        pro = utils.config("pro")
        payload["temperature_units"] = utils.config("temperature_units")
        payload["wind_speed_units"] = utils.config("wind_speed_units")

        if (payload["temperature_units"] != "celsius") and (payload["temperature_units"] != "fahrenheit"):
            return utils.output("end", "invalid_temperature_units", utils.translate("invalid_temperature_units"))

        if payload["wind_speed_units"] == "meters per seconds":
            payload["wind_speed_units_response"] = payload["wind_speed_units"]
            payload["wind_speed_units"] = "meters_sec"
        elif payload["wind_speed_units"] == "miles per hour":
            payload["wind_speed_units_response"] = payload["wind_speed_units"]
            payload["wind_speed_units"] = "miles_hour"
        else:
            return utils.output("end", "invalid_wind_speed_units", utils.translate("invalid_wind_speed_units"))

        if pro:
            payload["owm"] = OWM(api_key, subscription_type="pro")
        else:
            payload["owm"] = OWM(api_key)

        return func(payload)
    return wrapper_load_config


def acquire_weather(func):
    @functools.wraps(func)
    def wrapper_acquire_weather(payload):
        for item in payload["entities"]:
            if item["entity"] == "city":
                utils.output("inter", "acquiring", utils.translate("acquiring"))

                payload["city"] = item["sourceText"].title()
                try:
                    payload["observation"] = payload["owm"].weather_at_place(payload["city"])
                except:
                    tmp = payload["city"]

                    es = tmp.find(' ')
                    vi = tmp.find(',')
                    pt = tmp.find('.')

                    if es != -1:
                        tmp = tmp[:es]
                    elif vi != -1:
                        tmp = tmp[:es]
                    elif pt != -1:
                        tmp = tmp[:es]
                    payload["city"] = tmp
                    try:
                        payload["observation"] = payload["owm"].weather_at_place(payload["city"])
                    except:
                        return utils.output("end", "not_found", utils.translate("not_found"))
                payload["wtr"] = payload["observation"].get_weather()

                return func(payload)

        return utils.output("end", "request_error", utils.translate("request_error"))

    return wrapper_acquire_weather


def future(func):
    @functools.wraps(func)
    def wrapper_acquire_future_weather(payload):
        for item in payload["entities"]:
            if item["entity"] == "date":
                payload["date"] = item['resolution']['strValue']
                payload["date"] = payload["date"]+" 12:00+00"
                #return func(payload)
            elif item["entity"] == "datetime":
                payload["date"] = item['resolution']['values'][0]['value']
                return func(payload)
            elif item["entity"] == "city":
                utils.output("inter", "acquiring", utils.translate("acquiring"))

                payload["city"] = item["sourceText"].title()
                try:
                    payload["observation"] = payload["owm"].daily_forecast(payload["city"], limit=6)
                except:
                    tmp = payload["city"]
                    es = tmp.find(' ')
                    vi = tmp.find(',')
                    pt = tmp.find('.')

                    if es != -1:
                        tmp = tmp[:es]
                    elif vi != -1:
                        tmp = tmp[:es]
                    elif pt != -1:
                        tmp = tmp[:es]
                    payload["city"] = tmp

                    try:
                        payload["observation"] = payload["owm"].daily_forecast(payload["city"], limit=6)
                    except:
                        utils.output("inter", "city", utils.translate("city", {"city": payload["city"]}))
                        return utils.output("end", "not_found", utils.translate("not_found"))
                payload["wtr"] = payload["observation"].get_weather_at(payload["date"])
                return func(payload)

        return utils.output("end", "request_error", utils.translate("request_error"))

    return wrapper_acquire_future_weather

# Methods


@load_config
@acquire_weather
def current_weather(payload):
    """
    Get the current weather.
    """

    detailed_status = payload["wtr"].get_detailed_status()
    temperatures = payload["wtr"].get_temperature(payload["temperature_units"])   # {"temp_max": 10.5, "temp": 9.7, "temp_min": 9.0}
    humidity = payload["wtr"].get_humidity()
    #wind = payload["wtr"].get_wind(payload["wind_speed_units"])   # {"speed": 4.6, "deg": 330}

    return utils.output(
        "end",
        "current_weather",
        utils.translate(
            "current_weather",
            {
                "detailed_status": detailed_status.capitalize(),
                "city": payload["city"],
                "temperature": temperatures["temp"],
                "temperature_units": payload["temperature_units"].capitalize(),
                "humidity": humidity
            }
        )
    )


@load_config
@future
def future_weather(payload):
    """
    Get the weather few days in future
    """
    detailed_status = payload["wtr"].get_detailed_status()
    temperatures = payload["wtr"].get_temperature(payload["temperature_units"])   # {"temp_max": 10.5, "temp": 9.7, "temp_min": 9.0}
    humidity = payload["wtr"].get_humidity()
    #wind = payload["wtr"].get_wind(payload["wind_speed_units"])   # {"speed": 4.6, "deg": 330}

    return utils.output(
        "end",
        "future_weather",
        utils.translate(
            "future_weather",
            {
                "detailed_status": detailed_status.capitalize(),
                "city": payload["city"],
                "date": payload["date"],
                "temperature": temperatures["temp"],
                "temperature_units": payload["temperature_units"].capitalize(),
                "humidity": humidity
            }
        )
    )


@load_config
@acquire_weather
def temperature(payload):
    """
    Get the current temperature.
    """

    temperatures = payload["wtr"].get_temperature(payload["temperature_units"])   # {"temp_max": 10.5, "temp": 9.7, "temp_min": 9.0}

    return utils.output(
        "end",
        "temperature",
        utils.translate(
            "temperature",
            {
                "city": payload["city"],
                "temperature": temperatures["temp"],
                "temperature_units": payload["temperature_units"].capitalize()
            }
        )
    )


@load_config
@acquire_weather
def humidity(payload):
    """
    Get the current humidity.
    """

    humidity = payload["wtr"].get_humidity()

    return utils.output(
        "end",
        "humidity",
        utils.translate(
            "humidity",
            {
                "city": payload["city"],
                "humidity": humidity
            }
        )
    )


@load_config
@acquire_weather
def wind(payload):
    """
    Get the current wind speed and direction.
    """

    wind = payload["wtr"].get_wind(payload["wind_speed_units"])

    return utils.output(
        "end",
        "wind",
        utils.translate(
            "wind",
            {
                "city": payload["city"],
                "wind_speed": wind["speed"],
                "wind_speed_units_response": payload["wind_speed_units_response"],
                "wind_direction": wind["deg"]
            }
        )
    )


@load_config
@acquire_weather
def sunrise(payload):
    """
    Get when the sun rises.
    """

    dt = payload["wtr"].get_sunrise_time("date")

    return utils.output("end", "sunrise", utils.translate("sunrise", {"time": dt.strftime("%H:%M:%S"), "city": payload["city"]}))


@load_config
@acquire_weather
def sunset(payload):
    """
    Get when the sun sets.
    """

    dt = payload["wtr"].get_sunset_time("date")

    return utils.output("end", "sunset", utils.translate("sunset", {"time": dt.strftime("%H:%M:%S"), "city": payload["city"]}))
