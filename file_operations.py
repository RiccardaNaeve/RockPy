__author__ = 'mike'
from os.path import expanduser, join
import numpyson

default_folder = join(expanduser("~"), 'Desktop', 'RockPy')

def save(smthg, file_name, folder=None):
    if not folder:
        folder = default_folder
    with open(join(folder, file_name), 'wb') as f:
        dump = numpyson.dumps(smthg)
        f.write(dump)
        f.close()

def load(file_name, folder = None):
    if not folder:
        folder = default_folder
    with open(join(folder, file_name), 'rb') as f:
        out = numpyson.loads(f.read())
    return out