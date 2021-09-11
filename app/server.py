import base64
import io
from typing import Dict
from flask import Flask, Response, request, jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException
from app.film_converter import process_film
from app.config import load_config
from app.constants import VideoFileStatus
from app.db import get_all_films, get_film, create_new_film, create_film_pieces, get_session
from app.utils import generate_filename
from app.fileutils import upload_storage, result_storage
from app.schemas import GetListSchema, CreateFilmSchema, PatchFilmSchema, PutVideoSchema

app = Flask(__name__)

RETURN_MIMETYPE = load_config()['return_video_mimetype']
RETURN_FILE_EXTENSION = load_config()['return_video_file_extension']
# ######### error handling
#def _create_error_response(name, description='', code=500):
#    """
#    Common error function
#    """
#    response = {
#        "code": code,
#        "name": name,
#        "description": description
#    }
#    return jsonify(response), code


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
# TODO: Validation
@app.route('/api/videos', methods=['GET'])
def video_list() -> Dict:
    data = request.args
    schema = GetListSchema(**data)
    session = get_session()
    films = get_all_films(session, start=schema.start, count=schema.count)
    return {"films": [x.as_dict() for x in films]}


@app.route('/api/videos', methods=['POST'])
def create_video() -> Dict:
    data = request.json
    schema = CreateFilmSchema(**data)
    session = get_session()

    with session.begin():
        film = create_new_film(session, name=schema.name, description=schema.description, size=schema.size)

    return film.as_dict()


@app.route('/api/videos/<int:video_id>', methods=['PATCH'])
def patch_video(video_id: int) -> Dict:
    data = request.json
    schema = PatchFilmSchema(**data)

    session = get_session()
    film = get_film(session, video_id)

    if film is None:
        # TODO: wrap to handler
        return "Film is not found", 404

    # TODO: check after starting putting dataa pieces
    # TODO: check process
    with session.begin():
        film.size = schema.size
        session.add(film)

    return film.as_dict()


@app.route('/api/videos/<int:video_id>', methods=['GET'])
def get_video(video_id: int) -> Dict:
    session = get_session()
    film = get_film(session, video_id)

    if film is None:
        # TODO: wrap to handler
        return "Film is not found", 404

    return film.as_dict()


@app.route('/api/videos/<int:video_id>/content', methods=['PUT'])
def put_video_content(video_id: int) -> Dict:
    session = get_session()
    data = request.json
    schema = PutVideoSchema(**data)
    film = get_film(session, video_id)

    if film is None:
        # TODO: wrap to handler
        return "Film is not found", 404

    if film.size is None:
        # TODO: wrap to handler
        return "Film size isn't set", 400

    if film.status not in (VideoFileStatus.in_loading.value, VideoFileStatus.new.value):
        # TODO: wrap to handler
        return "Film isn't in right status", 400

    piece_number = schema.piece_number
    piece_content = schema.piece_content
    filename = generate_filename()
    decoded = base64.b64decode(piece_content)
    upload_storage.write(filename, decoded)
    run_convert = False

    with session.begin():
        create_film_pieces(session, video_id, piece_number, len(decoded), filename)
        session.refresh(film)
        # TODO: think about properties
        if film.uploaded_size > film.size:
            film.status = VideoFileStatus.failed.value
        elif film.uploaded_size == film.size:
            # run
            film.status = VideoFileStatus.in_process.value
            run_convert = True
        else:
            film.status = VideoFileStatus.in_loading.value

        session.add(film)

    if run_convert:
        process_film.delay(video_id)

    # TODO: think response
    return {}


@app.route('/api/videos/<int:video_id>/content', methods=['GET'])
def get_video_content(video_id: int) -> Response:
    session = get_session()
    data = request.json
    film = get_film(session, video_id)

    if film is None:
        return "Video not found", 404

    if film.status != VideoFileStatus.success.value:
        return "Video not found", 404

    data = result_storage.read(film.path)

    return send_file(
        io.BytesIO(data),
        mimetype=RETURN_MIMETYPE,
        as_attachment=True,
        attachment_filename=f'{film.path}.{RETURN_FILE_EXTENSION}'
    )
