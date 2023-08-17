import pandas as pd
import engine.keyword_extract as keyword_extract

def extraction(collection):
    # Read the .xlsx file
    question_data = pd.read_excel('quiz.xlsx')

    # Access the content
    question_column = question_data['Question']
    intent_column = question_data['Intent']
    api_column = question_data['API']

    keyword_list = []

    for index in range(len(question_column)):
        rankedList = keyword_extract.keyword_extration(question_column[index])
        keyword_list.append(
            {
                "keywords": rankedList,
                "intents": intent_column[index],
                "api": api_column[index]
            }
        )
        print(keyword_list)
    
    # Insert the data to database
    for item in keyword_list:
        collection.create(item)
    
    print("Extract Successed!!!")
