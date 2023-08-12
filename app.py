from flask import Flask, request
from pymongo import MongoClient
from models import keyword_intent # call model file
from flask_cors import CORS # to avoid cors error in different frontend like react js or any other
import engine.training_bot as training_bot
import engine.generate_answer as generate_answer

app = Flask(__name__)
CORS(app)

# Init mongo db and create collection
keyword_intent = keyword_intent.KeywordIntent()

@app.route('/api/get_answer', methods=['POST'])
def get_answer():
    # Access the request data
    data = request.get_json()
    question = data["question"]

    
    # Get suitable data for generating answer
    s_data = generate_answer.get_answer(question, keyword_intent)

    if s_data == None:
        return {
            "answer": "I'm sorry, your question is not registered in my database. I will inform administrator of this question."
        }, 200
    else:
        return {
            "answer": s_data
        }, 200  

if __name__ == '__main__':
    training_bot.extraction(keyword_intent)
    app.run(debug=True, use_reloader=False)
