from datetime import datetime

from flask import Flask, request, jsonify, Response
from werkzeug.exceptions import UnsupportedMediaType

from utils import get_load, get_from_redis, remove_from_redis, get_temp_from_redis, set_temp_to_redis

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def get_data():
    if request.method == 'GET':
        data = get_load(cpu=True, ram=True, swap=True, method="GET")
        return jsonify(data)

    if request.method == 'POST':
        try:
            load = request.json['load']
        except (UnsupportedMediaType, KeyError):
            return {
                "ERR": "Не верный̆ формат данных",
                "message": "Пример запроса {'load': ['cpu', 'ram', 'swap']}"}

        cpu = False
        ram = False
        swap = False

        for item in load:
            item = item.strip().lower()
            if item == 'cpu':
                cpu = True
            elif item == 'ram':
                ram = True
            elif item == 'swap':
                swap = True
        data = get_load(cpu=cpu, ram=ram, swap=swap, method="POST")
        return jsonify(data)


@app.route("/redis", methods=['GET', 'POST'])
def get_redis():
    if request.method == 'GET':
        return jsonify(get_from_redis())

    if request.method == 'POST':
        try:
            timestamp = request.json['timestamp']
        except (UnsupportedMediaType, KeyError):
            return jsonify({'removed': remove_from_redis()})

        try:
            start = datetime.strptime(timestamp[0], "%Y:%m:%d:%H:%M:%S")
            stop = datetime.strptime(timestamp[1], "%Y:%m:%d:%H:%M:%S")
        except (ValueError, IndexError):
            return {
                "ERR": "Не верный̆ формат данных",
                "message": "Пример запроса {'timestamp': ['2023:01:01:00:00:00', '2023:05:01:00:00:00']}"}

        return jsonify({'removed': remove_from_redis(start=int(datetime.timestamp(start)),
                                                     stop=int(datetime.timestamp(stop)))})


@app.route("/temp", methods=['GET', 'POST'])
def get_set_temp():
    if request.method == 'GET':
        return jsonify(get_temp_from_redis())

    if request.method == 'POST':
        data = request.json['temp']
        set_temp_to_redis(data=data)
        return Response(status=200)


if __name__ == '__main__':
    app.run()
