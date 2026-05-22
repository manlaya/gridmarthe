import os
import pytest

PATH_DATA = 'tests/data'
PATH_TMP_OUTPUTS = 'tests/tmp_outputs'


@pytest.fixture(scope='session', autouse=True)
def config():
    os.makedirs(PATH_TMP_OUTPUTS, exist_ok=True)
    return {
        'path_data': PATH_DATA,
        'path_tmp_outputs': PATH_TMP_OUTPUTS,
    }
