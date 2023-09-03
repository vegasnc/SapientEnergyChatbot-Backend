from flask import Flask
import requests
import apis.constapis as constapis
import apis.userapi as userapi
import datetime


class BuildingOverviewClass:
    ConstAPIClass = None
    UserAPIClass = None

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

        response = requests.post(constapis.BASE_URL + constapis.GET_ENERGY_BUILDING_EQUIPMENT, json=data,
                                 params=payload, headers=self.ConstAPIClass.getHeader())
        
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()