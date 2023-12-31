from datetime import datetime, timezone, timedelta
from time import localtime, mktime

import psutil
import redis


REDIS_KEY = "timestamp"


def redis_connection(func):
    def wrapper(*args, **kwargs):
        with redis.Redis(host='redis_server', port=6379, decode_responses=True) as r:
            return func(r=r, *args, **kwargs)
    return wrapper


@redis_connection
def set_to_redis(r: redis.Redis, method: str = "GET", data: dict = None) -> bool:
    redis_data = {converter(data, method): int(mktime(localtime()))}  # data, score
    r.zadd(REDIS_KEY, redis_data)
    return True


def get_load(cpu: bool = False, ram: bool = False, swap: bool = False, method: str = "GET") -> dict:
    msg = {}

    msg.update({"cpu, %": psutil.cpu_percent(interval=0.1)}) if cpu else None
    msg.update({"ram, %": psutil.virtual_memory().percent}) if ram else None
    msg.update({"swap, %": psutil.swap_memory().percent}) if swap else None

    set_to_redis(method=method, data=msg)
    return msg


def converter(data: dict | str, method: str | None = None) -> dict | str:
    if isinstance(data, dict):
        """ from dict to str for redis"""
        string = f"timestamp;{int(mktime(localtime()))};method;{method}"
        for key, val in data.items():
            string += f";{key}/{val}"
        return string
    else:
        """ from redis from str for json"""
        data_list = data.split(";")
        timestamp = str(datetime.fromtimestamp(int(data_list[1])).strftime("%Y:%m:%d:%H:%M:%S"))

        response = {timestamp: {"method": data_list[3], "load": {}}}

        for item in data_list[4:]:
            item = item.split("/")
            response[timestamp]["load"][item[0]] = float(item[1])

        return response


@redis_connection
def get_from_redis(r: redis.Redis) -> list:
    data = r.zrange(REDIS_KEY, 0, -1)
    return [converter(item) for item in data]


@redis_connection
def remove_from_redis(r: redis.Redis, start: int | None = None, stop: int | None = None) -> int:
    if start and stop:
        return r.zremrangebyscore(REDIS_KEY, start, stop)  # start stop - unix timestamp
    return r.delete(REDIS_KEY)


@redis_connection
def get_temp_from_redis(r: redis.Redis) -> dict:
    temp_hum = str(r.get("temp")).split("/")[0]
    d_time = str(r.get("temp")).split("/")[1]
    return {"data": temp_hum, "last_msg": d_time, "current time": str(datetime.now(tz=timezone(timedelta(hours=3))).strftime('%d %b %Y %H:%M:%S'))}


@redis_connection
def set_temp_to_redis(r: redis.Redis, data: str) -> None:
    data_datetime = f"{data}/{datetime.now(tz=timezone(timedelta(hours=3))).strftime('%d %b %Y %H:%M:%S')}"
    return r.set("temp", data_datetime)
