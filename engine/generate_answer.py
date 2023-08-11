from rake_nltk import Rake
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

# Generate answer from question
def get_answer(question, collection):

    # Extract keyword for searching API
    keyword_arr = keyword_extract.keyword_extration(question)
    print("========================keyword array======================")
    print(keyword_arr)
    result = collection.find_one({"keywords": {"$all" : keyword_arr}})
    
    # If the search result is not exist
    if result == None:
        return None
    # Matching api
    # What is the average power consumption of our equipment?
    elif result["api"] == "get_avg_power_consumption":
        res = EquipmentPowerConsumption.get_avg_power_consumption()
        print("generate_answer: 30 : ------------res-------------")
        print(res)
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
    return None

# Generate answer from data using OpenAI text completion
def generate_answer_from_openai(data):
    data = IngestClass.process_data(data)
    text = "\n".join([f"{item['key']}: {json.dumps(item['value'])}" for item in data])
    print("generate_answer: 54 : ------------text-------------")
    print(text)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system", 
                "content": text
            },
            {
                "role": "user", 
                "content": 'Please provide a human readable version of this data. Should be understandable to 18 year old, and include all of the data. No warnings, no other text shold be present in your answer.'
            },
        ],
    )
        
    if response and response.choices:
        assistant_reply = response.choices[0].message["content"]
        return assistant_reply
    else:
        return "Error"
