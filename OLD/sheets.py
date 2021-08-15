
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import os
import pickle

def klubhest():
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # here enter the id of your google sheet
    SAMPLE_SPREADSHEET_ID_input = '1JR03yrHEIwk8qJFmEM8Ev5kwxp4IRJydvggDLfpe5F0'
    SAMPLE_RANGE_NAME = 'A1:AA1000'
    
    def main():
        global values_input, service
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'creds.json', SCOPES) # here enter the name of your downloaded JSON file
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    
        service = build('sheets', 'v4', credentials=creds)
    
        # Call the Sheets API
        sheet = service.spreadsheets()
        result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                    range=SAMPLE_RANGE_NAME).execute()
        values_input = result_input.get('values', [])
    
    
    main()
    df=pd.DataFrame(values_input[1:], columns=values_input[0])
    return df

