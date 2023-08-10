from flask import Flask 
import openai
import os
import json
import ingest
import keyword_extraction


app = Flask(__name__)

# IngestClass = ingest.IngestDataClass()
# IngestClass.ingest_data()
KeywordExtraction = keyword_extraction.KeywordExtraction()
# keyword_extraction.extraction()
KeywordExtraction.matchingAPI(["regular basis", "equipment consumes"])

if __name__ == '__main__':
    app.run(debug=True)   
