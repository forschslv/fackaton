from functools import cache

import flask
import pandas as pd
import os
path_to_data = 'data.csv'
from init_data1 import get_data_by_time, render_table
if os.path.exists(path_to_data):
    data = pd.read_csv(path_to_data)
else:
    data = pd.DataFrame()

app = flask.Flask(__name__)



@app.route("/api/get_data/<tour_num>/<time>")
def data_ret(tour_num, time):
    if tour_num not in {'1', '2'}:
        flask.abort(400)
    else:
        if f"{time}.html" not in os.listdir('Материалы/Первый тур' if tour_num == 1 else 'Материалы/Второй тур'):
            flask.abort(404)
        else:
            return get_data_by_time(int(tour_num), time).to_json(index=False, orient='split')

@app.route("/api/get_data_html/<tour_num>/<time>")
def data_ret1(tour_num, time):
    if tour_num not in {'1', '2'}:
        flask.abort(400)
    else:
        if f"{time}.html" not in os.listdir('Материалы/Первый тур' if tour_num == 1 else 'Материалы/Второй тур'):
            flask.abort(404)
        else:
            flask.abort(500, "NOT IMPLEMENTED")



@app.route('/api/get_possible')
@cache
def possible():
    f = []
    for i in os.scandir('Материалы/Первый тур'):
        f.append(int(i.name[:i.name.find('.')]))
    s = []
    for i in os.scandir('Материалы/Второй тур'):
        s.append(int(i.name[:i.name.find('.')]))

    return {'1': f,
            '2': s}


@app.route("/")
def index():
    return flask.render_template("index.html")
APP_SETTINGS = {
    "site_name": "ХАКАТОН",
    "currency_symbol": "ERROR",
}
@app.context_processor
def inject_settings():
    return dict(cfg=APP_SETTINGS)

@app.route('/catalog')
def catalog():
    return flask.render_template('catalog.html')

if __name__ == '__main__':
    app.run(
        debug=True,
    )
