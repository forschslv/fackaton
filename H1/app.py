import flask
import pandas as pd
import os, sys
path_to_data = 'data.csv'

if os.path.exists(path_to_data):
    data = pd.read_csv(path_to_data)
else:
    data = pd.DataFrame()

app = flask.Flask(__name__)


@app.route("/")
def index():
    return "Hello world!"



if __name__ == '__main__':
    app.run(
        debug=True,
    )
