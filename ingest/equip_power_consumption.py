from flask import Flask
import requests
import apis.constapis as constapis
import apis.explorer_chart as explorer_chart
import apis.chart_graph as chart_graph
from datetime import datetime, timedelta
import numpy as np

class EquipPowerConsumption:

    ExplorerClass = None
    ChartClass = None
    DATE_FROM = "2022-05-01"
    DATE_NOW = datetime.now().strftime("%Y-%m-%d")
    DATE_BEFORE_ONE_WEEK = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

    def __init__(self) -> None:
        self.ExplorerClass = explorer_chart.ExplorerClass()
        self.ChartClass = chart_graph.ChatGraph()

    # Get all equipment information including power consumption
    def get_equip_power_consumption(self, date_from=DATE_FROM):
        building_list = self.ExplorerClass.get_building()

        if building_list != 404:
            equip_list = []

            for building in building_list:
                equip_list.extend(self.ExplorerClass.get_equipment_list(building["building_id"], date_from, self.DATE_NOW)["data"])

            return equip_list
        else:
            return 404

    # What is the average power consumption of our equipment?
    def get_avg_power_consumption(self):
        equip_list = self.get_equip_power_consumption()
        conp = []

        if equip_list != 404:
            for item in equip_list:
                conp.append(item["consumption"]["now"])

            return {
                    "key" : "average_consumption",
                    "value" : np.mean(conp)
                }
        else:
            return False
        
    # Which equipment consumes the most power on a regular basis?
    def get_most_consumption_equipment(self):
        building_list = self.ExplorerClass.get_building()

        if building_list != 404:
            equip_list = []
            top_equip = {}
            old_ytd = 0

            # Get equipment from building id
            for building in building_list:
                equip_list.append([building["building_id"], self.ExplorerClass.get_equipment_list(building["building_id"], self.DATE_FROM, self.DATE_NOW)["data"]])

            # Get YTD of equipment from equipment id
            for item in equip_list:
                building_id = item[0]
                equip = item[1]

                if len(equip) > 0:
                    temp = self.ExplorerClass.equipment_ytd_usage(equip[0]["equipment_id"], building_id, self.DATE_FROM, self.DATE_NOW)

                    if "data" in temp:
                        ytd = temp["data"][0]["ytd"]["ytd"]

                        if( ytd > old_ytd ):
                            old_ytd = ytd
                            equip.extend(temp["data"][0])
                            top_equip = equip[0]

            return top_equip
        else:
            return 404

    def get_y_key(self, x) :
        if x["y"] == "":
            return 0
        return x["y"]

    # Are there any specific time periods where power consumption is significantly higher?
    def get_period_higher_consumption(self):
        chart_data = self.ChartClass.getChartData(self.DATE_FROM, self.DATE_NOW)
        if chart_data != 404 and len(chart_data) > 0:
            chart_data.sort(key = self.get_y_key , reverse=True)
            period = chart_data[0]["x"]
            return {
                "key" : "specific time periods where power consumption is significantly higher",
                "value" : period
            }
        else:
            return 404

    # How do different equipment models and brands vary in terms of power consumption?
    def get_average_by_category_type(self):
        # Get all equipment power consumption
        equip_list = self.get_equip_power_consumption()
        
        if equip_list != 404:
            # Create a dictionary to store the sum and count of consumption values
            consumption_data = {}

            for item in equip_list:
                equipment_type = item['equipments_type']
                if equipment_type is not None:
                    consumption_now = item['consumption']['now']
                    if equipment_type in consumption_data:
                        consumption_data[equipment_type]['sum'] += consumption_now
                        consumption_data[equipment_type]['count'] += 1
                    else:
                        consumption_data[equipment_type] = {'sum': consumption_now, 'count': 1}

            # Calculate average consumption for each equipment type
            average_consumptions = {}
            for equipment_type, values in consumption_data.items():
                average_consumptions[equipment_type] = values['sum'] / values['count']

            return average_consumptions
        else:
            return 404

    # Which equipment has shown the most improvement in power efficiency over time?
    def get_most_improvement_equipment(self):
        # Get all equipment power consumption
        equip_list = self.get_equip_power_consumption(self.DATE_BEFORE_ONE_WEEK)

        old_temp_change = 0

        if equip_list != 404:
            # result array
            result_obj = []

            if equip_list != 404 and len(equip_list) > 0:
                equip_list.sort(key = lambda x: x["consumption"]["change"] , reverse=True)
            
            for item in equip_list:
                if item["consumption"]["change"] < 0 and len(result_obj) < 3: #  and old_temp_change > item["consumption"]["change"]
                    old_temp_change = item["consumption"]["change"]
                    result_obj.append(item)
            if result_obj != None:
                return result_obj
            else:
                return {
                    "answer" : "No equipment has yet improved power efficiency over time."
                }
        else:
            return 404