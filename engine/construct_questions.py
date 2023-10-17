import pandas as pd

def construct_questions(collection):
    # Read the .xlsx file
    question_data = pd.read_excel('quiz_response_system.xlsx')

    # Access the content
    question_column = question_data['Questions']
    relevant_column0 = question_data['Relevant0']
    relevant_column1 = question_data['Relevant1']
    relevant_column2 = question_data['Relevant2']
    system_message_column = question_data['SystemMessage']
    static_column = question_data['Static']

    keyword_list = []

    for index in range(len(question_column)):
        keyword_list.append(
            {
                "question": question_column[index],
                "relevant": [relevant_column0[index], relevant_column1[index], relevant_column2[index]],
                "system_message": system_message_column[index],
                "is_static_message": static_column[index] == "0"
            }
        )
    
    # Insert the data to database
    for item in keyword_list:
        collection.create(item)
    
    print("Questions Construct Successed!!!")

def construct_relevant(collection):
    # Read the .xlsx file
    question_data = pd.read_excel('response_api.xlsx')

    # Access the content
    response_column = question_data['Response']
    api_column = question_data['API']
    format_column = question_data['Format']
    title_column = question_data['Title']
    dropdown_column = question_data['Dropdown']

    row = []

    for index in range(len(response_column)):
        row.append(
            {
                "response": response_column[index],
                "api": api_column[index],
                "format": str(format_column[index]),
                "title": "" if pd.isnull(title_column[index]) else title_column[index],
                "dropdown": "" if pd.isnull(dropdown_column[index]) else dropdown_column[index]
            }
        )
    
    # Insert the data to database
    for item in row:
        collection.create(item)
    
    print("Questions Construct Successed!!!")

