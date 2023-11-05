import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pandas import DataFrame
from CmnBase import CmnBase

class SheetsWorker(CmnBase):
    __service = None

    def __init__(self, scope : str, tokenFile : str, credentialsFile : str = "credentials.json", port : int = 0) -> None:
        self.__service = self.GetAccessPermission(scope, credentialsFile, tokenFile, port)
        pass

    def __del__(self):
        pass


    def GetDataFrame(self, myId : str, myRange : str) -> DataFrame:
        output = None
        result = self.__service.spreadsheets().values().get(spreadsheetId=myId, range=myRange).execute()
        if result.get("values"):
            output = result["values"]
        return output

    # def findCellUpdate(labels : str, ) ->

    def CheckTitlesExist(self, sheetTitles : list, dataFrame : list) -> int:
        res = 0
        cnt = 0
        print(dataFrame)
        if dataFrame != None:
            length_data = self.SizeOf(dataFrame[0])
        else:
            length_data = 0
        if length_data > 0:
            titles = dataFrame[0]
            for index in range (0, min(len(sheetTitles), length_data)):
                if titles[index] == sheetTitles[index]:
                    cnt += 1
            print(cnt)
            if cnt == len(sheetTitles):
                res = 0
            elif cnt == 0:
                res = 2
            else:
                res = 1
        else:
            res = 1 
        return res

    def UpdateTitles(self, SheetsID : str, rangeName : str, sheetTitles : list, dataFrame : list, isTitlesInvail : int):
        if isTitlesInvail == 1:        
            self.UpdateSheetData(SheetsID, rangeName, 0, 0, sheetTitles)
        elif isTitlesInvail == 2:
            dataFrame.insert(0, sheetTitles)
            self.UpdateSheetData(SheetsID, rangeName, 0, 0, dataFrame)
        else:
            pass
    
    def CheckAvailableSheet(self, spreadSheetsID : str, sheetName : str) -> bool:
        output = False
        spreadsheet_info = self.__service.spreadsheets().get(spreadsheetId=spreadSheetsID).execute()
        #print(spreadsheet_info)
        sheets_info = spreadsheet_info["sheets"]
        available_sheets_name = []
        for sheet in sheets_info:
            available_sheets_name.append(sheet["properties"]["title"])
        if sheetName in available_sheets_name:
            output = True
        return output

    def Process(self, spreadSheetsID : str, sheetsName : str, myRange : str, sheetTitles : list, dataUpdate : list):
        for index in range (0, len(sheetsName)):
            is_avail_sheet = self.CheckAvailableSheet(spreadSheetsID, sheetsName[index])
            if is_avail_sheet == False:
                self.CreatNewSheet(spreadSheetsID, sheetsName[index])
            range_name = sheetsName[index] + "!" + myRange
            dataFrame = self.GetDataFrame(spreadSheetsID, range_name)
            is_Titles_Invail = self.CheckTitlesExist(sheetTitles, dataFrame)
            if is_Titles_Invail != 0:
                self.UpdateTitles(spreadSheetsID, range_name, sheetTitles, dataFrame, is_Titles_Invail)
                self.UpdateSheetData(spreadSheetsID, range_name, self.SizeOf(dataFrame)+2, 0, dataUpdate[index])
            else:
                print("Sheet's Title is correct") 
                self.UpdateSheetData(spreadSheetsID, range_name, self.SizeOf(dataFrame)+1, 0, dataUpdate[index])

    def UpdateSheetData(self, spreadSheetsID : str, rangeName : str, rowStart : int, colStart : int, data : list):
        try:
            new_range_name = ""
            new_data = []
            convert_data = []
            if data != None and data != [] and type(data[0]) == type(""):
                convert_data.append(data)
            else:
                convert_data = data
            if rowStart != 0:
                string_temp = rangeName.split("!")
                range_cell = string_temp[1].split(":")
                start_cell = range_cell[0].replace(":", "")
                print(start_cell)
                number_row = ""
                for charactor in start_cell:
                    if charactor.isdigit() == True:
                        number_row += charactor
                print(number_row)
                new_start_cell = start_cell.replace(number_row, str(rowStart))
                print(new_start_cell)
                new_range_name = rangeName.replace(start_cell, new_start_cell)
            else:
                new_range_name = rangeName

            if colStart != 0:
                for old_data in convert_data:
                    data_temp = []   
                    for col in range(0, colStart):
                        new_data.append(data_temp)
                    new_data.append(old_data)
            else:
                new_data = convert_data
            #print(new_data)
            body = {
                'values': new_data
            }
            result = self.__service.spreadsheets().values().update(
                spreadsheetId=spreadSheetsID, range=new_range_name,
                valueInputOption="USER_ENTERED", body=body).execute()
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
    
    def GetAccessPermission(self, scope : str, credentialsFile : str = "credentials.json", tokenFile : str = "token.json", port : int = 0):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        #print(self.tokenFile)
        if os.path.exists(tokenFile):
            creds = Credentials.from_authorized_user_file(tokenFile, scope)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                #print(self.credentialsFile)
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentialsFile, scope)
                creds = flow.run_local_server(port=port)
            # Save the credentials for the next run
            with open(tokenFile, 'w') as token:
                token.write(creds.to_json())
        sheet_service = build('sheets', 'v4', credentials=creds)
        return sheet_service

    def CreatNewSheet(self, spreadSheetsID : str, sheetName : str) -> str:
        my_request = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": sheetName
                        }
                    }
                }
            ]
        }
        sheetId = self.__service.spreadsheets().batchUpdate(spreadsheetId = spreadSheetsID, body = my_request) \
            .execute()
        return sheetId