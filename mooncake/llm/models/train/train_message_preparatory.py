
import argparse
import os
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from llm.constants.constants_llm import ConstantsLLM
from llm.models.message_preparatory import MessageTrainEngine
from llm.utils.utilities import _open

def initialise():
    parse = argparse.ArgumentParser(
        description="use formatted data to prepare messages for fine-tuning a chatgpt model",
        epilog="example: python models/train/train_message_preparatory.py elektra data/training/elektra/t001.csv data/training/elektra/m001.csv")
    parse.add_argument("--checkpoint_path",
                       nargs="?",
                       default="/tmp/llm/checkpoint.yaml",
                       help="if provided, location to store checkpoint variables to restore from crash")
    parse.add_argument("--client",
                       required=True,
                       help="name of client to use to connect and prepare training data")
    parse.add_argument("--config",
                       nargs="?",
                       default="configs/config.yaml",
                       help="config with various model params as well as fine-tuned models")
    parse.add_argument("--train_path",
                       required=True,
                       help="input path to csv with formatted columns ready for training")
    parse.add_argument("--message_path",
                       required=True,
                       help="output path to messages file that will be used for training; jsonl extension")
    args = parse.parse_args()

    return args


if __name__ == "__main__":

    args = initialise()
    config = _open(args.config)
    cnst = ConstantsLLM()

    message_engine = MessageTrainEngine(config, args.checkpoint_path)
    df = message_engine.prep_df(args.train_path)
    #destems = message_engine.solicitation_destem(df)
    message_engine.prep_train(df,
                              args.message_path)
    # saved as last stem in prep_train
    
