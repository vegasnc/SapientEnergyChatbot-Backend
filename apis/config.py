from flask import Flask
import requests
import apis.constapis as constapis


class ExplorerClass:
    ConstAPIClass = None

    def __init__(self) -> None:
        self.ConstAPIClass = constapis.APIClass()

    def get_metadata(self, building_id, search_key=""):
        payload = {
            "building_id": building_id,
            "search": search_key
        }
        response = requests.get(constapis.BASE_URL + constapis.GET_BUILDING,
                                params=payload, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

