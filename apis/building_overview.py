from flask import Flask
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session

import requests
import apis.constapis as constapis
import apis.userapi as userapi
import datetime

class BuildingOverviewClass:
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

    def energy_building_equipment_overview(self, building_id, date_from, date_to):
        payload = {
            "building_id": building_id
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        # response = requests.request("POST", constapis.BASE_URL + constapis.GET_ENERGY_BUILDING_EQUIPMENT,
        #                             params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        
        timeout_value = 30
        response = self.session.post(constapis.BASE_URL + constapis.GET_ENERGY_BUILDING_EQUIPMENT, 
                                     timeout=timeout_value, params=payload, json=data, 
                                     headers=self.ConstAPIClass.getHeader())
        
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()