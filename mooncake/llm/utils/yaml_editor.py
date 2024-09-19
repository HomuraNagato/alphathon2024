
import argparse
from pathlib import Path
import os
import sys
import yaml

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from utils.utilities import _open, create_path, get_logger

def initialise():

    parse = argparse.ArgumentParser(
        description="update a config with params",
        epilog="example: python yaml_editor.py --checkpoint_path /tmp/senzai_intermediary.yaml")
    parse.add_argument("--checkpoint_path",
                       nargs="?",
                       default="/tmp/senzai/checkpoint.yaml",
                       help="path to yaml used to store temporary data to recover during fine-tune")
    args = parse.parse_args()

    return args

class YamlEditor:

    def __init__(self, path, log_name="yaml_editor"):
        self.path = Path(path)
        self.rel_dir = os.environ.get("REL_DIR", "")
        self.log = get_logger(log_name)
        self.ydict = self.open_yaml()

    def __getitem__(self, key):
        return self.ydict.get(key)

    def __str__(self):
        return f"{self.ydict}"

    def save(self):
        f = open(self.path, 'w')
        for key, value in self.ydict.items():
            d = {key: value}
            f.write("\n")
            f.write(yaml.dump(d, allow_unicode=True, indent=4))
        f.close()

    def chmod(self, val):
        os.chmod(self.path, val)

    def open_yaml(self):
        if not self.path.exists():
            create_path(self.path)
            self.path.touch()
        d = _open(self.path) or {}
        return d

    def remove_key(self, key):
        del self.ydict[key]

    def remove_yaml(self):
        self.path.unlink()

    def save_model_key(self, key, **kwargs):
        
        self.update_key(key, kwargs)
        self.save()
        self.log.info(f"{self.path} has been updated")

        return self.ydict

    def update_key(self, key, values):
        self.ydict[key] = values


class Checkpoint(YamlEditor):

    def __init__(self, checkpoint_path=None):
        if not checkpoint_path:
            checkpoint_path = "/tmp/llm/checkpoint.yaml"
        YamlEditor.__init__(self, checkpoint_path, "chkpnt")


if __name__ == "__main__":

    args = initialise()

    checkpoint = Checkpoint(args.checkpoint_path)
    #checkpoint.update_key("model", "ft_id::11000")
    #checkpoint.update_key("batch_fileid", "file-CbbeK4fUbWSMfImX3jNNQWrt")
    checkpoint.remove_key("batch_batchid")
    checkpoint.remove_key("batch_fileid")
    checkpoint.save()
    #checkpoint.remove_yaml()

