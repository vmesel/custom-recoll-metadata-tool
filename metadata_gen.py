# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from collections import OrderedDict

from decouple import config

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = config('SPREADSHEET_ID')
SAMPLE_RANGE_NAME = 'Form Responses 1!A:P'


class MetadataGenerator:
    def __init__(self):
        """
        Esse constructor realiza a autenticação
        """

        self.creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            	self.creds = flow.run_local_server(port=0)
        token = open('token.pickle', 'wb')
        pickle.dump(self.creds, token)
        token.close()


    def _create_dictionary(self, values):
        if len(values) == 1:
            return False

        return_list = []
        model_dictionary = OrderedDict((k, "") for k in values[0])

        for row in values[1:]:
            copied_dict = model_dictionary.copy()
            for i, title in enumerate(values[0]):
                copied_dict[title] = row[i]

            return_list.append(copied_dict)

        return [return_list]


    def get_metadata_from_sheets(self):
        service = build('sheets', 'v4', credentials=self.creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            return False
        
        formatted_metadata = self._create_dictionary(values)

        return formatted_metadata

    def generate_metadata_json(self):
        metadata_ = self.get_metadata_from_sheets()

        metadata_dict = {}
        
        middle_json = [json.loads(json.dumps(meta)) for meta in metadata_[0]]
        end_dict = { item[u"nome_arquivo"]: item for item in middle_json }
        text = repr(end_dict).decode("unicode-escape").replace("u'", "'")

        print(text.replace("'", "\"").replace("\n", "").encode('utf-8'))

        

if __name__ == '__main__':
    main = MetadataGenerator()
    main.generate_metadata_json()
