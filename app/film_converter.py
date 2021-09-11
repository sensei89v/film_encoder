import json
import logging
import subprocess


from app.celery import celery_app
from app.constants import VideoFileStatus
from app.db import FilmPieces, get_session, get_film, Session, Films
from app.fileutils import upload_storage, temporary_storage, result_storage
from app.config import load_config
from app.utils import generate_filename


logger = logging.getLogger()


def _get_option(field):
    _config = load_config()
    options = _config['encode_settings'][field]

    if options is None:
        options = ""

    return options


_common_options = _get_option('common_options')
_infile_options = _get_option('infile_options')
_outfile_options = _get_option('outfile_options')


def _clean_all_temporary_files(session: Session, film: Films) -> None:
    for film_piece in film.film_pieces:
        upload_storage.delete(film_piece.path)

    session.query(FilmPieces).filter(FilmPieces.film_id == film.id).delete()
    session.refresh(film)


def _check_video_file(full_filename: str) -> bool:
    ffprobe_result = subprocess.run([f"ffprobe -show_streams -print_format json {full_filename}"], shell=True, capture_output=True)

    if ffprobe_result.returncode != 0:
        # TODO: add logging
        return False

    json_result = json.loads(ffprobe_result.stdout)
    streams = json_result['streams']
    video_stream_count = 0
    audio_stream_count = 0

    for stream in streams:
        codec_type = stream.get('codec_type')

        if codec_type == "video":
            video_stream_count += 1
        elif codec_type == "audio":
            audio_stream_count += 1

    return video_stream_count == 1 and audio_stream_count > 0


def _convert_video_file(input_filename: str, output_filename: str) -> bool:
    ffmpeg_result = subprocess.run(
        [f"ffmpeg {_common_options} {_infile_options} -i {input_filename} {_outfile_options} {output_filename}"],
        shell=True,
        capture_output=True
    )
    return ffmpeg_result.returncode == 0


@celery_app.task()
def process_film(video_id: int) -> None:
    session = get_session()

    film = get_film(session, video_id)

    if film is None:
        # TODO: add error
        return

    # TODO: long transaction
    with session.begin():
        try:
            film_pieces = film.film_pieces
            sorted_film_pieces = sorted(film_pieces, key=lambda x: x.piece_number)
            sorted_film_pieces_ids = [x.piece_number for x in sorted_film_pieces]

            if sorted_film_pieces_ids[0] != 0 or \
               sorted_film_pieces_ids[-1] != len(sorted_film_pieces_ids) - 1 or \
               len(sorted_film_pieces_ids) != len(set(sorted_film_pieces_ids)):
                _clean_all_temporary_files(session, film)
                film.status = VideoFileStatus.failed.value
                session.add(film)
                return

            new_filename = generate_filename()

            for film_pieces in sorted_film_pieces:
                data = upload_storage.read(film_pieces.path)
                temporary_storage.append(new_filename, data)

            full_new_filename = temporary_storage.get_full_filename(new_filename)
            converted_filename = generate_filename()
            full_converted_filename = temporary_storage.get_full_filename(converted_filename)

            if not _check_video_file(full_new_filename):
                temporary_storage.delete(new_filename)
                _clean_all_temporary_files(session, film)
                film.status = VideoFileStatus.failed.value
                session.add(film)
                return

            if not _convert_video_file(full_new_filename, full_converted_filename):
                # TODO: fix it
                temporary_storage.delete(new_filename)
                temporary_storage.delete(converted_filename)
                _clean_all_temporary_files(session, film)
                film.status = VideoFileStatus.failed.value
                session.add(film)
                return

            result_filename = generate_filename()

            # TODO: move!!!!!
            converted_data = temporary_storage.read(converted_filename)
            result_storage.write(result_filename, converted_data)

            temporary_storage.delete(new_filename)
            temporary_storage.delete(converted_filename)
            _clean_all_temporary_files(session, film)
            film.status = VideoFileStatus.success.value
            film.path = result_filename
            session.add(film)
        except Exception as e:
            session.rollback()
            session.refresh(film)
            logger.exception(e)
            film.status = VideoFileStatus.failed.value
            session.add(film)
