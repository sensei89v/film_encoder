import base64
import os
import yaml
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import HTTPException
from app.db import get_all_films, get_film, create_new_film, create_film_pieces
from app.utils import generate_filename
from app.fileutils import FileSystemFileStorage

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


#@app.errorhandler(HTTPException)
#def handle_flask_exception(exception):
#    return _create_error_response(exception.name, exception.description, exception.code)


#@app.errorhandler(ValidationError)
#def handle_validation_exception(exception):
#    return _create_error_response("Incorrect input data", str(exception), 400)


#@app.errorhandler(Exception)
#def handle_common_exception(exception):
#    return _create_error_response("internal exception", str(exception), 500)


# ######### routing
# Validation
@app.route('/api/videos', methods=['GET'])
def video_list():
    films = get_all_films()
    return {"films": [x.as_dict() for x in films]}


@app.route('/api/videos', methods=['POST'])
def create_video():
    data = request.json
    return create_new_film(name=data['name'], description=data['description']).as_dict()


@app.route('/api/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    film = get_film(video_id)

    if film is None:
        # TODO: wrap to handler
        return "Film is not found", 404

    return film.as_dict()


@app.route('/api/videos/<int:video_id>/content', methods=['PUT'])
def put_video_content(video_id):
    film = get_film(video_id)
    data = request.json

    if film is None:
        # TODO: wrap to handler
        return "Film is not found", 404

    # TODO: validation
    piece_number = data['piece_number']
    piece_content = data['piece_content']
    filename = generate_filename()
    decoded = base64.b64decode(data['piece_content'])
    app.upload_starage.write(filename, decoded)
    create_film_pieces(video_id, piece_number, len(decoded), filename)
    # TODO: think response
    return {}

@app.route('/api/videos/<int:video_id>/content', methods=['GET'])
def get_video_content(video_id):
    return "Hello world"


def load_config(app, config_name):
    try:
        opened_file = open(config_name, 'r')
        config = yaml.load(opened_file)
        app.config.update(config)
    except Exception:
        raise ValueError(f'Error on uploading config file: {config_name}')

    # TODO: think maybe divide
    # TODO: implement good dependiency injection
    with app.app_context():
        app.upload_starage = FileSystemFileStorage(app.config['upload_directory'])
