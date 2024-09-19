
import numpy as np
import os
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from algorithms.similarity import cosine_similarity_vec
from models.openai_client import OpenAIClient
from utils.utilities import get_logger, _open


class TextPreparatory:

    def __init__(self):
        self.openai = OpenAIClient()
        self.log_agent = get_logger("text_prep")

    def subspace_topk(self, texts, subspace, k=1):
        """
        texts str or list[str]
        subspace list[str]

        dimensions
        texts_vec         n_texts x embedding_size
        subspace_vec      n_categories x embedding_size
        vec_similarities  n_texts x n_categories
        res               n_texts x k
        """
        if len(subspace) == 0:
            return
        k = min(k, len(subspace))
        # convert to list and lowercase as embedding is case sensitive
        texts = np.char.lower(np.array(texts).astype(str))
        subspace = np.char.lower(np.array(subspace).astype(str))
        # step 01   transform into embedding space
        texts_vec = self.openai.embedding_model(texts)
        subspace_vec = self.openai.embedding_model(subspace)
        # step 02   map to subspace
        vec_similarities = cosine_similarity_vec(texts_vec, subspace_vec)
        res = []
        #step 03   find topk and map to subspace
        for vec in vec_similarities:
            topk = sorted(enumerate(vec), key=lambda x: x[1], reverse=True)[:k]  # k x 2
            topk = [ { "category": subspace[i], "probability": v } for i, v in topk ] # k x 1
            res.append(topk)

        return res

    def dict_to_list(self, destem_template, **kwargs):
        """
        arguments
        kwarg 1:    key01=['a', 'b', 'c']
        kwarg 2:    key02=['1', '2', '3']

        intermediary
        zipped:     [('key01 a', 'key02 1'), ('key01 b', 'key02 2'), ('key01 c', 'key02 3')]

        res str[]   ['key1 value1 .. keyN value1', 'key1 value2 .. keyN value2', ...]
                    where each value associated with each key
        """
        res = []
        zipped = []
        for key, values in kwargs.items():
            zipped_i = [ (f"{key}: {v}") for v in values ]
            zipped.append(zipped_i)
        zipped = list(zip(*zipped))

        for prompts in zipped:
            input_text = ' '.join(text for text in prompts)
            s = destem_template.format(input_text)
            res.append(s)

        return res

    def generate_prompts(self, prompt_template, prompts, categories):
        # assumes prompt_template has two curly brackets for two injected variables

        res = []
        categories_str = ", ".join(categories)
        for prompt in prompts:
            res.append(prompt_template.format(prompt, categories_str))

        return res

    def prep_messages(self, system_str="", prompts=[], truths=[]):
        # system_msg and truths might be empty
        messages = []
        d_system = {}
        n = len(prompts)

        if truths and len(prompts) != len(truths):
            raise Exception("the number of truths doesn't match the number of prompts")

        def role_content(role, content):
            d = { "role": role, "content": content }
            return d

        if system_str:
            d_system = role_content("system", system_str)

        for i in range(n):
            msg_pkg = []
            # add system message if included
            if d_system:
                msg_pkg.append(d_system)

            # should always add prompt
            d_prompt = role_content("user", prompts[i])
            msg_pkg.append(d_prompt)

            # add truth if included
            if truths:
                d_truth = role_content("assistant", truths[i])
                msg_pkg.append(d_truth)

            messages.append(msg_pkg)

        return messages

    def prep_messages_batch(self, messages, model_config={}):

        messages_jsonl = []

        for idx, msg in enumerate(messages):
            tmp = {
                "custom_id": str(idx),
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "max_tokens": model_config["max_tokens"],
                    "model": model_config["model_type"],
                    "messages": msg,
                    "temperature": model_config["temperature"],
                    "top_p": model_config["top_p"]
                } }
            messages_jsonl.append(tmp)

        return messages_jsonl

    def unwrap_message_batch(self, fpath):
        
        contents = _open(fpath)
        res = []

        for content in contents:
            idx = int(content["custom_id"])
            cnt = content["response"]["body"]["choices"][0]["message"]["content"]
            res.append((idx, cnt))

        # use key to return response in same order as request
        res = sorted(res, key=lambda x: x[0])
        res = [ x[1] for x in res ]

        return res
