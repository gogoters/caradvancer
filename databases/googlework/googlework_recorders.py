from pprint import pprint

import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


# Файл, полученный в Google Developer Console
CREDENTIALS_FILE = 'creds.json'
# ID Google Sheets документа (можно взять из его URL)
spreadsheet_id = '1OC0lddSwlDTNTvQhXplnjFzwgRPw2_YjyC0I6cDWjC0'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())

#экземпляр обертки API, с которым работаем в дальнейшем
service = discovery.build('sheets', 'v4', http = httpAuth)


def google_recorder(lister):
    values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'valueInputOption': 'RAW',
            'data': [
                {'range': 'Лист1!A1', 'values': [i for i in lister
                ]},
            ]
        }
    ).execute()



# Пример чтения файла
# values = service.spreadsheets().values().get(
#     spreadsheetId=spreadsheet_id,
#     range='A1:E10',
#     majorDimension='COLUMNS'
# ).execute()
# pprint(values)

# Пример записи в файл
values = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'valueInputOption': 'RAW',
        'data': [
            {'range': 'Лист1!A2', 'values': [
                ["Azzrael Code", "YouTube Channel"],
                ["More about", "Google Sheets API"],
                ["styling", "formulas", "charts"],
            ]},
            {'range': 'Лист1!A4', 'values': [
                ["Azzrael Code", "YouTube Channel"],
                ["More about", "Google Sheets API"],
                ["styling", "formulas", "charts"],
            ]}
        ]
    }
).execute()