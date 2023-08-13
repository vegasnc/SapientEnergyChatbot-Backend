from dotenv import load_dotenv
import openai
import os
import json
import datetime
import apis.constapis as constapi
import apis.userapi as userapi
import apis.explorer_chart as explorer_chart

class IngestDataClass:
    UserAPIClass = None
    ExplorerChartClass = None
    DATE_FROM = "1900-01-01"
    DATE_NOW = datetime.datetime.now().strftime("%Y-%m-%d")

    def __init__(self) -> None:
        load_dotenv()
        openai.api_key=os.getenv("OPENAI_API_KEY")
        
        # login for ingesting
        self.UserAPIClass = userapi.UserAPI()
        response = self.UserAPIClass.signin(os.getenv("LOGIN_USER_NAME"), os.getenv("LOGIN_PASSWORD"))
        user_token = response["data"]["token"]
        constapi.USER_TOKEN = user_token

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
    
    def ingest_data(self):
        #  -------------------------------- Explorer Chart API --------------------------------
        final_data = []
        # Get building data
        response = self.ExplorerChartClass.get_building(False)

        # Get building total energy consumption data
        for building in response:
            building_name = building["building_name"]
            building_id = building["building_id"]

            # Get building full json data
            total_energy_consumption = self.ExplorerChartClass.get_building_list(str(self.DATE_FROM), str(self.DATE_NOW), building_name)
            building_data = building.copy()
            if len(total_energy_consumption) != 0:
                building_data = self.merge_json_data(building, total_energy_consumption[0])
            
            # Get processed building data
            building_data = self.process_data(building_data)

            # Get equipment data
            equipment_list = self.ExplorerChartClass.get_equipment_list(building_id, str(self.DATE_FROM), str(self.DATE_NOW))
            
            equipment_data = []
            for item in equipment_list["data"]:
                equipment_data.append(self.process_data(item))
                
            print("\n------------------------------ total energy consumption -------------------------------\n")
            print(f"{equipment_data}")

            final_data.append(
                [
                    {
                        "key": "building",
                        "value": building_data,
                        "readable": self.get_readable(building_data)
                    },
                    {
                        "key": "equipment",
                        "value": equipment_data
                    }
                ]
            )
            # final_data.append(self.process_data(building))

        # Specify the filename
        filename = "data.json"
        with open(filename, "w") as json_file:
            json.dump(final_data, json_file, indent=4)
        print(f"JSON data has been written to {filename}")

        # print("\n------------------------------ Final -------------------------------\n")
        # print(f"{final_data}")

# for building in response:
#     for key, value in building.items():
#         print(f"{key}, {value}")
#     print("------")

# response = ExplorerChartClass.get_building_list("", "power", "consumption", "dce", 
#                                                 "2022-01-01", "2023-12-31", [""])
# response = ExplorerChartClass.get_building(True)
# response[0]["building_id"]
# response = ExplorerChartClass.equipment_ytd_usage("63920fbadc085066bf9781dc", "6357ffd71ce19dc07713433a", "2022-01-01", "2023-12-31")
# print(response)
# -------------------------------------------------------------------------------------
