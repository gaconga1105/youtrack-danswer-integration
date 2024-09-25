# Danswer Ingestion Client
import requests

class DanswerAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def post_ingest_document(self, document):
        url = f"{self.base_url}/danswer-api/ingestion"
        response = requests.post(url, headers=self.headers, json=document)
        response.raise_for_status()
        return response.json()

    def get_info(self):
        return {
            "base_url": self.base_url
        }

    def is_active(self):
        """
        Checks if the Danswer API is active by sending a GET request to the default connector-docs endpoint.

        Parameters:
        None

        Returns:
        bool: True if the API is active (200 status code), False otherwise.
        """
        url = f"{self.base_url}/danswer-api/connector-docs/0"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200

