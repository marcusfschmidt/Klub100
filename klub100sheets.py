
import pandas as pd
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
# import google.auth.transport.requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def klubhest(loc):
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # here enter the id of your google sheet
    # SAMPLE_SPREADSHEET_ID_input = '1JR03yrHEIwk8qJFmEM8Ev5kwxp4IRJydvggDLfpe5F0'
    SAMPLE_SPREADSHEET_ID_input = '1ZkggMIjbhU11oiux9mXN_OgXn09o-bcrE7A0McpvP3c'

    SAMPLE_RANGE_NAME = 'A1:AA1000'
    
    def main():

        """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    global values_input, service
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    
    main()
    df=pd.DataFrame(values_input[1:], columns=values_input[0])
    return df