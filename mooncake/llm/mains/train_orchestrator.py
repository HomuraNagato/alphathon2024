
import argparse
import datetime
import os
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from constants.constants_llm import ConstantsLLM
from models.train.train_data_preparatory import TrainEngine
from models.message_preparatory import MessageTrainEngine, MessageTestEngine
#from models.test.test_model_output import TestEngine
from models.test.test_model_statistics import StatisticEngine
from models.openai_liaison import liaison_finetune
from utils.config_editor import ConfigEditor
from utils.utilities import inspect_df, _open

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

    parse.add_argument("--checkpoint_path",
                       nargs="?",
                       default="/tmp/llm/checkpoint.yaml",
                       help="if provided, location to store checkpoint variables to restore from crash")
    parse.add_argument("--client",
                       required=True,
                       help="name of client to use to connect and prepare training data")
    parse.add_argument("--column_predicted",
                       nargs="?",
                       default="llm_model_category",
                       help="column with predictions to compare to actual")
    parse.add_argument("--column_true",
                       nargs="?",
                       default="true_category",
                       help="column with actual truths")
    parse.add_argument("--data_path",
                       required=True,
                       help="save location of initial data for training and testing")
    parse.add_argument("--message_path",
                       required=True,
                       help="output path to messages file that will be used for training; jsonl extension")
    parse.add_argument("--statistic_path",
                       nargs="?",
                       help="if provided, location to store statistics")
    parse.add_argument("--test_path",
                       required=False,
                       help="save directory for test data")
    parse.add_argument("--test_response_path",
                       nargs="?",
                       help="if provided, location to save responses from model")
    parse.add_argument("--train_path",
                       required=True,
                       help="save path for train data")
    parse.add_argument("--config",
                       required=True,
                       help="config with map between client columns and llm columns")
    parse.add_argument("--max_tokens",
                       nargs="?",
                       default=100,
                       type=int,
                       help="argument for max_tokens")
    parse.add_argument("--model",
                       nargs="?",
                       help="the model to use as base upon which fine-tuning will occur; overrides model from base_model_key. default is gpt-3.5-turbo-1106")
    parse.add_argument("--model_key_base",
                       nargs="?",
                       default="model_v000",
                       help="key within config to use as base for ft")
    parse.add_argument("--model_key",
                       nargs="?",
                       default="model_v001",
                       help="key within config to store ft model")
    parse.add_argument("--sample",
                       nargs="?",
                       type=int,
                       help="random sample of data prior to train/test split")
    parse.add_argument("--split",
                       nargs="?",
                       default=0.5,
                       type=restricted_float,
                       help="0-1, percent train/test split of initial data, value is for percent train, remainder will be test")
    parse.add_argument("--temperature",
                       nargs="?",
                       default=0.7,
                       type=float,
                       help="argument for model temperature")
    parse.add_argument("--threshold",
                       nargs="?",
                       type=int,
                       help="threshold value to limit samples if the total number of samples for a category is below this")
    parse.add_argument("--top_p",
                       nargs="?",
                       default=1,
                       type=int,
                       help="argument for model top_p")
    parse.add_argument("--unique",
                       action="store_true",
                       help="filter the initial data to only include unique rows; default false")
    args = parse.parse_args()

    return args

if __name__ == "__main__":

    args = initialise()
    cnst = ConstantsLLM()

    # ----------------- step 00 ----------------- #
    # check config and verify arguments?
    config_editor = ConfigEditor(args.config)
    config_editor.verify_config(args.client, args.model_key)
    config = _open(args.config)
    # ----------------- ------- ----------------- #

    # ----------------- step 01 ----------------- #
    # prep train / test data
    data_engine = TrainEngine(config,
                             args.checkpoint_path,
                             args.split,
                             args.sample,
                             args.threshold,
                             args.unique)
    df = data_engine.prep_df(args.data_path)
    data_engine.save_train_test(args.train_path, args.test_path, df)
    # ----------------- ------- ----------------- #

    # ----------------- step 02 ----------------- #
    # prep messages
    message_engine = MessageTrainEngine(config, args.checkpoint_path)
    df = message_engine.prep_df(args.train_path)
    #destems = message_engine.solicitation_destem(df)
    message_engine.prep_train(df,
                              args.message_path)
    # ----------------- ------- ----------------- #

    # ----------------- step 03 ----------------- #
    # upload file to openai and await completion
    # start fine-tuning and await completion
    model_base = args.model or config[args.model_key_base]["model_type"]
    ft_model = liaison_finetune(args.message_path, args.checkpoint_path, model_base)
    # ----------------- ------- ----------------- #

    # ----------------- step 04 ----------------- #
    # save finetune_id to config
    config_editor = ConfigEditor(args.config)
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d')
    config = config_editor.save_model_key(args.model_key,
                                          model_type=ft_model,
                                          data_path=args.data_path,
                                          date=now,
                                          temperature=args.temperature,
                                          top_p=args.top_p,
                                          max_tokens=args.max_tokens)
    # ----------------- ------- ----------------- #

    # ----------------- step 05 ----------------- #
    # test data with finetuned model
    message_engine = MessageTestEngine(config, args.checkpoint_path)
    df = message_engine.prep_df(args.test_path)
    #destems = message_engine.solicitation_destem(df)
    prompts, res = message_engine.solicitation_test(df, args.model_key)
    message_engine.update_df(df,
                             cnst.llm_model_category,
                             res,
                             args.test_response_path)
    # ----------------- ------- ----------------- #

    # ----------------- step 06 ----------------- #
    # statistics on test data responses
    stat_engine = StatisticEngine()
    stat_dict = stat_engine.calc_confusion_matrix(args.test_response_path,
                                                  args.column_true,
                                                  args.column_predicted)
    stat_engine.save_statistics(args.statistic_path, stat_dict)
    # ----------------- ------- ----------------- #
