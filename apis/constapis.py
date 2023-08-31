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
        print(USER_TOKEN)
        if( USER_TOKEN == "" ):
            return {
                'Content-type': 'application/json'
            }
        else:
            return {
                'Content-type': 'application/json',
                'Authorization' : 'Bearer ' + USER_TOKEN
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

#Time of day
GET_HOURLY_DATA='/api/energy/time_of_day/hourly'

# Portfolio
GET_OVERALL_BUILDING = "/api/energy/portfolio/overall"
