
import argparse
import os
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from llm.models.openai_liaison import liaison_finetune
from llm.utils.yaml_editor import Checkpoint

def initialise():

    parse = argparse.ArgumentParser(
        description="use formatted data to fine-tune a chatgpt model",
        epilog="example: python models/train/finetune_model.py file-9VH16KcX3xL6tPLOlulJ49TQ")
    parse.add_argument("--message_path",
                       required=True,
                       help="path to messages file that will be used for training; jsonl extension")
    parse.add_argument("--checkpoint_path",
                       nargs="?",
                       default="/tmp/llm/checkpoint.yaml",
                       help="if provided, location to store checkpoint variables to restore from crash")
    parse.add_argument("--model",
                       nargs="?",
                       default="gpt-4o-mini-2024-07-18",
                       help="the model to use as base upon which fine-tuning will occur")
    args = parse.parse_args()

    return args

if __name__ == "__main__":

    args = initialise()
    chkpnt = Checkpoint()

    ft_model = liaison_finetune(args.message_path, chkpnt, args.model)
    chkpnt.update_key("model", ft_model)

    print(ft_model)
