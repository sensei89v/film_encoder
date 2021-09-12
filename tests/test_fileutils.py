import os
import pytest
import shutil

from app.fileutils import FileSystemFileStorage, generate_filename, FileUtilsException


class TestFileUtils:
    STORAGE_NAME = "test_storage"
    storage = None

    @classmethod
    def setup_class(cls):
        cls.storage = FileSystemFileStorage(cls.STORAGE_NAME)

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.STORAGE_NAME)

    def test_create_new_file_storage(self):
        storage_name = "Test new storage name"

        if os.path.exists(storage_name):
            shutil.rmtree(storage_name)

        storage = FileSystemFileStorage(storage_name)
        assert os.path.exists(storage_name) == True
        del storage
        assert os.path.exists(storage_name) == True
        shutil.rmtree(storage_name)

    def test_generate_filename(self):
        filename1 = generate_filename()
        filename2 = generate_filename()
        assert filename1 != filename2

    def test_work(self):
        with pytest.raises(FileUtilsException):
            self.storage.read('unexisted file')

        self.storage.write('new', b'newdata')
        data = self.storage.read('new')
        assert data == b'newdata'
        self.storage.append('new2', b'newdata')
        self.storage.append('new2', b'newdata')
        data = self.storage.read('new2')
        assert data == b'newdatanewdata'
        self.storage.delete('new2')

        with pytest.raises(FileUtilsException):
            self.storage.read('new2')

        with pytest.raises(FileUtilsException):
            self.storage.write('failwriting/something', b'data')

        with pytest.raises(FileUtilsException):
            self.storage.append('failappending/something', b'data')

        with pytest.raises(FileUtilsException):
            # Fail on writing string non bytes
            self.storage.write('failwriting/something', 'data')

        with pytest.raises(FileUtilsException):
            # Fail on appending string non bytes
            self.storage.append('failappending/something', 'data')
