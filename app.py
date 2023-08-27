
from flask import Flask, request
from flask_cors import CORS
import re
import pickle
import pandas as pd
from datetime import datetime
from translate import line, dicts
from translate import max_bandwidth as max_values
# from maxes import max_values
app = Flask(__name__)
CORS(app)
@app.route('/', methods=['POST'])
def predict_all():  # put application's code here
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
    res = {key: value/max_values[key] for key, value in res.items()}
    reversed_translator = {v: k for k, v in dicts['station'].items()}
    res = {reversed_translator[k]: v for k, v in res.items()}
    return res
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('le.pkl', 'rb') as f:
    le = pickle.load(f)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
