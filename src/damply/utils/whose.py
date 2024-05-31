import os
from pwd import getpwuid
from pathlib import Path


def get_file_owner_full_name(file_path: Path):
    try:
        # Get the file's status
        file_stat = os.stat(file_path)

        # Get the user ID of the file owner
        uid = file_stat.st_uid

        # Get the user information based on the user ID
        user_info = getpwuid(uid)

        # Return the full name of the user
        return user_info.pw_gecos
    except Exception as e:
        return str(e)
