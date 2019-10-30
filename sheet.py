import gspread
import datetime
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

GOOGLE_API_TOKEN = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]


class Sheet:
    def __init__(self, sheet_url):
        # use creds to create a client to interact with the Google Drive API
        self.scope = ["https://spreadsheets.google.com/feeds"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(GOOGLE_API_TOKEN), self.scope
        )
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_url(sheet_url).sheet1

    def all(self):
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

