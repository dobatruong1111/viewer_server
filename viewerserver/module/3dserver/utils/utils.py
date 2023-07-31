import requests

class MyAuth(requests.auth.AuthBase):
    def __init__(self, auth):
        self._auth = auth
    def __call__(self, r):
        # Implement my authentication
        r.headers['Authorization'] = self._auth
        return r