import pandas as pd
import engine.keyword_extract as keyword_extract

def construct_questions(collection):
    # Read the .xlsx file
    question_data = pd.read_excel('quiz_relevant.xlsx')

    # Access the content
    question_column = question_data['Questions']
    relevant_column0 = question_data['Relevant0']
    relevant_column1 = question_data['Relevant1']
    relevant_column2 = question_data['Relevant2']
    system_message_column = question_data['SystemMessage']

    keyword_list = []

    for index in range(len(question_column)):
        rankedList = keyword_extract.keyword_extration(question_column[index])
        keyword_list.append(
            {
                "keywords": rankedList,
                "relevant": [relevant_column0[index], relevant_column1[index], relevant_column2[index]],
                "system_message": system_message_column[index]
            }
        )
    
    # Insert the data to database
    for item in keyword_list:
        collection.create(item)
    
    print("Questions Construct Successed!!!")

def construct_relevant(collection):
    # Read the .xlsx file
    question_data = pd.read_excel('relevant.xlsx')

    # Access the content
    response_column = question_data['Response']
    api_column = question_data['API']

    keyword_list = []

    for index in range(len(response_column)):
        rankedList = keyword_extract.keyword_extration(response_column[index])
        keyword_list.append(
            {
                "keywords": rankedList,
                "response": response_column[index],
                "api": api_column[index]
            }
        )
    
    # Insert the data to database
    for item in keyword_list:
        collection.create(item)
    
    print("Questions Construct Successed!!!")
