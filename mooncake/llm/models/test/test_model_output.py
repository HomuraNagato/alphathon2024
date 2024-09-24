
import argparse
import json
import os
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from llm.constants.constants_llm import ConstantsLLM
from llm.models.message_preparatory import MessageTestEngine
from llm.utils.utilities import create_path, inspect_df, _open
from llm.utils.yaml_editor import Checkpoint

def initialise():
    parse = argparse.ArgumentParser(
        description="call fine-tuned model with provided config and data",
        epilog="example: python models/test/test_model_output.py --config configs/config_elektra.yaml --model train_model_v001 --in_path data/training/elektra/t001.csv --out_path data/outputs/models/elektra/output.csv")
    parse.add_argument("--checkpoint_pdir",
                       nargs="?",
                       default="/tmp/llm",
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
                       default=0,
                       help="random sample of data to test")
    args = parse.parse_args()

    return args


if __name__ == "__main__":

    args = initialise()
    config = _open(args.config)
    cnst = ConstantsLLM()
    chkpnt = Checkpoint(args.checkpoint_pdir)

    message_engine = MessageTestEngine(config, chkpnt)
    df = message_engine.prep_df(args.test_path)
    #destems = message_engine.solicitation_destem(df)
    df = message_engine.sample(df, args.sample)
    breakpoint()
    prompts, res = message_engine.solicitation_test(df, args.model_key, args.sample)
    message_engine.update_df(df,
                             cnst.llm_model_category,
                             res,
                             args.test_response_path)

    """
    df = pd.DataFrame(columns=["ticker", "item_1a", "item_1b"])
    tmp = { "ticker": "AAPL", "item_1a": "customers say our products are too expensive", "item_1b": "our closed ecosystem is preventing growth" }
    df = df._append(tmp, ignore_index=True)
    tmp = { "ticker": "NVDA", "item_1a": "we are seeing great growth", "item_1b": "sales exceed expectations" }
    df = df._append(tmp, ignore_index=True)

    config = _open("mooncake/llm/configs/config_sp500_10k.yaml")
    response_col = "openai_response"
    model_key = "model_v001"

    message_engine = MessageTestEngine(config)
    prompts, res = message_engine.solicitation_test(df, model_key)
    message_engine.update_df(df,
                             response_col,
                             res)
    """
    # TODO, is this an ok place to remove all of the checkpoints?
    chkpnt.remove()
