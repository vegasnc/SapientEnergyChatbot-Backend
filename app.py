from flask import Flask, request
from flask_mail import Mail, Message
from pymongo import MongoClient
from models import keyword_intent # call model file
from models import questions # call model file
from models import relevant_api # call model file
from flask_cors import CORS # to avoid cors error in different frontend like react js or any other

import engine.construct_questions as construct_questions
import engine.generate_answer as generate_answer

app = Flask(__name__)
CORS(app, methods=[ 'POST', 'GET' ], allow_headers=[ 'Content-Type' ])

# Init mongo db and create collection
keyword_intent = keyword_intent.KeywordIntent()
question_model = questions.Questions()
relevant_model = relevant_api.RelevantAPI()

# configuration of mail
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'maksymdidkivskyi2@gmail.com'
app.config['MAIL_PASSWORD'] = 'maksymdidkiv285/'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/api/get_answer', methods=['POST'])
def get_answer():
    # Access the request data
    data = request.get_json()
    question = data["question"]

    print("Question: " + question)
    
    # Get suitable data for generating answer
    # s_data = generate_answer.get_answer(question, keyword_intent)

    # Generate answer using ChatGPT
    s_data = generate_answer.get_answer(question, question_model)

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

    print("Question: " + api)
    
    # Get suitable data for generating answer
    s_data = generate_answer.get_api_answer(api, format, question, stDate, enDate)

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

    msg = Message(
        'Feedback',
        sender = 'vegaslancer1025@gmail.com',
        recipients = ['maksymdidkivskyi2@gmail.com']
    )
    msgContent = "ChatHistory : \n\n" + history + "\n\n"
    msgContent += "Rate My Data : " + str(rate_my_data) + "\n\n"
    msgContent += "Rate My Ability : " + str(rate_my_ability) + "\n\n"
    msgContent += "Additional Comments : " + feedback + "\n\n"
    msg.body = msgContent
    mail.send(msg)

    return {
        "result": "success"
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
