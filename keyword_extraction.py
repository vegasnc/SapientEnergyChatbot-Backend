from rake_nltk import Rake
import pandas as pd
from pymongo import MongoClient
import data_engine.equip_power_consumption as equipment_power_consumption

class KeywordExtraction:
    mongo_client = None
    db = None
    collection = None

    EquipPowerConsumption = None

    def __init__(self) -> None:
        # Connect with mongodb
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo_client["sapient"]
        self.collection = self.db["keyword_intent"]    
        self.EquipPowerConsumption = equipment_power_consumption.EquipPowerConsumption()

    def extraction(self):
        # Read the .xlsx file
        question_data = pd.read_excel('quiz.xlsx')

        # Get the column names
        column_names = question_data.columns.to_list()

        # Access the content
        question_column = question_data['Question']
        intent_column = question_data['Intent']

        # Init Rake
        rake_mltk_var = Rake()
        keyword_list = []

        for index in range(len(question_column)):
            rake_mltk_var.extract_keywords_from_text(question_column[index])
            rankedList = rake_mltk_var.get_ranked_phrases()[:10]
            keyword_list.append(
                {
                    "keywords": rankedList,
                    "intents": intent_column[index]
                }
            )

        for item in keyword_list:
            # keyword_item = item["keywords"]
            # intent = item["intents"]
            self.collection.insert_one(item)

        print("Done!")

    def matchingAPI(self, keywords):
        result = self.collection.find_one({"keywords": {"$all" : keywords}})
        if result["intents"] == "Understand equipment power consumption":
            self.EquipPowerConsumption.get_most_consumption_equipment()
        print("-------------------------------")