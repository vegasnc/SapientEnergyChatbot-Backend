from flask import Flask, request
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

    print("Question: " + api)
    
    # Get suitable data for generating answer
    s_data = generate_answer.get_api_answer(api, question)

    if s_data == None:
        return {
            "answer": "I'm sorry, your question is not registered in my database. I will inform administrator of this question."
        }, 200
    else:
        return {
            "answer": s_data
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
    app.run()
