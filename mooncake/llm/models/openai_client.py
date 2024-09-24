
from openai import OpenAI
import os
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from llm.utils.utilities import _open

class OpenAIClient:

    def __init__(self):
        self.client = self.openai_client()

    def openai_client(self):
        #key = os.environ.get("OPENAI_API_KEY")
        key = "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"
        client = OpenAI(api_key=key)
        return client

    def call_batch(self, fileid):
        response = self.client.batches.create(
            input_file_id=fileid,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        return response

    def call_train(self, model, training_file):
        response = self.client.fine_tuning.jobs.create(
            training_file=training_file,
            model=model
        )
        return response

    def embedding_model(self, texts, model="text-embedding-3-small"):
        # reference: https://platform.openai.com/docs/guides/embeddings/use-cases
        if type(texts) == str:
            texts = [texts]
        texts = [x.replace("\n", " ") for x in texts]
        res = self.client.embeddings.create(input=texts, model=model)
        res = [x.embedding for x in res.data]
        return res

    def list_gen(self, func, limit=3):
        response = func.list()
        for idx, res in enumerate(response):
            if idx >= limit:
                break
            print(res)

    def list_batches(self, limit=3):
        self.list_gen(self.client.batches, limit=limit)

    def list_files(self, limit=3):
        response = self.client.files.list()
        for idx, res in enumerate(response):
            if idx >= limit:
                break
            print(res)

    def list_fine_tuning(self, limit=3):
        response = self.client.fine_tuning.jobs.list(limit=limit)
        for idx, res in enumerate(response):
            if idx >= limit:
                break
            print(res)


    def upload_file(self, messages_file, purpose="fine-tune"):
        
        response = self.client.files.create(
            file=open(str(messages_file), "rb"),
            purpose=purpose
        )
        return response
    
