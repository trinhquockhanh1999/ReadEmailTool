from __future__ import print_function

import os.path
import base64
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from requests.auth import HTTPBasicAuth
import requests
import google.auth

from JsonWorker import JsonWorker
from GmailWorker import GmailWorker
from SheetsWorker import SheetsWorker

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
SHEET_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1bGdnnBmQvgrdMRuGim4Y0orh4pKLMDK9uG2fUf9DZ0M'
RANGE_NAME = "Sheet!A1:E20"
GMAIL_TITLE = "ACB-Dich vu bao so du tu dong"
FILTER_LIST = [["ACB respectfully updates your *", "*"], 
               ["Updated account balance: *", "."],
               ["Latest transaction: Credit *", "."]]

def main():
    
    my_json = JsonWorker("data.json")
    gmail_scope = my_json.GetGmailScope()
    sheet_scope = my_json.GetSheetScope()
    spread_id = my_json.GetSpreadId()
    gmail_title = my_json.GetGmailTitle()
    filter_list = my_json.GetDataFilter()
    range_name = my_json.GetSheetRange()
    data_title = my_json.GetDataTitle()
    is_sheet_name = my_json.GetIsSheetName()
    init_number_email = my_json.GetInitEmailNum()
    normal_number_email = my_json.GetNormalEmailNum()
    email_labels = my_json.GetEmailLabels()
    # print(gmail_scope)
    # print(sheet_scope)
    # print(spread_id)
    # print(gmail_title)
    # print(filter_list)
    # print(range_name)
    # print(data_title)
    # print(is_sheet_name)
    # print(init_number_email)
    # print(normal_number_email)
    # print(email_labels)
    number_email = init_number_email
    my_gmail = GmailWorker(gmail_scope, tokenFile = "gmail-token.json")
    my_sheets = SheetsWorker(sheet_scope, tokenFile = "sheet_token.json")
    is_sheet_name_index = []
    while(1):
        sheets_name = []
        my_result = my_gmail.getNecessaryData(gmail_title, filter_list, email_labels, number_email, False)
        print(my_result)
        if number_email == init_number_email:
            for index in range(0, len(is_sheet_name)):
                if is_sheet_name[index] == "true":
                    is_sheet_name_index.append(index)
                    data_title.pop(index)
            print(data_title)
        else:
            pass
        for my_data in my_result:
            for index in is_sheet_name_index:
                sheets_name.append(my_data[index])
                my_data.pop(index)
        print(sheets_name)
        number_email = normal_number_email
        my_sheets.Process(spread_id, sheets_name, range_name, data_title, my_result)
        


    #print(my_result)



if __name__ == '__main__':
    main()