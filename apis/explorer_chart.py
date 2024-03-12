from flask import Flask
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session

import requests
import apis.constapis as constapis
import apis.userapi as userapi
import datetime


class ExplorerClass:
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

    """
    @param
        search_by_name: string (any)
        date_from: string (yyyy-mm-dd)
        date_to: string (yyyy-mm-dd)
        consumption: string (energy/power)
        order_by: string (building_name/consumption/peak_power/square_footage/building_type/change)
        sort_by: string (ace/dce)
    """
    def get_building_list(self, date_from, date_to, search_by_name="", consumption="energy", order_by="consumption", sort_by="dce"):
        payload = {
            "search_by_name": search_by_name,
            "consumption": consumption,
            "order_by": order_by,
            "sort_by": sort_by
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        print(f"get_building_list before post")

        # response = requests.request("POST", constapis.BASE_URL + constapis.BUILDING_LIST,
        #                             params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.BUILDING_LIST, 
                                     timeout=30, params=payload, json=data, headers=self.ConstAPIClass.getHeader())
        
        print(f"get_building_list after post = {response.status_code}")
        
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def get_building(self, config=False):
        # if user is logged in
        payload = {
            "config": config
        }

        # response = requests.request("GET", constapis.BASE_URL + constapis.GET_BUILDING,
        #                             params=payload, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.get(constapis.BASE_URL + constapis.GET_BUILDING, 
                                     timeout=30, params=payload, headers=self.ConstAPIClass.getHeader())
        
        print(f"-----------get_building {str(response)}")
        
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    """
    @param
        building_id: string (any)
        search_by_name: string (any)
        consumption: string (energy/power)
        order_by: string (building_name/consumption/peak_power/square_footage/building_type/change)
        sort_by: string (ace/dce)
        date_from: string (yyyy-mm-dd)
        date_to: string (yyyy-mm-dd)
        location: string array (any)
        equipment_types: string array (any)
        end_use: string array (any)
        space_type: string array (any)
    """
    def get_equipment_list(self, building_id, date_from, date_to, search_by_name="", consumption="energy",
                           order_by="consumption", sort_by="dce", page_size="", page_no="",
                           location=[], equipment_types=[], end_use=[], space_type=[]):
        payload = {
            "building_id": building_id,
            "search_by_name": search_by_name,
            "consumption": consumption,
            "order_by": order_by,
            "sort_by": sort_by,
            "page_size": 1000,
            "page_no": 1
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        if len(location) != 0:
            data.update({ "location" : location })
        
        if len(equipment_types) != 0:
            data.update({ "equipment_types" : equipment_types })

        if len(end_use) != 0:
            data.update({ "end_use" : end_use })
        
        if len(space_type) != 0:
            data.update({ "space_type" : space_type })

        # response = requests.request("POST", constapis.BASE_URL + constapis.GET_EQUIPMENT_LIST,
        #                     params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.GET_EQUIPMENT_LIST, 
                                     timeout=30, params=payload, json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()        

    """
    @param
        building_id: string (any)
        date_from: string (yyyy-mm-dd)
        date_to: string (yyyy-mm-dd)
        consumption: string (energy/power)
        location: string array (any)
        equipment_types: string array (any)
        end_use: string array (any)
        space_type: string array (any)
    """
    def filter_by_daterange(self, building_id, date_from, date_to, consumption='energy', 
                            location=[], equipment_types=[], end_use=[], space_type=[]):
        payload = {
            "building_id": building_id,
            "consumption": consumption,
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        if len(location) != 0:
            data.update({ "location" : location })
        
        if len(equipment_types) != 0:
            data.update({ "equipment_types" : equipment_types })

        if len(end_use) != 0:
            data.update({ "end_use" : end_use })
        
        if len(space_type) != 0:
            data.update({ "space_type" : space_type })

        # response = requests.request("POST", constapis.BASE_URL + constapis.FILTER_BY_DATERANGE,
        #                     params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.FILTER_BY_DATERANGE, 
                                     timeout=30, params=payload, json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()      
        
    """
    @param
        equipment_id: string (any)
        building_id: string (any)
        date_from: string (yyyy-mm-dd)
        date_to: string (yyyy-mm-dd)
        detailed: boolean (Ture/False)
        consumption: string (energy/power)
        aggregate: string (day/hour/minute/month)
        aggregation_type: string (avg/sum)
        minute: string (1~)
        divisible_by: string (1000/1000000)
    """
    def equipment_chart(self, equipment_id, building_id, date_from, date_to, detailed=False, 
                        consumption="energy", aggregate="day", aggregation_type="sum", minute="1", divisible_by="",):
        payload = {
            "equipment_id": equipment_id,
            "building_id": building_id,
            "detailed": detailed,
            "consumption": consumption,
            "aggregation_type": aggregation_type,
            "minute": minute
        }

        if aggregate != "":
            payload.update({"aggregate": aggregate})

        if divisible_by != "":
            payload.update({"divisible_by": divisible_by})

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        # response = requests.request("POST", constapis.BASE_URL + constapis.EQUIPMENT_CHART,
        #                     params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.EQUIPMENT_CHART, 
                                     timeout=30, params=payload, json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        
    """
    @param
        equipment_id: string (any)
        building_id: string (any)
        date_from: string (yyyy-mm-dd)
        date_to: string (yyyy-mm-dd)
        consumption: string (energy/power)
    """
    def equipment_ytd_usage(self, equipment_id, building_id, date_from, date_to, consumption="energy"):
        payload = {
            "equipment_id": equipment_id,
            "building_id": building_id,
            "consumption": consumption,
        }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        # response = requests.request("POST", constapis.BASE_URL + constapis.EQUIPMENT_YTD_USAGE,
        #                     params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.EQUIPMENT_YTD_USAGE, 
                                     timeout=30, params=payload, json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    def overall_building_energy_consumption(self, date_from, date_to):
        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        # response = requests.request("POST", constapis.BASE_URL + constapis.GET_OVERALL_BUILDING, 
        #                             data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.GET_OVERALL_BUILDING, 
                                     timeout=30, json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        
    def overall_building_power_consumption_by_end_uses_category(self, building_id, off_hours, date_from, date_to):
        if( off_hours == None ):
            payload = {
                "building_id": building_id
            }
        else:
            payload = {
                "off_hours": off_hours,
                "building_id": building_id
            }

        data = {
            "date_from": date_from,
            "date_to": date_to,
            "tz_info": "US/Eastern",
        }

        # response = requests.request("POST", constapis.BASE_URL + constapis.GET_END_USE_CATEGORY,
        #                     params=payload, data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.post(constapis.BASE_URL + constapis.GET_END_USE_CATEGORY, 
                                     timeout=30, json=data, params=payload, headers=self.ConstAPIClass.getHeader())
        
        if response.status_code!= 200:
            return response.status_code
        else:
            return response.json()
        

