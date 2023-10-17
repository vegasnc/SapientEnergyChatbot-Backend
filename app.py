from flask import Flask, request
from pymongo import MongoClient
from models import keyword_intent # call model file
from models import questions # call model file
from models import relevant_api # call model file
from flask_cors import CORS # to avoid cors error in different frontend like react js or any other
from dotenv import dotenv_values

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
            "answer": "I'm sorry, your question is not registered in my database. I will inform administrator of this question."
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

    print("Question: " + api)
    
    # Get suitable data for generating answer
    s_data = generate_answer.get_api_answer(api, format, question, stDate, enDate, type_id, type_name)

    if s_data == None:
        return {
            "answer": "I'm sorry, your question is not registered in my database. I will inform administrator of this question."
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

@app.route('/api/get_equipment_list', methods=['POST'])
def get_equipment_list():
    equip_data = generate_answer.get_equipment_list()
    return {
        "result": equip_data
    }, 200

@app.route('/api/get_equipment_type', methods=['POST'])
def get_equipment_type():
    equip_type = generate_answer.get_equipment_type()
    return {
        "result": equip_type
    }, 200

@app.route('/api/get_end_use', methods=['POST'])
def get_end_use():
    end_use = generate_answer.get_end_use()
    return {
        "result": end_use
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
    app.run(debug=False)
