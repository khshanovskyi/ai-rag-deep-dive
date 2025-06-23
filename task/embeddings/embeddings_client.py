import json

import requests

DIAL_EMBEDDINGS = 'https://ai-proxy.lab.epam.com/openai/deployments/{model}/embeddings'


class DialEmbeddingsClient:
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str, api_key: str):
        if not api_key or api_key.strip() == "":
            raise ValueError("API key cannot be null or empty")

        self._endpoint = DIAL_EMBEDDINGS.format(
            model=deployment_name
        )
        self._api_key = api_key

    def get_embeddings(
            self, inputs: str | list[str],
            dimensions: int,
            print_response: bool = False
    ) -> dict[int, list[float]]:
        """
        Generate dict of indexed embeddings:
            inputs[0](text) -> [0][embedding]
            inputs[1](text) -> [1][embedding]
            ...

        Args:
            inputs: input text, can be singular string or list of strings
            dimensions: number of dimensions
            print_response: to print response in chat or not
        """

        print(f"Searching similarities for `{inputs}` \nAnd such dimensions: {dimensions}\n📋Results:\n")

        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        request_data = {
            "input": inputs,
            "dimensions": dimensions,
        }

        response = requests.post(url=self._endpoint, headers=headers, json=request_data, timeout=60)

        if response.status_code == 200:
            response_json = response.json()
            data = response_json.get("data", [])
            if print_response:
                print("\n" + "=" * 50 + " RESPONSE " + "=" * 50)
                print(json.dumps(response_json, indent=2))
                print("=" * 108)
            return self._from_data(data)
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    def _from_data(self, data: list[dict]) -> dict[int, list[float]]:
        return {embedding_obj['index']: embedding_obj['embedding'] for embedding_obj in data}
