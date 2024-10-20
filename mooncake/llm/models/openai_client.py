
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
        key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=key)
        return client

    def call_batch(self, fileid: str):
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

    def delete_file(self, file_id: str):
        response = self.client.files.delete(file_id=file_id)
        return response

    def get_file_details(self, file_id: str):
        response = self.client.files.retrieve(file_id=file_id)
        return response

    def get_fine_tuning_details(self, job_id: str):
        response = self.client.fine_tuning.jobs.retrieve(id=job_id)
        return response

    def cancel_fine_tuning(self, job_id: str):
        response = self.client.fine_tuning.jobs.cancel(id=job_id)
        return response

    def call_completion(self, prompt: str, model="gpt-3.5-turbo", max_tokens=100):
        response = self.client.completions.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens
        )
        return response

    def get_batch_status(self, batch_id: str):
        response = self.client.batches.retrieve(id=batch_id)
        return response
