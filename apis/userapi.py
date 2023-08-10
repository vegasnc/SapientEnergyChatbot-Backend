from flask import Flask
import requests
import apis.constapis as constapis
from dotenv import load_dotenv
import os

class UserAPI:
    ConstAPIClass = None
    def __init__(self) -> None:
        load_dotenv()
        self.ConstAPIClass = constapis.APIClass()
        

    # check user login status (success : true, faild: false)
    def check_user_login_status(self):
        if self.check_token_validity() == 403:
            # if user didn't login, login again
            response = self.signin(os.getenv("LOGIN_USER_NAME"), os.getenv("LOGIN_PASSWORD"))
            if response == 404:
                return False
            else:
                user_token = response["data"]["token"]
                constapis.USER_TOKEN = user_token
                return True
        else:
            # User logged in
            return True

    # User SignUp
    def signup(self, first_name, last_name, email, password, vendor):
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "vendor": vendor
        }
        response = requests.post(constapis.BASE_URL + constapis.SIGNUP,
                                json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()

    # User SignIn
    def signin(self, email, password):
        data = {
            "email": email,
            "password": password,
        }
        response = requests.post(constapis.BASE_URL + constapis.SIGNIN,
                                json=data, headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        
    # User Check Token Validity
    def check_token_validity(self):
        response = requests.get(constapis.BASE_URL + constapis.CHECK_TOKEN,
                                headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        
    # Get user permissions
    def get_user_permissions(self):
        response = requests.get(constapis.BASE_URL + constapis.GET_USER_PERMISSIONS,
                                headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        