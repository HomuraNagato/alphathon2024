
import argparse
import datetime
from pathlib import Path
import os
import sys
import yaml

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from utils.yaml_editor import YamlEditor, Checkpoint
from utils.utilities import _open, get_logger

def initialise():

    parse = argparse.ArgumentParser(
        description="update a config with params",
        epilog="example: python models/train/update_config.py -- ")
    parse.add_argument("--config",
                       required=True,
                       help="config for client with various model params")
    parse.add_argument("--client",
                       nargs="?",
                       default="senzai",
                       help="name of client")
    parse.add_argument("--checkpoint_path",
                       nargs="?",
                       default="/tmp/llm/checkpoint.yaml",
                       help="path to yaml used to store temporary data to recover during fine-tune")
    parse.add_argument("--model_key_base",
                       nargs="?",
                       default="model_v000",
                       help="key within config to use as base for ft")
    parse.add_argument("--model_key",
                       nargs="?",
                       default="model_v001",
                       help="key within config to use for accessing params of model")
    parse.add_argument("--model",
                       nargs="?",
                       default="gpt-4o-mini",
                       help="corresponds to openai model; including finetuned; overrides model from base_model_key. default is gpt-3.5-turbo-1106")
    parse.add_argument("--data_path",
                       nargs="?",
                       help="path to source data file (prior to train/test) used for finetuning model")
    parse.add_argument("--temperature",
                       nargs="?",
                       default=0.7,
                       type=float,
                       help="argument for model temperature")
    parse.add_argument("--top_p",
                       nargs="?",
                       default=1,
                       type=int,
                       help="argument for model top_p")
    parse.add_argument("--max_tokens",
                       nargs="?",
                       default=100,
                       type=int,
                       help="argument for max_tokens")
    args = parse.parse_args()

    return args

class ConfigEditor(YamlEditor):

    def __init__(self, config_path):
        YamlEditor.__init__(self, config_path, "config")
        self.default_config_path = Path(self.rel_dir, "configs/config_base.yaml")

    def verify_config(self, client, model_key):

        if self.ydict:
            return
        
        default_config = _open(self.default_config_path)
        default_config["client"] = client
        self.ydict = default_config

        self.save()
        self.chmod(0o666)
        self.log.warning(f"{self.path} does not exist, created one with default attributes")


if __name__ == "__main__":

    args = initialise()
    chkpnt = Checkpoint(args.checkpoint_path)

    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d')
    model_base = args.model or config[args.model_key_base]["model_key"]

    config_editor = ConfigEditor(args.config)
    config_editor.verify_config(args.client, args.model_key)
    config_editor.save_model_key(args.model_key,
                                 model_type=chkpnt["model"] or args.model,
                                 data_path=args.data_path,
                                 date=now,
                                 temperature=args.temperature,
                                 top_p=args.top_p,
                                 max_tokens=args.max_tokens)
