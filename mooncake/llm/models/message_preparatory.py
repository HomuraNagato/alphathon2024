
import argparse
import os
import pandas as pd
from pathlib import Path
import sys
import json

#sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))
sys.path.append("/home/mooncake")

from llm.constants.constants_llm import ConstantsLLM
from llm.models.openai_liaison import liaison_batch, liaison_finetune
from llm.models.text_preparatory import TextPreparatory
from llm.utils.yaml_editor import Checkpoint
from llm.utils.utilities import create_path, inspect_df, _open

class MessageEngine:

    def __init__(self, config, checkpoint: Checkpoint):
        self.checkpoint = checkpoint if checkpoint else Checkpoint()
        self.cnst = ConstantsLLM()
        self.config = config
        self.text_preparatory = TextPreparatory()

    def prep_df(self, data_path):
        # load data, filter to columns with content as input to prompts
        df = pd.read_csv(data_path)
        df = df.dropna(axis=1, how="all")
        df = df.fillna("")
        return df

    def sample(self, df, sample_size):
        if 0 < sample_size < df.shape[0]:
            sample_idx = df.sample(n=sample_size).index
            df = df.loc[sample_idx,:]
        return df

    def solicitation_destem(self, df):
        # few steps to prep df -> list of strings for request batch

        tmp_destem_req = Path(self.checkpoint.pdir / "destem_request.jsonl")
        tmp_destem_res = Path(self.checkpoint.pdir / "destem_response.jsonl")

        # already completed
        if self.verify_checkpoint(tmp_destem_res):
            s03 = self.text_preparatory.unwrap_message_batch(tmp_destem_res)
            return s03

        # prep
        if self.cnst.true_category in df.columns:
            d = df.drop(columns=[self.cnst.true_category]).to_dict(orient="list")
        else:
            d = df.to_dict(orient="list")

        s00 = self.text_preparatory.generate_destems(self.config["destem_template"], **d)
        s01 = self.text_preparatory.prep_messages(prompts=s00)
        s02 = self.text_preparatory.prep_messages_batch(s01, self.config["destem_model"])
        self.save_messages(tmp_destem_req, s02)

        # solicitation
        res = liaison_batch(tmp_destem_req, tmp_destem_res, self.checkpoint)
        s03 = self.text_preparatory.unwrap_message_batch(tmp_destem_res)

        return s03

    def save_messages(self, message_path, messages):

        create_path(message_path)
        f = open(message_path, "w")
        for message in messages:
            message = json.dumps(message)
            f.write(f"{message}\n")
        f.close()

        print(f"messages are prepared at {message_path}")

    def set_config(self, config):
        self.config = config

    def update_df(self, df, col_name, col_cells, save_path=""):

        df[col_name] = col_cells

        # only save if save_path provided
        if save_path:
            create_path(save_path)
            df.to_csv(save_path, index=False)
            print(f"{col_name} has been included in the dataframe and stored at {save_path}")

        return df

    def verify_checkpoint(self, fpath):
        #res = self.checkpoint_dir and Path(self.checkpoint_dir).exists() and Path(fpath).exists()
        res = Path(fpath).exists()
        if res:
            print(f"checkpoint found for {fpath}")
        return res


class MessageTrainEngine(MessageEngine):

    def __init__(self, config, checkpoint: Checkpoint=None):
        MessageEngine.__init__(self, config, checkpoint)

    def prep_train(self, df, message_path):
        
        if self.verify_checkpoint(message_path):
            return

        truths = df.loc[:,self.cnst.true_category].tolist()
        # prep
        if self.cnst.true_category in df.columns:
            d = df.drop(columns=[self.cnst.true_category]).to_dict(orient="list")
        else:
            d = df.to_dict(orient="list")

        template = "{}"
        texts = self.text_preparatory.dict_to_list(template, **d)
        #texts = self.text_preparatory.prep_messages(prompts=s00)
        
        # messages with true category
        # categories are intersect of those in data and those suggested by config
        categories = list(set([ x.lower() for x in truths ]))
        if self.config["categories"]:
            categories = set(categories)
            config_categories = set([ x.lower() for x in self.config["categories"] ])
            categories = list(config_categories & categories)
        else:
            print("no categories found in config; will use those found in truth column")

        prompts = self.text_preparatory.generate_prompts(self.config["prompt_template"],
                                                         texts,
                                                         categories)
        msgs = self.text_preparatory.prep_messages(system_str=self.config["system_msgs"]["classification"],
                                                   prompts=prompts,
                                                   truths=truths)
        msgs_dict = [ { "messages": msg } for msg in msgs ]

        self.save_messages(message_path, msgs_dict)
        

class MessageTestEngine(MessageEngine):

    def __init__(self, config, checkpoint: Checkpoint=None):
        MessageEngine.__init__(self, config, checkpoint)
        self.path_cls_req = Path(self.checkpoint.pdir / "cls_request.jsonl")
        self.path_cls_res = Path(self.checkpoint.pdir / "cls_response.jsonl")

    def solicitation_test(self, df, model_key, sample_size=0):
        # messages without true category
        # note, message_json's for chat completion are different than fine-tuning

        # prep
        if self.cnst.true_category in df.columns:
            d = df.drop(columns=[self.cnst.true_category]).to_dict(orient="list")
        else:
            d = df.to_dict(orient="list")

        template = "{}"
        texts = self.text_preparatory.dict_to_list(template, **d)

        prompts = self.text_preparatory.generate_prompts(self.config["prompt_template"],
                                                         texts,
                                                         self.config["categories"])

        if self.path_cls_res.exists():
            res = self.text_preparatory.unwrap_message_batch(str(self.path_cls_res))
            return prompts, res

        msgs = self.text_preparatory.prep_messages(system_str=self.config["system_msgs"]["classification"],
                                                   prompts=prompts)

        msgs_jsonl = self.text_preparatory.prep_messages_batch(msgs, self.config[model_key])
        self.save_messages(str(self.path_cls_req), msgs_jsonl)
        
        # solicitation
        openai_res = liaison_batch(self.path_cls_req, self.path_cls_res, self.checkpoint)
        res = self.text_preparatory.unwrap_message_batch(self.path_cls_res)
        
        return prompts, res
