from asyncio.log import logger
import logging
from server import app
from quart import jsonify, render_template, abort, request
from pathlib import Path


class APIResponse:
    def __init__(self):
        self._error = []
        self._data = {}

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, newError: BaseException):
        return self._error.append({str(type(newError)): newError.args[0]})

    def toObj(self):
        return {'error': self.error, 'data': self._data}


# default to main page
# @app.route('/')
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    logging.error("send th efkn mail bitch on reload")
    # raise ValueError("asdfsdf")

    # abort(404)
    return render_template("index.html")

# import the api eps
