import requests
from urllib.parse import urlparse

class YouTrackAPI:
    def __init__(self, base_url, token, use_https=True, verify_ssl=True):
        parsed_url = urlparse(base_url)
        self.scheme = 'https' if use_https else 'http'
        self.base_url = f"{self.scheme}://{parsed_url.netloc}"
        self.headers = {"Authorization": f"Bearer {token}"}
        self.verify_ssl = verify_ssl

    def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        kwargs['headers'] = self.headers
        kwargs['verify'] = self.verify_ssl
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def get_issues(self, project_id, max_results=100, fields=None):
        endpoint = "/api/issues"
        params = {
            "project": project_id,
            "$top": max_results,
            "fields": fields
        }
        return self._make_request('GET', endpoint, params=params).json()

    def get_issue_from_query(self, query, fields=None, batch_size=200):
        endpoint = "/api/issues"
        params = {
            "query": query,
            "fields": fields,
            "$top": batch_size,
            "$skip": 0
        }

        all_issues = []
        while True:
            response = self._make_request('GET', endpoint, params=params).json()
            if not response:
                break
            all_issues.extend(response)
            params["$skip"] += batch_size
            if len(response) < batch_size:
                break

        return all_issues

    def get_info(self):
        return {
            "base_url": self.base_url,
            'scheme': self.scheme,
            'verify_ssl': self.verify_ssl
        }

    # a method to check status of the API
    def is_active(self):
        """
        Checks if the YouTrack API is active by sending a GET request to the projects endpoint.

        Returns:
            bool: True if the API is active, False otherwise.
        """
        endpoint = "/api/admin/projects"
        response = self._make_request(method='GET', endpoint=endpoint)
        return response.status_code == 200
