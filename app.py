# demo/__init__.py
from flask import Flask 
from dotenv import load_dotenv
import requests
import os
import apis.constapis as constapi
import apis.userapi as userapi
import apis.explorer_chart as explorer_chart


app = Flask(__name__)

# ------------------------------------- User API -------------------------------------
UserAPIClass = userapi.UserAPI()
response = UserAPIClass.signin("michael@kneeshaw.dev", "2R*k&wqiUf.)&LWy<eux")
user_token = response["data"]["token"]
constapi.USER_TOKEN = user_token

response = UserAPIClass.get_user_permissions()
# -------------------------------------------------------------------------------------

#  -------------------------------- Explorer Chart API --------------------------------
ExplorerChartClass = explorer_chart.ExplorerClass()
# response = ExplorerChartClass.get_building_list("", "power", "consumption", "dce", 
#                                                 "2022-01-01", "2023-12-31", [""])
response = ExplorerChartClass.get_building(True)
# response[0]["building_id"]
response = ExplorerChartClass.equipment_ytd_usage("63920fbadc085066bf9781dc", "6357ffd71ce19dc07713433a", "2022-01-01", "2023-12-31")
print(response)
# -------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)   
