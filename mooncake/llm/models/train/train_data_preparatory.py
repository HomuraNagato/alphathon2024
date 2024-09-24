
import argparse
import os
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from llm.constants.constants_llm import ConstantsLLM
from llm.models.data_preparatory import DataEngine
from llm.utils.utilities import create_path, inspect_df, _open

def restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{x} is not a valid float")
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError(f"{x} is not in range [0.0, 1.0]")
    return x

def initialise():
    
    parse = argparse.ArgumentParser(
        description="prep data for training, using mapping table with human-labelled categories",
        epilog="example: python proto/prep_train_data.py")
    parse.add_argument("--client",
                       required=True,
                       help="name of client to use to connect and prepare training data")
    parse.add_argument("--data_path",
                       required=True,
                       help="save location of initial data for training and testing")
    parse.add_argument("--train_path",
                       required=True,
                       help="save path for train data")
    parse.add_argument("--test_path",
                       help="optional; save path for test data; if excluded, all data will save in train_path")
    parse.add_argument("--config",
                       nargs="?",
                       default="configs/config_base.yaml",
                       help="config with map between client columns and llm columns")
    parse.add_argument("--checkpoint_path",
                       nargs="?",
                       default="/tmp/senzai/checkpoint.yaml",
                       help="if provided, location to store checkpoint variables to restore from crash")
    parse.add_argument("--sample",
                       nargs="?",
                       type=int,
                       help="random sample of data prior to train/test split")
    parse.add_argument("--sep",
                       nargs="?",
                       default=",",
                       help="df separator")
    parse.add_argument("--split",
                       nargs="?",
                       default=0.5,
                       type=restricted_float,
                       help="0-1, percent train/test split, value is for percent train, remainder will be test")
    parse.add_argument("--threshold",
                       nargs="?",
                       type=int,
                       help="threshold value to limit samples if the total number of samples for a category is below this")
    parse.add_argument("--unique",
                       action="store_true",
                       help="filter the data to only include unique rows; default false")
    args = parse.parse_args()

    return args

class TrainEngine(DataEngine):

    def __init__(self, config, checkpoint_path, split, sample, threshold, unique, sep=","):
        DataEngine.__init__(self, config)
        self.cnst_llm = ConstantsLLM()
        self.column_map = config["column_map"]
        self.checkpoint_path = checkpoint_path
        self.sep = sep
        self.split = split
        self.sample = sample
        self.threshold = threshold
        self.unique = unique

    def prep_df(self, data_path):

        df = pd.read_csv(data_path, low_memory=False, sep=self.sep)
        df = df.fillna('')
        df = df.map(lambda x: x.lower() if isinstance(x, str) else x)

        # map columns to desired llm columns and make for easier reading
        df.columns = [ x.lower().replace(" ", "_") for x in df.columns ]
        df.rename(columns=self.column_map, inplace=True)
        # remove unnecessary columns
        cols_drop = set(df.columns) - set(self.column_map.values())
        df.drop(columns=cols_drop, inplace=True)
        # include additional columns for llm
        #cols_include = set(self.cnst_llm.columns) - set(df.columns)
        #for col in cols_include:
        #    df[col] = ""
        idx_category_na = df.loc[:,self.cnst_llm.true_category] == ""
        df = df.loc[~idx_category_na,:]

        if self.unique:
            n_pre = df.shape[0]
            df = df.drop_duplicates()
            n_post = df.shape[0]
            if n_post < n_pre:
                print(f"the data has been reduced from {n_pre} to {n_post} rows due to duplicates")

        if (self.sample and (self.sample < df.shape[0])):
            sample_idx = df.sample(n=self.sample).index
            df = df.loc[sample_idx,:]

        if self.threshold:
            counts = df.groupby(self.cnst_llm.true_category).size()
            counts_threshold = counts[counts >= self.threshold].index
            threshold_idx = df.loc[:,self.cnst_llm.true_category].isin(counts_threshold)
            df = df.loc[threshold_idx,:]

        inspect_df(df, description="prepped df")

        return df

    def save_train_test(self, train_path, test_path, df):

        create_path(train_path)

        if not test_path:
            df.to_csv(train_path, index=False)
            print(f"all data is prepped for message transformation at {train_path} (n={df.shape[0]})")
            return

        create_path(test_path)
        # split into train and test
        df_train, df_test = train_test_split(df,
                                             train_size=self.split,
                                             stratify=df.loc[:,self.cnst_llm.true_category])

        df_train.to_csv(train_path, index=False)
        df_test.to_csv(test_path, index=False)
        print(f"train data is prepped for message transformation at {train_path} (n={df_train.shape[0]})")
        print(f"test data is prepped for testing at {test_path} (n={df_test.shape[0]})")


if __name__ == "__main__":

    args = initialise()
    config = _open(args.config)
    print(config)

    data_engine = TrainEngine(config,
                              args.checkpoint_path,
                              args.split,
                              args.sample,
                              args.threshold,
                              args.unique,
                              sep=args.sep)
    
    df = data_engine.prep_df(args.data_path)
    data_engine.save_train_test(args.train_path, args.test_path, df)
