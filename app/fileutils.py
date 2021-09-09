import os
from app.config import load_config

class IFileStorage:
    def read(self, filename):
        raise NotImplementedError

    def write(self, filename, data):
        raise NotImplementedError

    def delete(self, filename):
        raise NotImplementedError


class FileSystemFileStorage(IFileStorage):
    def __init__(self, directory_name):
        self._directory_name = directory_name

        if os.path.exists(self._directory_name):
            pass  # TODO: generate error?
        else:
            os.mkdir(self._directory_name)

    # TODO: errors
    def _get_full_file_name(self, filename):
        return os.path.join(self._directory_name, filename)

    # TODO: What if we have a giant file
    def read(self, filename):
        storage_filename = self._get_full_file_name(filename)
        fi = open(storage_filename, 'rb')
        result = fi.read(data)
        fi.close()
        return result

    def write(self, filename, data):
        storage_filename = self._get_full_file_name(filename)
        fo = open(storage_filename, 'wb')
        fo.write(data)
        fo.close()

    def delete(self, filename):
        storage_filename = self._get_full_file_name(filename)
        os.remove(storage_filename)


_config = load_config()

upload_storage = FileSystemFileStorage(_config['upload_storage'])
temporary_storage = FileSystemFileStorage(_config['temporary_storage'])
result_storage = FileSystemFileStorage(_config['result_storage'])
