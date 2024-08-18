from flask import Flask, request
from flask_cors import CORS
import pickle
import pandas as pd
from datetime import datetime
from translate import line, dicts
from functools import lru_cache
from maxes import max_values
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/', methods=['GET'])
def get():
    print('hello world!')
    return 'hello'
@app.route('/', methods=['POST'])
def post():  # put application's code here
    data = request.get_json()
    datetime = data['datetime']
    pred = predict_all(datetime)
    return {'stations': {key: value for key, value in pred.items()}}

def process_datetime(date):
    date = date + ':00'
    parsed_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    is_weekend = 1 if parsed_datetime.weekday() in [5, 6] else 0
    month = parsed_datetime.month
    hour = parsed_datetime.hour
    day_of_week = parsed_datetime.weekday()
    day = parsed_datetime.day
    return is_weekend, month, hour, day_of_week, day

@lru_cache(maxsize=30)
def predict_all(datetime):
    res = {}
    for station in line:
        is_weekend, month, hour, day_of_week, day = process_datetime(datetime)
        line_of_station = dicts['line'][line[station]]
        station = dicts['station'][station]
        res[station] = model.predict(
            pd.DataFrame(
                data=[[hour, line_of_station, station, month, day,  day_of_week, is_weekend]],
                columns=model.feature_names_in_
            )
        )[0]
    res = {key: value for key, value in res.items()}
    reversed_translator = {v: k for k, v in dicts['station'].items()}
    res = {reversed_translator[k]: min(1, v/max_values[k]) for k, v in res.items()}
    return res
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('le.pkl', 'rb') as f:
    le = pickle.load(f)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')

