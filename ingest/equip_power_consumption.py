from flask import Flask
import requests
import apis.constapis as constapis
import apis.explorer_chart as explorer_chart
import apis.chart_graph as chart_graph
import apis.building_overview as building_overview
import apis.end_uses as end_uses
from datetime import datetime, timedelta
import numpy as np
import ingest.utils as utils

class EquipPowerConsumption:

    ExplorerClass = None
    BuildingOverviewClass = None
    ChartClass = None
    EndUsesClass = None
    DATE_FROM = "2022-05-01"
    DATE_NOW = datetime.now().strftime("%Y-%m-%d")

    def __init__(self) -> None:
        self.ExplorerClass = explorer_chart.ExplorerClass()
        self.ChartClass = chart_graph.ChatGraph()
        self.BuildingOverviewClass = building_overview.BuildingOverviewClass()
        self.EndUsesClass = end_uses.EndUsesClass()

    def setDate(self, stDate, enDate):
        self.DATE_FROM = stDate
        self.DATE_NOW = enDate
        
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
    def get_avg_power_consumption(self, question):
        equip_list = self.get_equip_power_consumption()
        conp = []

        if equip_list != 404:
            for item in equip_list:
                conp.append(item["consumption"]["now"])

            return {
                    "question" : question,
                    "answer" : np.mean(conp)
                }
        else:
            return False
        
    # Which equipment consumes the most power on a regular basis?
    def get_most_consumption_equipment(self, question, building_id, type_id):
        equip_list = []
        top_equip = {}
        old_ytd = 0

        equip_list.append([building_id, self.ExplorerClass.get_equipment_list(building_id, self.DATE_FROM, self.DATE_NOW)["data"]])

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

        return {
            "question" : question,
            "answer" : top_equip
        }

    def get_y_key(self, x) :
        if x["y"] == "":
            return 0
        return x["y"]

    # Are there any specific time periods where power consumption is significantly higher?
    def get_period_higher_consumption(self, question):
        chart_data = self.ChartClass.get_chart_data(self.DATE_FROM, self.DATE_NOW)
        if chart_data != 404 and len(chart_data) > 0:
            chart_data.sort(key = self.get_y_key , reverse=True)
            period = chart_data[0]["x"]
            return {
                "question" : question,
                "answer" : period
            }
        else:
            return 404

    # How do different equipment models and brands vary in terms of power consumption?
    def get_average_by_category_type(self, question):
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

            return {
                "question": question,
                "answer" : average_consumptions
            }
        else:
            return 404

    # Which equipment has shown the most improvement in power efficiency over time?
    def get_most_improvement_equipment(self, question):
        # Get all equipment power consumption
        equip_list = self.get_equip_power_consumption(self.DATE_FROM)

        if equip_list != 404:
            # result array
            result_obj = []

            if equip_list != 404 and len(equip_list) > 0:
                equip_list.sort(key = lambda x: x["consumption"]["change"] , reverse=True)
            
            for item in equip_list:
                if item["consumption"]["change"] < 0 and len(result_obj) < 3:
                    result_obj.append(item)

            if result_obj != None:
                return {
                    "question": question,
                    "answer" : result_obj
                }
            else:
                return {
                    "question": question,
                    "answer" : "No equipment has yet improved power efficiency over time."
                }
        else:
            return 404
        
    # Are there any seasonal trends noticeable in equipment power consumption?
    def get_seasonal_trends_power_consumption(self, question)  :
        chart_data = self.ChartClass.get_chart_data(self.DATE_FROM, self.DATE_NOW)

        if chart_data != 404 and len(chart_data) > 0:
            season_cunsumption = utils.get_season_average_consumption(chart_data)
            
            return {
                "question": question,
                "answer" : season_cunsumption,
                "unit" : "Wh"
            }
        else:
            return 404
        
    # Have there been any instances where sudden spikes in power consumption occurred?
    def get_spike_power_consumption(self, question):
        chart_data = self.ChartClass.get_chart_data(self.DATE_FROM, self.DATE_NOW)

        if chart_data != 404 and len(chart_data) > 0:
            offset = 0
            old_y_value = 0
            x_result = None

            for item in chart_data:
                y_value = item["y"]
                if y_value == "":
                    y_value = 0

                # if the old and now offset is big than history offset, update the offset and save the item
                if offset < abs(y_value - old_y_value):
                    offset = abs(y_value - old_y_value)
                    x_result = {
                        "sudden_spikes_in_power_consumption_date" : item["x"],
                        "sudden_spikes_in_power_consumption_value": item["y"]
                    }

                old_y_value = y_value

            return {
                "question" : question,
                "answer" : x_result
            }
        else:
            return 404
    
    # Is there any noticeable difference in power consumption between weekdays and weekends?
    def get_power_consumption_weekdays_weekend(self, question, building_id, building_name, type_id):
        building_data = []

        # Get equipment from building id
        chart_data = self.ChartClass.get_hourly_data(self.DATE_FROM, self.DATE_NOW, building_id)

        # Get weekday and weekend consumption average
        weekdays_data = chart_data[0]["weekdays"]
        weekend_data = chart_data[0]["weekend"]

        weekday_arr = np.array([item["y"] if item["y"] != "" else 0 for item in weekdays_data])
        weekend_arr = np.array([item["y"] if item["y"] != "" else 0 for item in weekend_data])

        # Get weekday average and weekend average
        weekday_avg = np.mean(weekday_arr)
        weekend_avg = np.mean(weekend_arr)

        building_data.append({
            "building_name" : building_name,
            "weekday_average_power_consumption" : weekday_avg,
            "weekend_average_power_consumption" : weekend_avg,
        })

        return {
            "question" : question,
            "answer" : building_data
        }

    # How does power consumption vary between different equipment brand within our organization?
    def get_power_consumption_between_equip_type(self, question):
        # Get all equipment power consumption
        equip_list = self.get_equip_power_consumption()

        if equip_list != 404:
            # Create a dictionary to store total consumption and count for each equipment type
            consumption_by_type = {}

            # Process each data entry
            for entry in equip_list:
                equipment_type = entry["equipments_type"]
                consumption_value = entry["consumption"]["now"]
                
                if equipment_type not in consumption_by_type:
                    consumption_by_type[equipment_type] = {"total": 0, "count": 0}
                
                consumption_by_type[equipment_type]["total"] += consumption_value
                consumption_by_type[equipment_type]["count"] += 1

            # Calculate the average consumption for each equipment type
            average_consumption_by_type = {}
            for equipment_type, values in consumption_by_type.items():
                average_consumption = values["total"] / values["count"]
                average_consumption_by_type[equipment_type] = average_consumption

            return {
                "question" : question,
                "answer" : average_consumption_by_type,
                "unit" : "Wh"
            }
        else:
            return False
        
    # Does power consumption vary during different time periods of the day or night?
    def get_power_consumption_day_night(self, question):
        chart_data = self.ChartClass.get_chart_data(self.DATE_FROM, self.DATE_NOW, "hour")
        
        if chart_data != 404 and len(chart_data) > 0:
            
            day_start_hour = 6  # Assuming day starts at 6 AM
            day_end_hour = 18  # Assuming day ends at 6 PM

            day_values = []
            night_values = []

            for entry in chart_data:
                x = datetime.strptime(entry["x"], "%Y-%m-%dT%H:%M:%S%z")
                y_value = entry["y"]

                if y_value != "":
                    y_value = float(y_value)

                    if day_start_hour <= x.hour < day_end_hour:
                        day_values.append(entry["y"])
                    else:
                        night_values.append(entry["y"])

            average_day = sum(day_values) / len(day_values)
            average_night = sum(night_values) / len(night_values)

            return {
                "question" : question,
                "answer" : {
                    "average_day" : average_day,
                    "average_night" : average_night,
                },
                "unit" : "Wh"
            }
        else:
            return 404
        
    # Have any of the equipment undergone a sudden increase in power consumption?
    def get_equipment_sudden_increase_consumption(self, question):
        equip_list = self.get_equip_power_consumption(self.DATE_FROM)
        result = []

        if equip_list != 404:
            for item in equip_list:
                if item["consumption"]["change"] > 100:
                    result.append({
                        "equipment_name" : item["equipment_name"],
                        "consumption_old" : item["consumption"]["old"],
                        "consumption_now" : item["consumption"]["now"],
                        "consumption_unit" : "Wh",
                        "change_percentage" : item["consumption"]["change"]
                    })

            return {
                "question" : question,
                "answer" : result
            }
        else:
            return False
    
    # # Is there any equipment showing increased energy usage during non-business periods?
    # def get_euqipment_increased_consumption_nonbusiness(self):
    #     building_list = self.ExplorerClass.get_building()

    #     if building_list != 404:
    #         equip_list = []

    #         for building in building_list:
    #             equip_list = self.ExplorerClass.get_equipment_list(building["building_id"], self.DATE_BEFORE_ONE_MONTH, self.DATE_NOW)["data"]
                
    #             for equip_item in equip_list:
    #                 equip_chart = self.ExplorerClass.equipment_chart(equip_item["equipment_id"], building["building_id"], 
    #                                                                  self.DATE_BEFORE_ONE_MONTH, self.DATE_NOW)
    #                 print(equip_chart["data"])
    #                 # aggregate the weekday and weekend data

    #     # We can make the API but the speed is too slow, so if we make the api, may be can't use this

    # ???
    def get_building_energy_consumption_overall(self, question):
        building_consumption_overall = self.ExplorerClass.overall_building_energy_consumption(self.DATE_FROM, self.DATE_NOW)

        if building_consumption_overall != 404 and building_consumption_overall != 422:
            return {
                "question" : question,
                "answer" : building_consumption_overall,
                "unit" : "Wh"
            }
        else:
            return False
        
    def get_building_energy_consumption_by_end_uses_category(self, question, building_id, building_name, type_id):
        end_uses_category = []

        building_consumption = self.ExplorerClass.overall_building_power_consumption_by_end_uses_category(building_id, None, 
                                                                                                            self.DATE_FROM, self.DATE_NOW)

        if building_consumption != 404 and building_consumption != 422:
            end_uses_category.append({
                                    "building_name" : building_name,
                                    "end_uses_category" : building_consumption
                                })
        return {
            "question" : question,
            "answer" : end_uses_category,
            "unit" : "Wh"
        }
        
    def get_energy_building_equipment(self, question, building_id, building_name, type_id):
        equipment_consumption = []

        consumption = self.BuildingOverviewClass.energy_building_equipment_overview(building_id, 
                                                                                    self.DATE_FROM, self.DATE_NOW)
        
        if consumption!= 404 and consumption!= 422:
            equipment_consumption.append({
                                    "building_name" : building_name,
                                    "equipment_consumption" : consumption
                                })
                
        return {
            "question" : question,
            "answer" : equipment_consumption,
            "unit" : "Wh"
        }
        
    # Return top 5 pieces of equipment that contribute most to energy consumption of a specific end use category
    def get_explorer_equip_power_consumption(self, question, building_id, date_from=DATE_FROM):
        equip_list = []

        equip_list.extend(self.ExplorerClass.get_equipment_list(building_id, date_from, self.DATE_NOW)["data"])

        return {
            "question" : question,
            "answer" : equip_list
        }
        
    def get_hvac_end_use_category_energy_consumption(self, question):
        building_list = self.ExplorerClass.get_building()

        if building_list != 404:
            energy_consumption = []

            for building in building_list:
                energy_consumption.append({
                    "building_name" : building["building_name"],
                    "consumption_data" : self.EndUsesClass.energy_end_use_load_usage(building["building_id"], "HVAC",
                                                                                      self.DATE_FROM, self.DATE_NOW)["data"]
                })


            return {
                "question" : question,
                "answer" : energy_consumption
            }
        else:
            return 404
        
    def get_lighting_end_use_category_energy_consumption(self, question):
        building_list = self.ExplorerClass.get_building()

        if building_list != 404:
            energy_consumption = []

            for building in building_list:
                energy_consumption.extend({
                    "building_name" : building["building_name"],
                    "consumption_data" : self.EndUsesClass.energy_end_use_load_usage(building["building_id"], "Lighting",
                                                                                      self.DATE_FROM, self.DATE_NOW)["data"]
                })

            return {
                "question" : question,
                "answer" : energy_consumption
            }
        else:
            return 404
        
    def get_plug_end_use_category_energy_consumption(self, question):
        building_list = self.ExplorerClass.get_building()

        if building_list != 404:
            energy_consumption = []

            for building in building_list:
                energy_consumption.extend({
                    "building_name" : building["building_name"],
                    "consumption_data" : self.EndUsesClass.energy_end_use_load_usage(building["building_id"], "Plug",
                                                                                      self.DATE_FROM, self.DATE_NOW)["data"]
                })

            return {
                "question" : question,
                "answer" : energy_consumption
            }
        else:
            return 404
        
    def get_process_end_use_category_energy_consumption(self, question):
        building_list = self.ExplorerClass.get_building()

        if building_list != 404:
            energy_consumption = []

            for building in building_list:
                energy_consumption.extend({
                    "building_name" : building["building_name"],
                    "consumption_data" : self.EndUsesClass.energy_end_use_load_usage(building["building_id"], "Process",
                                                                                      self.DATE_FROM, self.DATE_NOW)["data"]
                })

            return {
                "question" : question,
                "answer" : energy_consumption
            }
        else:
            return 404
        
    def get_other_end_use_category_energy_consumption(self, question):
        building_list = self.ExplorerClass.get_building()

        if building_list != 404:
            energy_consumption = []

            for building in building_list:
                energy_consumption.extend({
                    "building_name" : building["building_name"],
                    "consumption_data" : self.EndUsesClass.energy_end_use_load_usage(building["building_id"], "Other",
                                                                                      self.DATE_FROM, self.DATE_NOW)["data"]
                })

            return {
                "question" : question,
                "answer" : energy_consumption
            }
        else:
            return 404
        