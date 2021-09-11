import uuid


def generate_filename() -> str:
    return uuid.uuid4().hex
