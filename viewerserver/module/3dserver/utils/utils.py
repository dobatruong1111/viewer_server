import requests
from typing import Optional
import os

class MyAuth(requests.auth.AuthBase):
    def __init__(self, auth):
        self._auth = auth
    def __call__(self, r):
        # Implement my authentication
        r.headers['Authorization'] = self._auth
        return r
    
def getInfoMemory(self) -> Optional[tuple]:
    try:
        total_memory, used_memory, free_memory = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
        return (total_memory, used_memory, free_memory)
    except:
        return None