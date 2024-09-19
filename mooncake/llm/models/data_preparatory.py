
import os
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from utils.utilities import create_path, _open

class DataEngine:

    def __init__(self, config):
        self.config = config

    def prep_df(self, data_path):
        df = pd.read_csv(data_path, low_memory=False)
        df = df.fillna('')
        df = df.map(lambda x: x.lower() if isinstance(x, str) else x)
        return df

