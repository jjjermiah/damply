import os
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DirectoryModificationMetadata:
    directory: Path
    last_modification_time: Optional[int] = None
    last_modification_time_measured_at: Optional[datetime] = None

    def __post_init__(self):
        # Ensure the directory exists and is a directory
        self.validate_directory()
        
        # Initialize modification time and the measurement timestamp
        self.update_last_modification_time(initial=True)

    def validate_directory(self):
        """Validate that the directory exists and is indeed a directory."""
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory '{self.directory}' does not exist.")
        if not self.directory.is_dir():
            raise NotADirectoryError(f"Path '{self.directory}' is not a directory.")
    
    def get_last_modification_time(self) -> int:
        """Recursively get the last modification time of the directory and its contents."""
        # if empty, modification time is just time of directory's actual modification and nothing to do with files
        print(f"Getting last modification time for {self.directory.absolute()}")
        last_mod_time = max(
            (f.stat().st_mtime for f in self.directory.rglob('*') if f.is_file()),
            default=self.directory.stat().st_mtime
        )
        return int(last_mod_time)

    def update_last_modification_time(self, initial: bool = False):
        """Update the stored last modification time and measurement timestamp."""
        self.last_modification_time = self.get_last_modification_time()
        self.last_modification_time_measured_at = datetime.now()
        if not initial:
            print(f"Updated last modification time for {self.directory.absolute()}")

    def update(self):
        """Update the metadata if the directory has been modified since the last check."""
        if self.get_last_modification_time() != self.last_modification_time:
            self.update_last_modification_time(initial = True)
        
        self.get_file_count()
        self.get_total_size()
        self.has_subdirectories()

    def get_file_count(self) -> int:
        """Get the total number of files in the directory."""
        file_count = sum(1 for _ in self.directory.rglob('*') if _.is_file())
        return file_count

    def get_total_size(self) -> int:
        """Calculate the total size of the directory."""
        total_size = sum(f.stat().st_size for f in self.directory.rglob('*') if f.is_file())
        return total_size

    def has_subdirectories(self) -> bool:
        """Check if the directory contains any subdirectories."""
        contains_subdirs = any(f.is_dir() for f in self.directory.iterdir())
        return contains_subdirs

    def display(self):
        """Display the metadata and check for modifications."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        self.update()
        
        console = Console()
        table = Table(title=f"Directory: {self.directory.absolute()}")
        table.add_column("Property", justify="left", style="cyan", no_wrap=True)
        table.add_column("Value", justify="left", style="magenta")
        
        table.add_row("Last modification time", str(datetime.fromtimestamp(self.last_modification_time)))
        table.add_row("Last modification time measured at", str(self.last_modification_time_measured_at))
        table.add_row("File count", str(self.get_file_count()))
        table.add_row("Total size", str(self.get_total_size()))
        table.add_row("Has subdirectories", str(self.has_subdirectories()))
        
        panel = Panel(table, title="Directory Metadata", border_style="red")
        console.print(panel)
        
        


if __name__ == '__main__':
    # directory_path = Path("/path/to/your/directory")
    import tempfile
    
    directory_path = Path(tempfile.mkdtemp())
    
    try:
        metadata = DirectoryModificationMetadata(directory=directory_path)
        metadata.display()
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    try:
        import time
        time.sleep(5)
        print("\nWriting to directory...")
        # Create a file in the directory
        with open(os.path.join(directory_path, 'new_file.txt'), 'w') as f:
            f.write('New file content')
            
        metadata.display()
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        time.sleep(2)
        print("\nDeleting file in directory...")
        # Delete the file
        os.remove(os.path.join(directory_path, 'new_file.txt'))
        metadata.display()
        
        import shutil
        shutil.rmtree(directory_path)

# def test_complex_multiple_subdirectories():
#     """
#     This test will do the following:
#     1. Create a directory structure with multiple subdirectories
#     2. Create a file in each subdirectory
#     3. Record the last modification time of each subdirectory
#     4. Add a file to each subdirectory
#     5. Record the last modification time of each subdirectory. Ensure that the last modification time has changed.
#     6. Update one of the files in each subdirectory
#     7. Record the last modification time of each subdirectory. Ensure that the last modification time has changed.
#     """
#     import os
#     import shutil
#     import time
#     import tempfile
    
#     base_dir = tempfile.mkdtemp()
#     subdirs = [f'subdir_{i}' for i in range(5)]
#     files = [f'file_{i}.txt' for i in range(5)]

#     if os.path.exists(base_dir):
#         shutil.rmtree(base_dir)
#     os.mkdir(base_dir)

#     initial_times = {}
#     updated_times_after_add = {}
#     final_times_after_update = {}

#     try:
#         # Step 1: Create subdirectories
#         for subdir in subdirs:
#             os.mkdir(os.path.join(base_dir, subdir))
        
#         # Step 2: Create a file in each subdirectory
#         for subdir, file_name in zip(subdirs, files):
#             with open(os.path.join(base_dir, subdir, file_name), 'w') as f:
#                 f.write('Initial content')

#         # Step 3: Record the last modification time of each subdirectory and ensure it changed
#         dmm_list = [DirectoryModificationMetadata(directory=Path(os.path.join(base_dir, subdir))) for subdir in subdirs]
#         for dmm in dmm_list:
#             dmm.display()
#             assert dmm.get_last_modification_time() > 0, f"Modification time is not greater than 0 for {dmm.directory.absolute()}"
#         time.sleep(5)
#         print("\n\n")
#         # Step 4: Add a file to each subdirectory
#         for subdir in subdirs:
#             new_file_path = os.path.join(base_dir, subdir, 'new_file.txt')
#             with open(new_file_path, 'w') as f:
#                 f.write('New file content')
                
#         # Step 5: Record the last modification time of each subdirectory and ensure it changed
#         for dmm in dmm_list:
#             dmm.display()
#             assert dmm.get_last_modification_time() > 0, f"Modification time is not greater than 0 for {dmm.directory.absolute()}"

#         time.sleep(5)
#         print("\n\n")
        
#         # Check again
#         for dmm in dmm_list:
#             dmm.display()
            

#     finally:
#         # Cleanup
#         if os.path.exists(base_dir):
#             shutil.rmtree(base_dir)

    