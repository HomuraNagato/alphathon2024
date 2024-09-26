
import argparse
from pathlib import Path
import os
import sys
import yaml

sys.path.append(os.getcwd())

from llm.utils.utilities import _open, create_path, get_logger

def initialise():

    parse = argparse.ArgumentParser(
        description="update a config with params",
        epilog="example: python yaml_editor.py --checkpoint_path /tmp/senzai_intermediary.yaml")
    parse.add_argument("--checkpoint_dir",
                       nargs="?",
                       default="/tmp/llm",
                       help="path to yaml used to store temporary data to recover during fine-tune")
    args = parse.parse_args()

    return args

class YamlEditor:

    def __init__(self, path, log_name="yaml_editor"):
        self.path = Path(path)
        self.rel_dir = os.environ.get("LLM_DIR", "")
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

    def get(self, key, default=None):
        return self.ydict.get(key, default)

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

    def __init__(self, checkpoint_dir=None):
        self.pdir = Path(checkpoint_dir) if checkpoint_dir else Path("/tmp/llm")
        checkpoint_path = Path(self.pdir / "checkpoint").with_suffix(".yaml")
        YamlEditor.__init__(self, checkpoint_path, "chkpnt")

    def remove(self):
        for path in self.pdir.iterdir():
            Path(path).unlink()
        self.pdir.rmdir()

if __name__ == "__main__":

    args = initialise()

    checkpoint = Checkpoint(args.checkpoint_dir)
    #checkpoint.update_key("model", "ft_id::11000")
    #checkpoint.update_key("batch_fileid", "file-CbbeK4fUbWSMfImX3jNNQWrt")
    checkpoint.remove_key("batch_batchid")
    checkpoint.remove_key("batch_fileid")
    checkpoint.save()
    #checkpoint.remove_yaml()

