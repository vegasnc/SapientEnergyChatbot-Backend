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

    def getChartData(self, date_from, date_to, building_id = "", aggregate = "month", aggregation_type="sum",
                     minute="1", consumption="energy"):
        if self.UserAPIClass.check_user_login_status():
            # if user is logged in
            data = {
                "date_from": date_from,
                "date_to": date_to,
                "tz_info": "US/Eastern"
            }
            response = requests.post(constapis.BASE_URL + constapis.GET_CHART_DATA, json=data,
                                    headers=self.ConstAPIClass.getHeader())
            print("-------------")
            print(response)
            if response.status_code != 200:
                return 404
            else:
                return response.json()
        else:
            return 404
