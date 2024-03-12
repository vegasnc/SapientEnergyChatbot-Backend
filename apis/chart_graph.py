from flask import Flask
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session

import requests
import apis.constapis as constapis
import apis.userapi as userapi

class ChatGraph:
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

    def get_chart_data(self, date_from, date_to, aggregate = "month", building_id = "", aggregation_type="sum",
                     minute="1", consumption="energy"):
        # if user is logged in
        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern"
        }
        timeout_value = 30
        if aggregate != "month":
            payload = {
                "aggregate" : aggregate
            }
            
            # response = requests.request("POST", constapis.BASE_URL + constapis.GET_CHART_DATA,
            #                             params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
            response = self.session.post(constapis.BASE_URL + constapis.GET_CHART_DATA, 
                                        timeout=timeout_value, params=payload, json=data, 
                                        headers=self.ConstAPIClass.getHeader())
        else:
            # response = requests.request("POST", constapis.BASE_URL + constapis.GET_CHART_DATA,
            #                             data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
            response = self.session.post(constapis.BASE_URL + constapis.GET_CHART_DATA, 
                                        timeout=timeout_value, json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return 404
        else:
            return response.json()
    
    def get_hourly_data(self, date_from, date_to, building_id):
        payload = {
            "building_id": building_id,
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern"
        }
        # response = requests.request("POST", constapis.BASE_URL + constapis.GET_HOURLY_DATA,
        #                             params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.GET_HOURLY_DATA, 
                                    timeout=30, params=payload, json=data, 
                                    headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return 404
        else:
            return response.json()
