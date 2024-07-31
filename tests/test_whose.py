import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from damply.utils import whose


def test_get_file_owner_full_name_unix():
    file_path = Path('/dummy/path')

    with patch('os.stat') as mock_stat, patch('pwd.getpwuid') as mock_getpwuid:
        mock_stat.return_value.st_uid = 1000
        mock_user_info = MagicMock()
        mock_user_info.pw_gecos = 'John Doe'
        mock_getpwuid.return_value = mock_user_info

        assert whose.get_file_owner_full_name(file_path) == 'John Doe'

def test_get_file_owner_full_name_import_error():
    file_path = Path('/dummy/path')

    with patch('builtins.print') as mock_print, patch.object(Path, 'owner', return_value='dummy_owner') as mock_owner:
        with patch.dict('sys.modules', {'pwd': None}):
            assert whose.get_file_owner_full_name(file_path) == 'dummy_owner'
            mock_print.assert_called_with("Module 'pwd' is not available on this platform.")

def test_get_file_owner_full_name_windows():
    file_path = Path('/dummy/path')

    with patch('platform.system', return_value='Windows'):
        assert whose.get_file_owner_full_name(file_path) == 'Retrieving user info is not supported on Windows.'

def test_get_file_owner_full_name_exception():
    file_path = Path('/dummy/path')

    with patch('os.stat', side_effect=Exception('An error occurred')):
        assert whose.get_file_owner_full_name(file_path) == 'An error occurred'
