import os

from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class FoundryClient:

    def __init__(self):

        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://ai.azure.com/.default",
        )

        self.client = OpenAI(
            base_url=endpoint,
            api_key=token_provider,
        )

        self.model = os.getenv("MODEL_DEPLOYMENT")

    def stream_response(
        self,
        instructions,
        user_input,
        previous_response_id=None,
    ):

        return self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_input,
            previous_response_id=previous_response_id,
            stream=True,
        )