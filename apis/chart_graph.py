from flask import Flask
import requests
import apis.constapis as constapis

class ChatGraph:
    ConstAPIClass = None
    
    def __init__(self) -> None:
        self.ConstAPIClass = constapis.APIClass()

    def getChartData(self, date_from, date_to, building_id = "", aggregate = "", aggregation_type="sum",
                     minute="1", consumption="energy"):
        payload = {
            "aggregate": aggregate,
            "aggregation_type": aggregation_type,
            "minute": minute,
            "building_id": building_id,
            "consumption": consumption
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern"
        }
    
        response = requests.post(constapis.BASE_URL + constapis.GET_CHART_DATA, json=data,
                                 params=payload, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
