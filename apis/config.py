from flask import Flask
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session

import requests
import apis.constapis as constapis

class ExplorerClass:
    ConstAPIClass = None
    session = Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    def __init__(self) -> None:
        self.ConstAPIClass = constapis.APIClass()

    def get_metadata(self, building_id, search_key=""):
        payload = {
            "building_id": building_id,
            "search": search_key
        }
        # response = requests.request("POST", constapis.BASE_URL + constapis.GET_BUILDING,
        #                             params=payload, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.GET_BUILDING, 
                                     timeout=30, params=payload, headers=self.ConstAPIClass.getHeader())
                                     
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

