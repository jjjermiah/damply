from pathlib import Path
from damply.utils import Directory, DirectoryList


# pytest tests
def test_directory():
    dir_path = Path("/home/user/dir1")
    directory = Directory(directory=dir_path, size_GB=10)
    
    assert directory.directory == dir_path
    assert directory.size_GB == 10
    assert directory['directory'] == dir_path
    assert directory['size_GB'] == 10
    assert repr(directory) == f"Directory({dir_path}, 10)"

def test_directory_list():
    dir1_path = Path("/home/user/dir1")
    dir2_path = Path("/home/user/dir2")
    directory_list = DirectoryList(directories=[
        Directory(directory=dir1_path, size_GB=10),
        Directory(directory=dir2_path, size_GB=20)
    ])
    
    assert len(directory_list) == 2
    assert directory_list[0].directory == dir1_path
    assert directory_list[1].directory == dir2_path
    assert directory_list.get_common_root() == Path("/home/user")
    assert directory_list.dir_size_dict() == {
        dir1_path: 10,
        dir2_path: 20
    }
    assert repr(directory_list) == f"CommonPre:{Path('/home/user')}\nDirectory({dir1_path}, 10)\nDirectory({dir2_path}, 20)\n"