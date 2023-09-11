from rake_nltk import Rake
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from dotenv import dotenv_values
import re
import json
import openai
from models import relevant_api # call model file
import engine.keyword_extract as keyword_extract
import ingest.equip_power_consumption as equipment_power_consumption
import ingest.ingest as ingest

# load and init OpenAI
env_vars = dotenv_values('.env')
openai.api_key=env_vars["OPENAI_API_KEY"]

relevant_model = relevant_api.RelevantAPI()
IngestClass = ingest.IngestDataClass()
EquipmentPowerConsumption = equipment_power_consumption.EquipPowerConsumption()

notDetectedResponseList = [
    "This question is about non-energy consummption.",
    "This question is about general business."
]

notDetectedSystemMSGList = [
    "You are an Energy Chatbot working to help facilitate energy data and information to help companies become more efficiency with energy use. User has asked a question which you can not answer with contentaul data. If the question is related to energy, business or equipment attempt to answer. If not, suggest asking a question about the platform or energy data.",
    "You are an Energy Chatbot working to help facilitate energy data and information to help companies become more efficiency with energy use. User has asked a question which you can not answer with contentaul data. If the question is related to energy, business or equipment attempt to answer. If not, suggest asking a question about the platform or energy data."
]

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
        index = get_best_response(question, notDetectedResponseList)
        system_msg = notDetectedSystemMSGList[index]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": system_msg
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        if response and response.choices:
            assistant_reply = response.choices[0].message["content"]
            result = {
                "answer": assistant_reply,
                "api": []
            }
            return result
        else:
            return None
    else:
        # ------------ Generate Answer Using ChatGPT ------------
        system_msg = result["system_message"]
        relevant_arr = result["relevant"]
        api_arr = []
        result = []

        for relevant in relevant_arr:
            result = relevant_model.find_one({"response": relevant})
            if result != None:
                api_arr.append({
                    "response" : relevant,
                    "api" : result["api"]
                })

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system", 
                    "content": system_msg
                },
                {
                    "role": "user", 
                    "content": question
                },
            ],
        )

        if response and response.choices:
            assistant_reply = response.choices[0].message["content"]
            result = {
                    "answer" : assistant_reply,
                    "api" : api_arr
                }
            return result
        else:
            return None
        
    return None

def get_api_answer(api, question):
    
    # ------------------- Matching api ---------------------
    # What is the average power consumption of our equipment?
    if api == "get_avg_power_consumption":
        res = EquipmentPowerConsumption.get_avg_power_consumption(question)

        if res:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Which equipment consumes the most power on a regular basis?
    elif api == "get_most_consumption_equipment":
        res = EquipmentPowerConsumption.get_most_consumption_equipment(question)

        if res != 404 and len(res) != 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Are there any specific time periods where power consumption is significantly higher?
    elif api == "get_period_higher_consumption":
        res = EquipmentPowerConsumption.get_period_higher_consumption(question)

        if res != 404:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # How do different equipment models and brands vary in terms of power consumption?
    elif api == "get_average_by_category_type":
        res = EquipmentPowerConsumption.get_average_by_category_type(question)

        if res != 404:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Which equipment has shown the most improvement in power efficiency over time?
    elif api == "get_most_improvement_equipment":
        res = EquipmentPowerConsumption.get_most_improvement_equipment(question)

        if res != 404 and res != None:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Are there any seasonal trends noticeable in equipment power consumption?
    elif api == "get_seasonal_trends_power_consumption":
        res = EquipmentPowerConsumption.get_seasonal_trends_power_consumption(question)

        if res != 404 and res != None:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Have there been any instances where sudden spikes in power consumption occurred?
    elif api == "get_spike_power_consumption":
        res = EquipmentPowerConsumption.get_spike_power_consumption(question)

        if res != 404 and res != None:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Is there any noticeable difference in power consumption between weekdays and weekends?
    elif api == "get_power_consumption_weekdays_weekend":
        res = EquipmentPowerConsumption.get_power_consumption_weekdays_weekend(question)

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
    
    # How does power consumption vary between different equipment brand within our organization?
    elif api == "get_power_consumption_between_equip_type":
        res = EquipmentPowerConsumption.get_power_consumption_between_equip_type(question)

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Does power consumption vary during different time periods of the day or night?
    elif api == "get_power_consumption_day_night":
        res = EquipmentPowerConsumption.get_power_consumption_day_night(question)

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    # Have any of the equipment undergone a sudden increase in power consumption?
    elif api == "get_equipment_sudden_increase_consumption":
        res = EquipmentPowerConsumption.get_equipment_sudden_increase_consumption(question)

        print(res)

        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None

    # The question is not sure for now, 
    elif api == "get_building_energy_consumption_overall":
        res = EquipmentPowerConsumption.get_building_energy_consumption_overall(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_building_energy_consumption_by_end_uses_category":
        res = EquipmentPowerConsumption.get_building_energy_consumption_by_end_uses_category(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_energy_building_equipment":
        res = EquipmentPowerConsumption.get_energy_building_equipment(question)
        
        if res != 404 and res!= False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_explorer_equip_power_consumption":
        res = EquipmentPowerConsumption.get_explorer_equip_power_consumption(question)
        
        if res != 404 and res!= False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_hvac_end_use_category_energy_consumption":
        res = EquipmentPowerConsumption.get_hvac_end_use_category_energy_consumption(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_plug_end_use_category_energy_consumption":
        res = EquipmentPowerConsumption.get_plug_end_use_category_energy_consumption(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_process_end_use_category_energy_consumption":
        res = EquipmentPowerConsumption.get_process_end_use_category_energy_consumption(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_lighting_end_use_category_energy_consumption":
        res = EquipmentPowerConsumption.get_lighting_end_use_category_energy_consumption(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None
        
    elif api == "get_other_end_use_category_energy_consumption":
        res = EquipmentPowerConsumption.get_other_end_use_category_energy_consumption(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            return answer
        else:
            return None

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
                "content": 'Please provide a human readable sentence of this data. Should be understandable to 18 year old, and include almost of the data. No warnings, no other text shold be present in your answer. Now the power and energy unit are all w. But please convert to kWh.'
            },
        ],
    )
        
    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]
        return assistant_reply
    else:
        return "Error"

# Function to get the best response and its index
def get_best_response(question, response_list):
    # Initialize variables to store the best response and its index
    best_response_index = -1
    best_response_score = -1.0  # Initialize with a low score

    for i, response in enumerate(response_list):
        # Generate a response from GPT-3 for the given question and response
        # prompt = f"the myQuestion is : '{question}' \n the myAnswer is : {response}.\n please score from 0 to 100 how much the myAnswer is the correct answer of the myQuestion.\n  your response must be like : Score = score "
        prompt = f"the myQuestion is : '{question}' \n the myCategory is : {response}.\n please score from 0 to 100 how much the myQuestion is in myCategory.\n  your response must be like : Score = score "
        completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.9,
            max_tokens=256
        )
        score = re.findall(r'\d+' , completion.choices[0].text.strip())
        if len(score):
            try:
                score = int(score[0])
                if score > best_response_score:
                    best_response_score = score
                    best_response = response
                    best_response_index = i
            except:
                pass
    return best_response_index