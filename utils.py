from datetime import datetime
from time import localtime, mktime

import psutil
import redis


def get_load(cpu: bool = False, ram: bool = False, swap: bool = False) -> dict:
    msg = {}

    msg.update({"cpu, %": psutil.cpu_percent(interval=0.1)}) if cpu else None
    msg.update({"ram, %": psutil.virtual_memory().percent}) if ram else None
    msg.update({"swap, %": psutil.swap_memory().percent}) if swap else None

    return msg


def converter(data: dict | str, method: str | None = None) -> dict | str:
    if isinstance(data, dict):
        """ from dict to str for redis"""
        string = f"timestamp;{int(mktime(localtime()))};method;{method}"
        for key, val in data.items():
            string += f";{key};{val}"
        return string
    else:
        """ from redis from str for json"""
        response = {}
        data_list = data.split(";")
        timestamp = str(datetime.fromtimestamp(int(data_list[1])))

        response = {timestamp: {"method": data_list[3], "load": {}}}
        data = data_list[4:]
        for index in range(0, len(data), 2):
            response[timestamp]["load"][data[index]] = data[index + 1]
        return response


def set_to_redis(method: str = "GET", data: dict = None) -> bool:
    r = redis.Redis(host='localhost', port=6379)

    redis_data = {converter(data, method): int(mktime(localtime()))}  # data, score
    r.zadd('timestamp', redis_data)
    return True


def get_from_redis() -> list:
    r = redis.Redis(host='localhost', port=6379)
    data = r.zrange('timestamp', 0, -1)
    return [converter(item.decode("utf-8")) for item in data]


def remove_from_redis(start: int | None = None, stop: int | None = None) -> int:
    r = redis.Redis(host='localhost', port=6379)
    if start and stop:
        return r.zremrangebyscore('timestamp', start, stop)  # start stop - unix timestamp
    else:
        return r.delete('timestamp')
