from flask import Flask, request
from pymongo import MongoClient
from models import keyword_intent # call model file
from models import questions # call model file
from models import relevant_api # call model file
from flask_cors import CORS # to avoid cors error in different frontend like react js or any other
from dotenv import dotenv_values

import apis.userapi as userapi
import apis.constapis as constapis
import engine.construct_questions as construct_questions
import engine.generate_answer as generate_answer
import smtplib

app = Flask(__name__)
CORS(app, methods=[ 'POST', 'GET' ], allow_headers=[ 'Content-Type' ])

env_vars = dotenv_values('.env')

# Init mongo db and create collection
keyword_intent = keyword_intent.KeywordIntent()
question_model = questions.Questions()
relevant_model = relevant_api.RelevantAPI()
UserAPIClass = userapi.UserAPI()
ConstAPIClass = constapis.APIClass()

global mBuildingData
global mEquipType
global mEndUse
mBuildingData = None
mEquipType = None
mEndUse = None

@app.route('/api/get_prepopulated_data', methods=['POST'])
def get_prepopulated_data():
    return {
        "building_data" : mBuildingData,
        "equip_type" : mEquipType,
        "end_use" : mEndUse,
    }, 200

@app.route('/api/get_answer', methods=['POST'])
def get_answer():
    # Access the request data
    data = request.get_json()
    question = data["question"]
    stDate = data["stDate"]
    enDate = data["enDate"]

    print("Question: " + question)
    
    # Get suitable data for generating answer
    # s_data = generate_answer.get_answer(question, keyword_intent)

    # Generate answer using ChatGPT
    s_data = generate_answer.get_answer(question, question_model, stDate, enDate)

    if s_data == None:
        return {
            "answer": "I apologize for the inconvenience, but I'm unable to assist with navigating across the platform at the moment. It's possible that you may require personalized guidance for this. To ensure you get the help you need, I recommend reaching out to our support team. They have the expertise to assist you with platform navigation and any other questions you may have. They'll be glad to guide you further. Is there anything else I can assist you with today?"
        }, 200
    else:
        return {
            "answer": s_data
        }, 200  
    
@app.route('/api/get_api_answer', methods=['POST'])
def get_api_answer():
    # Access the request data
    data = request.get_json()
    api = data["api"]
    question = data["question"]
    format = data["format"]
    stDate = data["stDate"]
    enDate = data["enDate"]
    type_id = data["type_id"]
    type_name = data["type_name"]
    building_id = data["building_id"]
    building_name = data["building_name"]

    print("Question: " + api)

    print(f"Building infor: id: {building_id}, name: {building_name}, type_id: {type_id}, type_name: {type_name}")
    
    # Get suitable data for generating answer
    s_data = generate_answer.get_api_answer(api, format, question, stDate, enDate, building_id, building_name, type_id, type_name)

    if s_data == None:
        return {
            "answer": "I apologize for the inconvenience, but I'm unable to assist with navigating across the platform at the moment. It's possible that you may require personalized guidance for this. To ensure you get the help you need, I recommend reaching out to our support team. They have the expertise to assist you with platform navigation and any other questions you may have. They'll be glad to guide you further. Is there anything else I can assist you with today?"
        }, 200
    else:
        return {
            "answer": s_data
        }, 200  
    
@app.route('/api/send_feedback', methods=['POST'])
def get_send_feedback():
    data = request.get_json()
    feedback = data["feedback"]
    history = data["history"]
    rate_my_data = data["rate_my_data"]
    rate_my_ability = data["rate_my_ability"]
    email = data["email"]

    gmailaddress = env_vars["MAIL_ADDRESS"]
    gmailpassword = env_vars["MAIL_PASSWORD"]
    mailto = env_vars["RECEIPIENT_ADDRESS"]

    msgContent = "From " + email + "\n\n"
    msgContent += "ChatHistory : \n\n" + history + "\n\n"
    msgContent += "Rate My Data : " + str(rate_my_data) + "\n\n"
    msgContent += "Rate My Ability : " + str(rate_my_ability) + "\n\n"
    msgContent += "Additional Comments : " + feedback + "\n\n"

    try:
        mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
        mailServer.starttls()
        mailServer.login(gmailaddress , gmailpassword)
        mailServer.sendmail(gmailaddress, mailto , msgContent)
        print(f"Successfully sent message")
        mailServer.quit()
        return {
            "result": "success"
        }, 200
    except Exception as e:
        print(f"An error occurred while sending{str(e)}")
        return {
            "result": "false"
        }, 200

# --------------- Building database --------------- 
@app.route('/model/question', methods=['GET'])
def set_question_model():
    construct_questions.construct_questions(question_model)

    return {
        "answer": "Success! "
    }, 200

@app.route('/model/relevant', methods=["GET"])
def set_relevant_model():
    construct_questions.construct_relevant(relevant_model)
    return {
        "answer": "Success! "
    }, 200
    

if __name__ == '__main__':
    print("Server is running 5000")
    token = UserAPIClass.check_user_login_status()
    constapis.USER_TOKEN = token

    mBuildingData = generate_answer.get_building_data()
    mEquipType = generate_answer.get_equipment_type()
    mEndUse = generate_answer.get_end_use()
    app.run(debug=False)
