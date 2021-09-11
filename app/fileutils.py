import os
from app.config import load_config


class IFileStorage:
    def read(self, filename: str) -> bytes:
        raise NotImplementedError

    def write(self, filename: str, data: bytes) -> None:
        raise NotImplementedError

    def append(self, filename: str, data: bytes) -> None:
        raise NotImplementedError

    def delete(self, filename: str) -> None:
        raise NotImplementedError

    def get_full_filename(self, filename: str) -> str:
        raise NotImplementedError


class FileSystemFileStorage(IFileStorage):
    def __init__(self, directory_name: str):
        self._directory_name = directory_name

        if os.path.exists(self._directory_name):
            pass  # TODO: generate error?
        else:
            os.mkdir(self._directory_name)

    def get_full_filename(self, filename: str) -> str:
        return os.path.join(self._directory_name, filename)

    # TODO: What if we have a giant file
    def read(self, filename: str) -> bytes:
        storage_filename = self.get_full_filename(filename)
        fi = open(storage_filename, 'rb')
        result = fi.read()
        fi.close()
        return result

    def write(self, filename: str, data: bytes) -> None:
        storage_filename = self.get_full_filename(filename)
        fo = open(storage_filename, 'wb')
        fo.write(data)
        fo.close()

    def append(self, filename: str, data: bytes) -> None:
        storage_filename = self.get_full_filename(filename)
        fo = open(storage_filename, 'ab')
        fo.write(data)
        fo.close()

    def delete(self, filename: str) -> None:
        storage_filename = self.get_full_filename(filename)

        if os.path.exists(storage_filename):
            os.remove(storage_filename)


_config = load_config()

upload_storage = FileSystemFileStorage(_config['upload_storage'])
temporary_storage = FileSystemFileStorage(_config['temporary_storage'])
result_storage = FileSystemFileStorage(_config['result_storage'])
