from pprint import pprint

import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


# Файл, полученный в Google Developer Console.
# Обязательно укажи полный путь к файлу, чтобы не было проблем с импортом
CREDENTIALS_FILE = r'C:\Users\User\Desktop\caradvancer\databases\googlesheets_api\creds.json'

# ID Google Sheets документа (можно взять из его URL)
spreadsheet_id = '1OC0lddSwlDTNTvQhXplnjFzwgRPw2_YjyC0I6cDWjC0'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())

# экземпляр обертки API, с которым работаем в дальнейшем
service = discovery.build('sheets', 'v4', http=httpAuth)


def google_recorder(id, lister):
    res = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'valueInputOption': 'RAW',
            'data': [
                {'range': f'Лист1!A{id}', 'values': [
                    [i for i in lister],
                ]},

            ]
        }
    ).execute()