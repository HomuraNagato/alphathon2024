
import os
from pathlib import Path
import sys

sys.path.append(str(Path(os.getcwd(), os.environ.get("REL_DIR", ""))))

from models.openai_client import OpenAIClient

class OpenAIModels(OpenAIClient):

    def __init__(self):
        OpenAIClient.__init__(self)

    def de_stemming_model(self, message, config: dict):
        """
        response = self.client.chat.completions.create(
            model=config['model_type'],
            messages=[
                {'role': 'user', 'content': f"{prompt}"}
            ],
            temperature=config['temperature'],  # Adjust the temperature here (typically between 0.1 and 1.0)
            max_tokens=config['max_tokens'],  # Maximum tokens in the generated response
            top_p=config['top_p'],  # Adjust the nucleus sampling probability (typically between 0.1 and 1.0)
        )
        """
        response = self.client.chat.completions.create(
            model=config['model_type'],
            messages=message,
            temperature=config['temperature'],  # Adjust the temperature here (typically between 0.1 and 1.0)
            max_tokens=config['max_tokens'],  # Maximum tokens in the generated response
            top_p=config['top_p'],  # Adjust the nucleus sampling probability (typically between 0.1 and 1.0)
        )
        return response.choices[0].message.content

    def classification_model(self, prompt, config: dict):
        response = self.client.chat.completions.create(
            model=config['model_type'],
            # model = 'gpt-3.5-turbo-1106',
            # model = "ft:gpt-3.5-turbo-1106:personal::8k9b2Hie",

            messages=[
                {'role': 'system',
                 'content': "Ensure that the generated output aligns with one of the predefined categories provided. Avoid generating content that does not belong to any of these specified categories."},
                {'role': 'user',
                 'content': prompt}],
            temperature=config['temperature'],  # Adjust the temperature here (typically between 0.1 and 1.0)
            max_tokens=config['max_tokens'],  # Maximum tokens in the generated response
            top_p=config['top_p'],  # Adjust the nucleus sampling probability (typically between 0.1 and 1.0)
        )
        return response.choices[0].message.content

    def api_model(self, prompt, config):
        response = self.client.chat.completions.create(
            model=config['model_type'],
            messages=[{"role": "user", "content": prompt}],

            temperature=config['temperature'],  # Adjust the temperature here (typically between 0.1 and 1.0)
            max_tokens=config['max_tokens'],  # Maximum tokens in the generated response
            top_p=config['top_p'],  # Adjust the nucleus sampling probability (typically between 0.1 and 1.0)
        )
        return response.choices[0].message.content
