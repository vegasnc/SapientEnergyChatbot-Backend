import os
from dotenv import load_dotenv
load_dotenv()

global USER_TOKEN
USER_TOKEN = ""

class APIClass:
    def getToken(self):
        return USER_TOKEN
    
    def setToken(self, token):
        USER_TOKEN = token

    def getHeader(self):

        print(f"User Token = {USER_TOKEN}")

        if( USER_TOKEN == "" ):
            return {
                'Content-type': 'application/json',
                'Cache-Control': 'no-cache',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        else:
            return {
                'Content-type': 'application/json',
                'Authorization' : 'Bearer ' + USER_TOKEN,
                'Cache-Control': 'no-cache',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }


BASE_URL = os.getenv('API_BASE')

# user api
SIGNUP='/api/user_role/user/signup'
SIGNIN='/api/user_role/user/signin'
CHECK_TOKEN='/api/user_role/user/check-token-validity'

# user permission
GET_USER_PERMISSIONS='/api/user_role/user-permission-role/user-permissions'

# explorer chart
FILTER_BY_DATERANGE='/api/explorer/filter_by_daterange'
BUILDING_LIST='/api/explorer/building_list'
GET_BUILDING='/api/config/get_buildings'
GET_EQUIPMENT_LIST='/api/explorer/equipment_list'
EQUIPMENT_CHART='/api/explorer/equipment_chart'
EQUIPMENT_YTD_USAGE='/api/explorer/equipment_ytd_usage'

# chart & graph
GET_CHART_DATA = '/api/energy/chart'

# config
CONFIG_METADATA='/api/config/metadata'
GET_EQUIPMENT_TYPE = '/api/config/get_equipment_type'

#Time of day
GET_HOURLY_DATA='/api/energy/time_of_day/hourly'

# Portfolio
GET_OVERALL_BUILDING = "/api/energy/portfolio/overall"
GET_END_USE_CATEGORY = "/api/energy/portfolio/end-uses-info"

#Building Overview
GET_ENERGY_BUILDING_EQUIPMENT = "/api/energy/building/equipment"
GET_ENERGY_ENDUSE_LOAD_USAGE = "/api/energy/end_use/load_usage"

# Helper APIs
GET_END_USE = "/api/config/get_end_use"
