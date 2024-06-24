# access email: test-798@crypto-talon-327110.iam.gserviceaccount.com


import os.path

from datetime import datetime

import gspread
import pandas as pd

from deeplay.utils.get_root_directory import get_root_directory
from family_fund.numeric import *
from family_fund.time import to_datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as CredentialsOAuth
from google.oauth2.service_account import Credentials as CredentialsSA
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class SpreadSheetSyncer:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    def __init__(
        self,
        spreadsheet_id,
        client_secret_fn=os.path.join(get_root_directory(__file__), "credentials/client_secret.json"),
        service_account_secret_fn=os.path.join(get_root_directory(__file__), "credentials/service_account_secret.json"),
    ):
        self.client_secret_fn = client_secret_fn
        self.service_account_secret_fn = service_account_secret_fn
        self.spreadsheet_id = spreadsheet_id
        self._init_credentials()
        self._init_sheet()
        self._init_worksheet_list()

    def _init_credentials(self):
        creds = None
        if os.path.exists("token.json"):
            creds = CredentialsOAuth.from_authorized_user_file("token.json", self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_fn, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        self.creds = creds

        self.creds_sa = CredentialsSA.from_service_account_file(self.service_account_secret_fn, scopes=self.SCOPES)

    def _init_worksheet_list(self):
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheets = sheet_metadata.get("sheets", "")
        self.worksheets = [sheet.get("properties", {}).get("title", "Sheet1") for sheet in sheets]

    def _init_sheet(self):
        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()
        self.gc = gspread.authorize(self.creds_sa).open_by_key(self.spreadsheet_id)

    def _parse(self, value):
        if isinstance(value, list):
            return [self._parse(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._parse(v) for k, v in value.items()}
        elif is_int_like(value):
            return cast_int(value)
        elif is_float_like(value):
            return float(value)
        elif isinstance(value, str):
            try:
                return to_datetime(value)
            except:
                pass
        return value

    def _format(self, value):
        if is_none(value):
            return ""
        if isinstance(value, list):
            return [self._format(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._format(v) for k, v in value.items()}
        elif isinstance(value, datetime):
            return str(value)

        return value

    def read_sheet(self, sheet_name):
        result = self.sheet.values().get(spreadsheetId=self.spreadsheet_id, range=f"{sheet_name}!A1:M").execute()
        values = result.get("values", [])
        values = self._parse_values(values)
        if not values:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])

    def read_sheet_sa(self, sheet_name):
        sheet_index = self.worksheets.index(sheet_name)
        sheet = self.gc.get_worksheet(sheet_index)
        values = sheet.get_all_values()
        values = self._parse(values)

        if not values:
            return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])

    def write_sheet_sa(self, sheet_name, df):
        sheet_index = self.worksheets.index(sheet_name)
        sheet = self.gc.get_worksheet(sheet_index)
        values = [df.columns.values.tolist()] + df.values.tolist()
        values = self._format(values)
        self.clear(sheet_name)
        sheet.update(values)

    def read(self, sheet_name):
        return self.read_sheet_sa(sheet_name)

    def write(self, sheet_name, df):
        return self.write_sheet_sa(sheet_name, df)

    def clear(self, sheet_name):
        range_all = f"{sheet_name}!A1:Z"
        return (
            self.service.spreadsheets()
            .values()
            .clear(spreadsheetId=self.spreadsheet_id, range=range_all, body={})
            .execute()
        )
