import gspread
import datetime
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Sheet:
    def __init__(self, sheet_url):
        # use creds to create a client to interact with the Google Drive API
        self.scope = ["https://spreadsheets.google.com/feeds"]
        self.authorize(sheet_url)

    def all(self):
        if self.creds.access_token_expired:
            self.client.login()
        return self.sheet.get_all_records()

    def insert(self, row):
        records = self.all()
        row_count = len(records)
        self.sheet.insert_row(row, row_count + 2)

    def get_untranslated_terms(self):
        untranslated = []
        for term in self.all():
            if not term["Arabic"]:
                untranslated.append(term)

        return untranslated

    def authorize(self, sheet_url):
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            BASE_DIR + '/cred.json', self.scope
        )

        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_url(sheet_url).sheet1
