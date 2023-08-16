from flask import Flask
import requests
import apis.constapis as constapis
import apis.userapi as userapi

class ChatGraph:
    ConstAPIClass = None
    UserAPIClass = None
    
    def __init__(self) -> None:
        self.ConstAPIClass = constapis.APIClass()
        self.UserAPIClass = userapi.UserAPI()

    def get_chart_data(self, date_from, date_to, aggregate = "month", building_id = "", aggregation_type="sum",
                     minute="1", consumption="energy"):
        if self.UserAPIClass.check_user_login_status():
            # if user is logged in
            data = {
                "date_from": date_from,
                "date_to": date_to,
                "tz_info": "US/Eastern"
            }
            if aggregate != "month":
                payload = {
                    "aggregate" : aggregate
                }
                
                response = requests.post(constapis.BASE_URL + constapis.GET_CHART_DATA, json=data,
                                        params=payload, headers=self.ConstAPIClass.getHeader())
            else:
                response = requests.post(constapis.BASE_URL + constapis.GET_CHART_DATA, json=data,
                                    headers=self.ConstAPIClass.getHeader())
            if response.status_code != 200:
                return 404
            else:
                return response.json()
        else:
            return 404
    
    def get_hourly_data(self, date_from, date_to, building_id):
        if self.UserAPIClass.check_user_login_status():
            # if user is logged in
            payload = {
                "building_id": building_id,
            }

            data = {
                "date_from": date_from,
                "date_to": date_to,
                "tz_info": "US/Eastern"
            }
            response = requests.post(constapis.BASE_URL + constapis.GET_HOURLY_DATA, json=data,
                                    params=payload, headers=self.ConstAPIClass.getHeader())
            if response.status_code != 200:
                return 404
            else:
                return response.json()
        else:
            return 404
