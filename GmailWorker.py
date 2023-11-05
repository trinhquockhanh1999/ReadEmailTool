import os.path
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailWorker():
    __service = None
    def __init__(self, scope : str, tokenFile : str, credentialsFile : str = "credentials.json", port : int = 0) -> None:
        self.__service = self.getAccessPermission(scope, credentialsFile, tokenFile, port)
        pass

    def __del__(self):
        pass


    def getEmailSubject(self, __msgInfo : dict) -> str:
        msg_headers = __msgInfo['payload']['headers']
        msg_subject = ''
        for header in msg_headers:
            name = header.get("name")
            if(name.lower() == "subject"):
                msg_subject = header.get("value")
                break
        return msg_subject

    def getEmailDate(self, __msgInfo : dict) -> str:
        msg_headers = __msgInfo['payload']['headers']
        msg_date = ''
        for header in msg_headers:
            name = header.get("name")
            if(name.lower() == "date"):
                msg_date = header.get("value")
                break
        return msg_date
        
    def getEmailContent(self, __msgInfo : dict) -> str:
        return self.convertEncodeToDecode(__msgInfo['payload']['parts'][0]['body']['data'])

    def getNecessaryData(self, subject : str, filterList : list, labels : list, maxResults : int, includeSpamTrash : bool) -> list:
        try:
            # Call the Gmail API
            
            msg_info_list = self.__service.users().messages().list(userId='me', maxResults = maxResults, includeSpamTrash = includeSpamTrash, labelIds = labels).execute()
            msg_list = msg_info_list['messages']
            print(msg_list)
            nec_data_list = []
            post_data = {
                "removeLabelIds": [
                    "UNREAD"
                ]
            }
            for msg in msg_list:
                msg_info = self.__service.users().messages().get(userId='me', id = msg['id']).execute()
                msg_subject = self.getEmailSubject(msg_info)
                print(msg_subject)
                #print(msg_subject)
                if msg_subject in subject:
                    msg_data = self.getEmailContent(msg_info)
                    msg_time = self.getEmailDate(msg_info)
                    tmp = msg_time.rsplit(" ", 2)
                    msg_date = tmp[0]
                    msg_hour = tmp[1]
                    #print(msg_data)
                    nec_data = self.filterData(msg_data, filterList)
                    nec_data.insert(0, msg_hour)
                    nec_data.insert(0, msg_date)
                    nec_data_list.append(nec_data)
                    #print(nec_data_list)
                    self.__service.users().messages().modify(userId = 'me', id=msg['id'], body=post_data).execute()
            return nec_data_list
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')
            return None
    
    def filterData(self, inputData : str, filterList : list) -> list:
        output_data = []
        for my_filter in filterList:
            if len(my_filter) > 0:
                head = my_filter[0]
                tmp = inputData.split(head)
                #print(tmp[1])
                if len(my_filter) > 1:
                    tail = my_filter[1]
                    element = ""
                    for charactor in tmp[1]:
                        
                        if charactor.isdigit():
                            element += charactor
                        if charactor == tail:
                            break
                output_data.append(element)
            
        #print(output_data)
        return output_data
            

    def convertEncodeToDecode(self, dataInput : str) -> str:
        dataInput = dataInput.replace("-", "+")
        dataInput = dataInput.replace("_", "/")
        base64_bytes = dataInput.encode("utf-8")
        string_bytes = base64.b64decode(base64_bytes)
        string_data = string_bytes.decode("utf-8")
        dataOutput = string_data.split("<html>", 1)
        return dataOutput[0]

    def getAccessPermission(self, scope : str, credentialsFile : str = "credentials.json", tokenFile : str = "token.json", port : int = 0):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(tokenFile):
            creds = Credentials.from_authorized_user_file(tokenFile, scope)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print(credentialsFile)
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentialsFile, scope)
                creds = flow.run_local_server(port=port)
            # Save the credentials for the next run
            with open(tokenFile, 'w') as token:
                token.write(creds.to_json())
        mail_service = build('gmail', 'v1', credentials=creds)
        return mail_service