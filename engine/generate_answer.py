from rake_nltk import Rake
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from dotenv import dotenv_values
from models import relevant_api # call model file

import re
import json
import openai
import engine.keyword_extract as keyword_extract
import ingest.equip_power_consumption as equipment_power_consumption
import ingest.ingest as ingest

# load and init OpenAI
env_vars = dotenv_values('.env')
openai.api_key=env_vars["OPENAI_API_KEY"]

relevant_model = relevant_api.RelevantAPI()
IngestClass = ingest.IngestDataClass()
EquipmentPowerConsumption = equipment_power_consumption.EquipPowerConsumption()

TEXT = "1"
TEXT_TABLE = "2"
TEXT_PIECHART = "3"
TEXT_BARCHART = "4"

notDetectedResponseList = [
    "This question is about non-energy consummption.",
    "This question is about general business.",
    "This sentence is about user greetings."
]

notDetectedSystemMSGList = [
    "Yes, this is a static test message 1.",
    "Yes, this is a static test message 2.",
    "You are kind chatbot. You have to reply about the user greeting message. Very kindly and friendly.",
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
    result_arr = collection.find({})
    question_arr = []
    for item in result_arr:
        question_arr.append(item["question"])

    score, index = get_best_question(question, question_arr)

    question_category = get_question_category(question)

    print(f"Question Category: {question_category}")

    if question_category == 1:
        # Want to talk to real person
        result = {
            "answer": "This is a chatbot meant to help, if you need more assistance reach out to your representative or our email group at: help@sapient.industries",
            "api": []
        }
        return result

    print(f"score is {score}")
    print(f"index is {index}")
    print(f"question is {question_arr[index]}")

    # If the search result is not exist
    if score < 50:
        index = get_best_response(question, notDetectedResponseList)
        system_msg = notDetectedSystemMSGList[index]
        print(f"Best Response index: {index}")
        print(f"System Message: {system_msg}")

        if index == 2:
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

        result = {
            "answer" : system_msg,
            "api" : []
        }

        return result
    else:
        # ------------ Generate Answer Using ChatGPT ------------
        system_msg = result_arr[index]["system_message"]
        relevant_arr = result_arr[index]["relevant"]
        api_arr = []
        result = []

        for relevant in relevant_arr:
            result = relevant_model.find_one({"response": relevant})
            if result != None:
                api_arr.append({
                    "response" : relevant,
                    "api" : result["api"],
                    "format" : result["format"]
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

def get_api_answer(api, format, question, stDate, enDate):

    EquipmentPowerConsumption.setDate(stDate, enDate)
    
    # ------------------- Matching api ---------------------
    if api == "get_most_consumption_equipment":
        """
        Response: 
            Return energy consumption for a specific piece of equipment
            Return highest power draw of equipment in specified time period and time of occurence.
            Return magnitude of change in energy consumption for [a specific piece of equipment]
        Format:
            Text
        """
        res = EquipmentPowerConsumption.get_most_consumption_equipment(question)

        if res != 404 and len(res) != 0:
            answer = generate_answer_from_openai(res)
            return answer, None
        else:
            return None
        
    elif api == "get_power_consumption_weekdays_weekend":
        """
        Response:
            Return time of day when average energy consumption was the highest over specified period (and kWh value)
        Format:
            Text
        """
        res = EquipmentPowerConsumption.get_power_consumption_weekdays_weekend(question)
        
        if res != 404 and len(res) > 0:
            answer = generate_answer_from_openai(res)
            return answer, None
        else:
            return None

    elif api == "get_building_energy_consumption_overall":
        """
        Response:
            Return total building energy consumption
            Return energy consumption by month for [total building]
            Return magintude of change for total building energy consumption from one period to the next (i.e., this month vs. last month)
        Format:
            Text, Text+BarChart
        """
        res = EquipmentPowerConsumption.get_building_energy_consumption_overall(question)
        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            data = []
            return answer, data
        else:
            return None
        
    elif api == "get_building_energy_consumption_by_end_uses_category":
        """
        Response:
            Return total building after hours energy consumption with a break down by [end use category]
            Return total building after hours energy consumption (and % of total)
            Return total building energy consumption with a break down by end use category
            Return aggregated energy consumption for a specific end use category
            Return total building after hours energy consumption (and % of total)
            Return aggregated after hours energy consumption for a specific end use category (and % of total of end use category)
            Return contribution of change to total building energy consumption broken down by [end-use category]
            Return magnitude of change in energy consumption for [a specific end use category]
        Format:
            Text+Pie Chart, Text, Text+Table
        """
        res = EquipmentPowerConsumption.get_building_energy_consumption_by_end_uses_category(question)

        if res != 404 and res != False:
            answer = generate_answer_from_openai(res)
            data = []
            return answer, data
        else:
            return None
        
    elif api == "get_energy_building_equipment":
        """
        Response:
            Return top 5 pieces of equipment that contribute most to energy consumption for a specific time period
            Return contribution of change to total building energy consumption broken down by [specific equipment] (show top 5 in magnitude)
            Return top 5 pieces of equipment that contribute most to whole building energy consumption
        Format:
            Text+Table
        """
        res = EquipmentPowerConsumption.get_energy_building_equipment(question)
        
        if res != 404 and res!= False:
            answer = generate_answer_from_openai(res)
            data = []
            return answer, data
        else:
            return None
        
    elif api == "get_explorer_equip_power_consumption":
        """
        Response:
            Return top 5 pieces of equipment that contribute most to energy consumption of a specific end use category
            Return top 5 pieces of equipment that contribute most to energy consumption for a specific equipment type
            Return top 5 contributors (specific pieces of equipment) that contributed to a change in energy consumption for [total building]
            Return top 5 contributors (specific pieces of equipment) that contributed to a change in energy consumption for [a specific end-use category]
            Return top 5 contributors (specific pieces of equipment) that contributed to a change in energy consumption for [a specific equipment type]
            Return top 5 contributors (specific pieces of equipment) that contributed to a change in energy consumption for [a specific space type]
        Format:
            Text+Table
        """
        res = EquipmentPowerConsumption.get_explorer_equip_power_consumption(question)
        
        if res != 404 and res!= False:
            answer = generate_answer_from_openai(res)
            data = []
            return answer, data
        else:
            return None

    return None

# Generate answer from data using OpenAI text completion
def generate_answer_from_openai(data):
    if type(data) is list:
        print("Generating answer as array...")
        data = IngestClass.process_array_data(data)
    else:
        print("Generating answer as object...")
        data = IngestClass.process_data(data)

    text = "\n".join([f"{item['key']}: {json.dumps(item['value'])}" for item in data])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content": 'You are an energy chatbot that helps tally power and energy consumption. Please provide a human readable sentence of this data. Should be understandable to 18 year old, and include almost of the data. In the data, there are question and the data. You must reference the data for generating answer. There are lots of data not related with question in the data. So you have to reference only related data. In the data, there is key related with question. So you must reference this value of key from data. Not reference all data. No warnings, no other text shold be present in your answer. All values representing electric power and energy consumption are Wh(watt-hours). But all values representing electric power and energy consumption must be converted to KWh(kilowatt-hours). 1000Wh is 1KWh. Therefore, all values representing electric power and energy consumption must be divided by 1000. Convert the all energy consumption from Wh(watt-hours) to kWh(kilowatt-hours). You must divide all values, even if the values are less than 1000. Please do not use original Wh(watt-hours) values.'
            },
            {
                "role": "user", 
                "content": text
            },
        ],
    )
        
    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]
        return assistant_reply
    else:
        return "Error"
    
# Function to get the best question and its index
def get_best_question(question, question_list):
    # Initialize variables to store the best response and its index
    best_response_index = -1
    best_response_score = -1.0  # Initialize with a low score

    for i, response in enumerate(question_list):
        # Generate a response from GPT-3 for the given question and response
        # prompt = f"the myQuestion is : '{question}' \n the myAnswer is : {response}.\n please score from 0 to 100 how much the myAnswer is the correct answer of the myQuestion.\n  your response must be like : Score = score "
        prompt = f"The myQuestion is : '{question}' \n the myQuestionTemplate is : {response}.\n Please rate from 0 to 100 how similar myQuestion is to myQuestionTemplate.\n  Your response must be like : Score = score "
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

    return best_response_score, best_response_index

# Function to detect the date request question
def get_question_category(question):
    prompt = f"The myQuestion is : '{question}' \n Please return 1 if the user want to talk with real person. If not, please return 0.\n Your reponse must be like : Result = result"
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=256
    )
    result = re.findall(r'\d+' , completion.choices[0].text.strip())
    if len(result):
        result = int(result[0])
        return result
    else:
        return 3


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