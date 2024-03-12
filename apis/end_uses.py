from flask import Flask
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session

import requests
import apis.constapis as constapis
import apis.userapi as userapi
import datetime

class EndUsesClass:
    ConstAPIClass = None
    UserAPIClass = None
    session = Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    def __init__(self) -> None:
        self.ConstAPIClass = constapis.APIClass()
        self.UserAPIClass = userapi.UserAPI()

    def energy_end_use_load_usage(self, building_id, end_uses_type, date_from, date_to):
        payload = {
            "building_id": building_id, # HVAC, Lighting, Plug, Process, Other
            "consumption": "energy",
            "aggregate_type": "sum",
            "minute": 1,
            "end_uses_type": end_uses_type
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }
        
        # response = requests.request("POST", constapis.BASE_URL + constapis.GET_ENERGY_ENDUSE_LOAD_USAGE,
        #                             params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        
        response = self.session.post(constapis.BASE_URL + constapis.GET_ENERGY_ENDUSE_LOAD_USAGE, 
                                     timeout=30, params=payload, json=data, headers=self.ConstAPIClass.getHeader())
        
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()