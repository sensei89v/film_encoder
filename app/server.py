from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

from db import get_all_films, get_session

app = Flask(__name__)


# ######### error handling
def _create_error_response(name, description='', code=500):
    """
    Common error function
    """
    response = {
        "code": code,
        "name": name,
        "description": description
    }
    return jsonify(response), code


@app.errorhandler(HTTPException)
def handle_flask_exception(exception):
    return _create_error_response(exception.name, exception.description, exception.code)


#@app.errorhandler(ValidationError)
#def handle_validation_exception(exception):
#    return _create_error_response("Incorrect input data", str(exception), 400)


@app.errorhandler(Exception)
def handle_common_exception(exception):
    return _create_error_response("internal exception", str(exception), 500)


# ######### routing
@app.route('/api/videos', methods=['GET'])
def video_list():
    return {"films": get_all_films()}


@app.route('/api/videos', methods=['POST'])
def create_video():
    return "Hello world"


@app.route('/api/videos/<int:video_id>/content', methods=['PUT'])
def put_video_data(video_id):
    return "Hello world"


@app.route('/api/videos/<int:video_id>/content', methods=['GET'])
def get_video_data(video_id):
    return "Hello world"



@app.route('/', methods=['GET'])
def hello_world():
    return "Hello world"


if __name__ == '__main__':
    app.run()
