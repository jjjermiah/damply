#!/cluster/home/t119797uhn/damply/.pixi/envs/py310/bin/python 


from pathlib import Path; 
from damply.metadata import DMPMetadata
from rich import print

metadata = DMPMetadata.from_path(Path("./tests/examples/gcsi"))

print(metadata)