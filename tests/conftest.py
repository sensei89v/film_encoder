import os
import pytest
import shutil


TEST_DB = 'TEST.DB'
UPLOAD_TEST =  './upload_directory_test'
TEMPORARY_TEST = './temporary_directory_test'
RESULT_TEST = './result_directory_test'


def pytest_configure(config):
    from app.config import load_config
    config = load_config()
    config['upload_storage'] = UPLOAD_TEST
    config['temporary_storage'] = TEMPORARY_TEST
    config['result_storage'] = RESULT_TEST

    config['database'] = f'sqlite:///{TEST_DB}'
    print("pytest_configure\n")

#def pytest_sessionstart(session):
#def pytest_sessionfinish(session, exitstatus):

def pytest_unconfigure(config):
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    for directory in (UPLOAD_TEST, TEMPORARY_TEST, RESULT_TEST):
        if os.path.exists(directory):
            shutil.rmtree(directory)
