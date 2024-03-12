from flask import Flask
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session

import requests
import apis.constapis as constapis
from dotenv import load_dotenv
import os

class UserAPI:
    ConstAPIClass = None
    session = Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    def __init__(self) -> None:
        load_dotenv()
        self.ConstAPIClass = constapis.APIClass()
        

    # check user login status (success : true, faild: false)
    def check_user_login_status(self):
        if self.check_token_validity() == 403:
            print(f"User Name : {os.getenv('LOGIN_USER_NAME')}")
            print(f"User Password : {os.getenv('LOGIN_PASSWORD')}")
            # if user didn't login, login again
            response = self.signin(os.getenv("LOGIN_USER_NAME"), os.getenv("LOGIN_PASSWORD"))
            if response == 404:
                return False
            elif response == 422:
                return False
            else:
                print(f"-----------------Response = {str(response)}-----------------")
                user_token = response["data"]["token"]

                print(f"------------------------- User Token ------------------------- = {user_token}")
                return user_token
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
        response = requests.request("POST", constapis.BASE_URL + constapis.SIGNUP,
                                data=data, headers=self.ConstAPIClass.getHeader(), timeout=600)
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
        # response = requests.request("POST", constapis.BASE_URL + constapis.SIGNIN, json=data,
        #                             headers=self.ConstAPIClass.getHeader(), timeout=600)
        timeout_value = 30
        response = self.session.post(constapis.BASE_URL + constapis.SIGNIN, 
                                     timeout=timeout_value, json=data, 
                                     headers=self.ConstAPIClass.getHeader())
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        
    # User Check Token Validity
    def check_token_validity(self):
        try:
            print(f"----------------------------- Check token  validaty -----------------------------")
            # response = requests.get(constapis.BASE_URL + constapis.CHECK_TOKEN,
            #                         headers=self.ConstAPIClass.getHeader(), timeout=600, verify=False)
            # response = requests.request("GET", constapis.BASE_URL + constapis.CHECK_TOKEN, 
            #                             headers=self.ConstAPIClass.getHeader(), timeout=600)
            response = self.session.get(constapis.BASE_URL + constapis.CHECK_TOKEN, 
                                     timeout=30, headers=self.ConstAPIClass.getHeader())
            print(f"----------------------------- Response : {response} -----------------------------")
        except Exception as e:
            print(f"----------------------------- ERROR : {e} -----------------------------")
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        
    # Get user permissions
    def get_user_permissions(self):
        response = requests.request("GET", constapis.BASE_URL + constapis.GET_USER_PERMISSIONS,
                                    headers=self.ConstAPIClass.getHeader(), timeout=600)
        if response.status_code != 200:
            return response.status_code
        else:
            return response.json()
        