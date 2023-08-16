from rake_nltk import Rake
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from dotenv import dotenv_values
import json
import openai
import engine.keyword_extract as keyword_extract
import ingest.equip_power_consumption as equipment_power_consumption
import ingest.ingest as ingest

# load and init OpenAI
env_vars = dotenv_values('.env')
openai.api_key=env_vars["OPENAI_API_KEY"]

IngestClass = ingest.IngestDataClass()
EquipmentPowerConsumption = equipment_power_consumption.EquipPowerConsumption()

# Get top ratio object
def get_top_ratio_item(documents, keyword_arr):
    t_ratio = 0
    res_obj = None

    # Make a sentence from keyword arr
    c_sentence = ""
    for item in keyword_arr:
        c_sentence += item + " "

    # Make a sentence and get top ratio object
    for item in documents:

        #  Make a sentence from origin keyword arr
        o_sentence = ""
        for word in item["keywords"]:
            o_sentence += word + " "
        
        # Get token sort ratio with origin sentence and current sentence
        ratio = fuzz.token_sort_ratio(o_sentence, c_sentence)
        if ratio >= 75 and t_ratio < ratio:
            t_ratio = ratio
            res_obj = item
    return res_obj

# Generate answer from question
def get_answer(question, collection):

    # Extract keyword for searching API
    keyword_arr = keyword_extract.keyword_extration(question)
    result = collection.find({"keywords": {"$in" : keyword_arr}})

    result = get_top_ratio_item(result, keyword_arr)
    
    # If the search result is not exist
    if result == None:
        return None
    
    # ------------------- Matching api ---------------------
    # What is the average power consumption of our equipment?
    elif result["api"] == "get_avg_power_consumption":
        res = EquipmentPowerConsumption.get_avg_power_consumption()

        if res:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Which equipment consumes the most power on a regular basis?
    elif result["api"] == "get_most_consumption_equipment":
        res = EquipmentPowerConsumption.get_most_consumption_equipment()

        if res != 404 and len(res) != 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Are there any specific time periods where power consumption is significantly higher?
    elif result["api"] == "get_period_higher_consumption":
        res = EquipmentPowerConsumption.get_period_higher_consumption()

        if res != 404:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # How do different equipment models and brands vary in terms of power consumption?
    elif result["api"] == "get_average_by_category_type":
        res = EquipmentPowerConsumption.get_average_by_category_type()

        if res != 404:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Which equipment has shown the most improvement in power efficiency over time?
    elif result["api"] == "get_most_improvement_equipment":
        res = EquipmentPowerConsumption.get_most_improvement_equipment()

        if res != 404 and res != None:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Are there any seasonal trends noticeable in equipment power consumption?
    elif result["api"] == "get_seasonal_trends_power_consumption":
        res = EquipmentPowerConsumption.get_seasonal_trends_power_consumption()

        if res != 404 and res != None:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Have there been any instances where sudden spikes in power consumption occurred?
    elif result["api"] == "get_spike_power_consumption":
        res = EquipmentPowerConsumption.get_spike_power_consumption()

        if res != 404 and res != None:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Is there any noticeable difference in power consumption between weekdays and weekends?
    elif result["api"] == "get_power_consumption_weekdays_weekend":
        res = EquipmentPowerConsumption.get_power_consumption_weekdays_weekend()

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
    
    # How does power consumption vary between different equipment brand within our organization?
    elif result["api"] == "get_power_consumption_between_equip_type":
        res = EquipmentPowerConsumption.get_power_consumption_between_equip_type()

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Does power consumption vary during different time periods of the day or night?
    elif result["api"] == "get_power_consumption_day_night":
        res = EquipmentPowerConsumption.get_power_consumption_day_night()

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Have any of the equipment undergone a sudden increase in power consumption?
    elif result["api"] == "get_equipment_sudden_increase_consumption":
        res = EquipmentPowerConsumption.get_equipment_sudden_increase_consumption()

        print(res)

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Is there any equipment showing increased energy usage during non-business periods?
    # elif result["api"] == "get_euqipment_increased_consumption_nonbusiness":
    #     res = EquipmentPowerConsumption.get_euqipment_increased_consumption_nonbusiness()

    #     print(res)

    #     if res != 404 and len(res) > 0:
    #         answer = generate_answer_from_openai(res)
    #         return answer
    #     else:
    #         return None
        
    return None

# Generate answer from data using OpenAI text completion
def generate_answer_from_openai(data):
    if type(data) is list:
        data = IngestClass.process_array_data(data)
    else:
        data = IngestClass.process_data(data)

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
                "content": 'Please provide a human readable sentence of this data. Should be understandable to 18 year old, and include almost of the data. No warnings, no other text shold be present in your answer.'
            },
        ],
    )
        
    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]
        return assistant_reply
    else:
        return "Error"
