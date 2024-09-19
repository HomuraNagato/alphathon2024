
import json
import os
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from models.message_preparatory import MessageEngine
from models.openai_client import OpenAIClient
from models.openai_liaison import LiaisonChat, LiaisonFile, LiaisonFinetune
from models.text_preparatory import TextPreparatory
from utils.utility import create_path

def request_destem(text, config, path_destem_req, path_destem_res):
    # destem requests

    message_engine = MessageEngine()
    text_preparatory = TextPreparatory()

    s01 = text_preparatory.prep_messages(prompts=text)
    s02 = text_preparatory.prep_messages_batch(s01, config["destem_model"])
    message_engine.save_messages(path_destem_req, s02)

    res = liaison_batch(path_destem_req, path_destem_res)
    s03 = text_preparatory.unwrap_message_batch(path_destem_res)

    return s03

def request_classification(text, config, model_key, path_cls_req, path_cls_res):
    # train requests

    message_engine = MessageEngine()
    text_preparatory = TextPreparatory()

    s04 = text_preparatory.prep_messages(system_str=config["system_msgs"]["classification"],
                                         prompts=text)
    s05 = text_preparatory.prep_messages_batch(s04, config[model_key])
    message_engine.save_messages(path_cls_req, s05)

    res = liaison_batch(path_cls_req, path_cls_res)
    s06 = text_preparatory.unwrap_message_batch(path_cls_res)

    return s06
