from flask import Flask
import requests
import apis.constapis as constapis
import apis.userapi as userapi
import datetime

class EndUsesClass:
    ConstAPIClass = None
    UserAPIClass = None

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

        response = requests.post(constapis.BASE_URL + constapis.GET_ENERGY_ENDUSE_LOAD_USAGE, json=data,
                                 params=payload, headers=self.ConstAPIClass.getHeader())
        
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()