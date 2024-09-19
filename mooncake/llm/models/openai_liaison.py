
import openai
import os
from pathlib import Path
import sys
import threading
import time

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from models.openai_client import OpenAIClient
from utils.config_editor import Checkpoint
from utils.utilities import get_logger, _open

class OpenAILiaison(threading.Thread, OpenAIClient):

    def __init__(self, name):
        threading.Thread.__init__(self)
        OpenAIClient.__init__(self)
        self.name = name
        self.log = get_logger("thread")
        self.completion = False
        self.error = None

    def run(self, func):

        try:
            func()
            self.completion = True

        except openai.NotFoundError as err:
            self.log.error(err)
            self.error = err

        except Exception as err:
            self.log.error(err)
            self.error = err


class LiaisonFile(OpenAILiaison):

    def __init__(self, fileid, name="file-observer"):
        OpenAILiaison.__init__(self, name)
        self.fileid = fileid
        self.sleep_time = 2

    def _run(self):
        while self.client.files.retrieve(self.fileid).status != "processed":
            self.log.info(f"sleeping {self.sleep_time} seconds before checking whether {self.fileid} has been uploaded")
            time.sleep(self.sleep_time)

        self.log.info(f"{self.fileid} has been successfully uploaded to openai")

    def run(self):

        super().run(self._run)


class LiaisonFinetune(OpenAILiaison):

    def __init__(self, finetuneid, name="finetune-observer"):
        OpenAILiaison.__init__(self, name)
        self.finetuneid = finetuneid
        self.sleep_time = 60
        self.ft_model = None

    def _run(self):        

        res = False

        while not res:

            tmp = self.client.fine_tuning.jobs.retrieve(self.finetuneid)
            if tmp.status == "succeeded":
                res = tmp
                break
            elif tmp.status == "failed" or tmp.status == "cancelled":
                raise Exception(tmp)

            self.log.info(f"sleeping {self.sleep_time} seconds before checking whether {self.finetuneid} has completed")
            time.sleep(self.sleep_time)

        self.ft_model = res.fine_tuned_model
        self.log.info(f"{self.finetuneid} with ft_model_id {self.ft_model} has finished fine-tuning and is ready for testing or use")

    def run(self):

        super().run(self._run)

class LiaisonChat(OpenAILiaison):

    def __init__(self, batchid, content_file, name="chat-observer"):
        OpenAILiaison.__init__(self, name)
        self.batchid = batchid
        self.output_file_id = None
        self.content_file = content_file
        self.sleep_time = 15

    def _run(self):

        res = False
        failure_msgs = ["cancelling", "cancelled", "expired", "failed"]

        while not res:

            tmp = self.client.batches.retrieve(self.batchid)
            print(tmp, tmp.status)
            if tmp.status == "completed":
                res = tmp
                break
            elif tmp.status in failure_msgs:
                raise Exception(tmp)

            self.log.info(f"sleeping {self.sleep_time} seconds before checking whether {self.batchid} has completed")
            time.sleep(self.sleep_time)

        self.output_file_id = res.output_file_id
        content = self.client.files.content(self.output_file_id)
        content.stream_to_file(self.content_file)
        self.log.info(f"{self.batchid} with file output id {self.output_file_id} has finished")


    def run(self):

        super().run(self._run)

def liaison_batch(file_path, content_path, checkpoint_path=None):

    openai_client = OpenAIClient()
    checkpoint = Checkpoint(checkpoint_path)
    fileid = checkpoint["batch_fileid"]
    batchid = checkpoint["batch_batchid"]

    if not fileid:
        response = openai_client.upload_file(file_path, purpose="batch")
        fileid = response.id
        checkpoint.update_key("batch_fileid", fileid)
        checkpoint.save()

    ldestem = LiaisonFile(fileid)
    ldestem.start()
    ldestem.join()

    if not batchid:
        response = openai_client.call_batch(fileid)
        batchid = response.id
        checkpoint.update_key("batch_batchid", batchid)
        checkpoint.save()

    lchat = LiaisonChat(batchid, content_path)
    lchat.start()
    lchat.join()

    checkpoint.remove_key("batch_fileid")
    checkpoint.remove_key("batch_batchid")
    checkpoint.save()

    return 0

def liaison_finetune(data_path, checkpoint_path=None, model="gpt-4o-mini"):

    openai_client = OpenAIClient()
    checkpoint = Checkpoint(checkpoint_path)
    fileid = checkpoint["ft_fileid"]
    ftid = checkpoint["ft_id"]

    if not fileid:
        response = openai_client.upload_file(data_path)
        fileid = response.id
        checkpoint.update_key("ft_fileid", fileid)
        checkpoint.save()

    lfile = LiaisonFile(fileid)
    lfile.start()
    lfile.join()

    if not ftid:
        response = openai_client.call_train(model, fileid)
        ftid = response.id
        checkpoint.update_key("ft_id", ftid)
        checkpoint.save()

    lfinetune = LiaisonFinetune(ftid)
    lfinetune.start()
    lfinetune.join()

    #checkpoint.remove_key("ft_fileid")
    #checkpoint.remove_key("ft_id")
    #checkpoint.save()

    return lfinetune.ft_model
    
