from flask import Flask, request, jsonify

from utils import get_load, set_to_redis, get_from_redis, remove_from_redis

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def get_data():
    if request.method == 'GET':
        data = get_load(cpu=True, ram=True, swap=True)
        set_to_redis(method="GET", data=data)
        return jsonify(data)

    if request.method == 'POST':
        try:
            load = request.json['load']
        except KeyError:
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
        data = get_load(cpu=cpu, ram=ram, swap=swap)
        set_to_redis(method="POST", data=data)
        return jsonify(data)


@app.route("/redis", methods=['GET', 'POST'])
def get_redis():
    if request.method == 'GET':
        return jsonify(get_from_redis())

    if request.method == 'POST':
        try:
            timestamp = request.json['timestamp']
        except KeyError:
            return jsonify({'removed': remove_from_redis()})

        start = int(timestamp[0])
        stop = int(timestamp[1])
        print(timestamp, stop, start)
        return "OK"  # jsonify({'removed': remove_from_redis(start, stop)})


if __name__ == '__main__':
    app.run()
