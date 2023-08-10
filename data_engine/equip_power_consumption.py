from flask import Flask
import requests
import apis.constapis as constapis
import apis.explorer_chart as explorer_chart
import datetime
import numpy

class EquipPowerConsumption:

    ExplorerClass = None
    DATE_FROM = "1900-01-01"
    DATE_NOW = datetime.datetime.now().strftime("%Y-%m-%d")

    def __init__(self) -> None:
        self.ExplorerClass = explorer_chart.ExplorerClass()

    # Get all equipment information including power consumption
    def get_equip_power_consumption(self):
        building_list = self.ExplorerClass.get_building()
        if building_list != 404:
            equip_list = []
            for building in building_list:
                equip_list.extend(self.ExplorerClass.get_equipment_list(building["building_id"], self.DATE_FROM, self.DATE_NOW)["data"])

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
            return numpy.mean(conp)
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
                            top_equip = equip
            return top_equip
        else:
            return 404
    # Are there any specific time periods where power consumption is significantly higher?
    def get_period_higher_consumption(self):
        
        pass