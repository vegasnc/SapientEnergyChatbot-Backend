from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session

import openai
import os
import json
import datetime
import requests
import apis.constapis as constapi
import apis.userapi as userapi
import apis.explorer_chart as explorer_chart

class IngestDataClass:
    UserAPIClass = None
    ExplorerChartClass = None
    ConstAPIClass = None
    DATE_FROM = "1900-01-01"
    DATE_NOW = datetime.datetime.now().strftime("%Y-%m-%d")
    session = Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    def __init__(self) -> None:
        load_dotenv()
        openai.api_key=os.getenv("OPENAI_API_KEY")
        
        # login for ingesting
        self.UserAPIClass = userapi.UserAPI()
        self.ConstAPIClass = constapi.APIClass()
        # response = self.UserAPIClass.signin(os.getenv("LOGIN_USER_NAME"), os.getenv("LOGIN_PASSWORD"))
        # user_token = response["data"]["token"]
        # constapi.USER_TOKEN = user_token

        # init explorer chart class
        self.ExplorerChartClass = explorer_chart.ExplorerClass()

    # Get readable content using OpenAI chat completion
    def get_readable(self, data):
        text = "\n".join([f"{item['key']}: {json.dumps(item['value'])}" for item in data])
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system", 
                    "content": text
                },
                {
                    "role": "user", 
                    "content": 'Please provide a human readable version of this data. Should be understandable to 18 year old, and include all of the data. No warnings, no other text shold be present in your answer.'
                },],
        )
        
        if response and response.choices:
            assistant_reply = response.choices[0].message["content"]
            return assistant_reply
        else:
            return "Error"

    # Flatten json data to 1 depth json data
    def flatten_json(self, data, parent_key='', sep='_'):
        items = {}
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(self.flatten_json(value, new_key, sep))
            else:
                items[new_key] = value
        return items

    # Re-format the json data
    def process_data(self, raw_data):
        result_data = []
        raw_data = self.flatten_json(raw_data)
        for key, value in raw_data.items():
            item = {"key": key.replace('_', ' ').capitalize(), "value": value}
            result_data.append(item)
        return result_data
    
    # Re-format the json array data
    def process_array_data(self, list_raw_data):
        result_data = []
        for item in list_raw_data:
            raw_data = self.flatten_json(item)
            for key, value in raw_data.items():
                t_item = {"key": key.replace('_', ' ').capitalize(), "value": value}
                result_data.append(t_item)
        print(result_data)
        return result_data

    
    # Merge two json data without repeat keys
    def merge_json_data(self, source1, source2):
        merged_data = source1.copy()

        for key, value in source2.items():
            if key not in merged_data:
                merged_data[key] = value
        
        return merged_data
    
    def get_building_data(self):
        response = self.ExplorerChartClass.get_building(False)
        return response
    
    def get_equipment_list(self):
        #  -------------------------------- Explorer Chart API --------------------------------
        final_data = []
        # Get building data
        response = self.ExplorerChartClass.get_building(False)

        # Get building total energy consumption data
        for building in response:
            building_id = building["building_id"]
            # Get equipment data
            equipment_list = self.ExplorerChartClass.get_equipment_list(building_id, str(self.DATE_FROM), str(self.DATE_NOW))

            final_data.extend(equipment_list["data"])
            
        return final_data
    
    def get_equipment_type(self):
        result = []
        # response = requests.request("GET", constapi.BASE_URL + constapi.GET_EQUIPMENT_TYPE,
        #                     headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.get(constapi.BASE_URL + constapi.GET_EQUIPMENT_TYPE, 
                                     timeout=30, headers=self.ConstAPIClass.getHeader())
        if response.status_code == 200:
            data = response.json()
            for item in data["data"]:
                if item["equipment_count"] != 0:
                    result.append(item)
            return result
        else:
            return None
        
    def get_end_use(self):
        # response = requests.request("GET", constapi.BASE_URL + constapi.GET_END_USE,
        #             headers=self.ConstAPIClass.getHeader(), timeout=600)
        response = self.session.get(constapi.BASE_URL + constapi.GET_END_USE, 
                                     timeout=30, headers=self.ConstAPIClass.getHeader())
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

