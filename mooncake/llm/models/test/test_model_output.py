
import argparse
import json
import os
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from constants.constants_llm import ConstantsLLM
from models.models_llm import OpenAIModels
from models.message_preparatory import MessageTestEngine
from utils.utilities import create_path, inspect_df, _open

def initialise():
    parse = argparse.ArgumentParser(
        description="call fine-tuned model with provided config and data",
        epilog="example: python models/test/test_model_output.py --config configs/config_elektra.yaml --model train_model_v001 --in_path data/training/elektra/t001.csv --out_path data/outputs/models/elektra/output.csv")
    parse.add_argument("--checkpoint_path",
                       nargs="?",
                       default="/tmp/llm/checkpoint.yaml",
                       help="if provided, location to store checkpoint variables to restore from crash")
    parse.add_argument("--config",
                       required=True,
                       help="config with various model params as well as fine-tuned models")
    parse.add_argument("--model_key",
                       nargs="?",
                       default="model_v001",
                       help="key in config with params for fine-tuned model")
    parse.add_argument("--test_path",
                       required=True,
                       help="source data to prepare prompts for calling model with")
    parse.add_argument("--test_response_path",
                       nargs="?",
                       help="if provided, location to save responses from model")
    parse.add_argument("--sample",
                       nargs="?",
                       type=int,
                       help="random sample of data to test")
    args = parse.parse_args()

    return args


if __name__ == "__main__":

    args = initialise()
    config = _open(args.config)
    openai_models = OpenAIModels()
    cnst = ConstantsLLM()

    message_engine = MessageTestEngine(config, args.checkpoint_path)
    df = message_engine.prep_df(args.test_path)
    #destems = message_engine.solicitation_destem(df)
    prompts, res = message_engine.solicitation_test(df, args.model_key)
    breakpoint()
    message_engine.update_df(df,
                             cnst.llm_model_category,
                             res,
                             args.test_response_path)
