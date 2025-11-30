import os
import datetime
from flask import Flask, request, jsonify, send_from_directory
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__, static_url_path='')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']

def get_credentials():
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
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def find_or_create_diary(service, drive_service):
    # Search for the file
    query = "name = 'My New Diary' and mimeType = 'application/vnd.google-apps.document' and trashed = false"
    results = drive_service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()
    items = results.get('files', [])

    if not items:
        # Create the file
        file_metadata = {
            'name': 'My New Diary',
            'mimeType': 'application/vnd.google-apps.document'
        }
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        return file.get('id')
    else:
        return items[0]['id']

def append_entry(service, document_id, entry_text):
    today = datetime.datetime.now().strftime("%A, %b %d, %Y")
    
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': f"{today}\n{entry_text}\n\n"
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': 1 + len(today)
                },
                'textStyle': {
                    'bold': True,
                    'fontSize': {
                        'magnitude': 12,
                        'unit': 'PT'
                    },
                    'weightedFontFamily': {
                        'fontFamily': 'Times New Roman'
                    }
                },
                'fields': 'bold,fontSize,weightedFontFamily'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1 + len(today) + 1,
                    'endIndex': 1 + len(today) + 1 + len(entry_text)
                },
                'textStyle': {
                    'bold': False,
                    'fontSize': {
                        'magnitude': 11,
                        'unit': 'PT'
                    },
                    'weightedFontFamily': {
                        'fontFamily': 'Times New Roman'
                    }
                },
                'fields': 'bold,fontSize,weightedFontFamily'
            }
        }
    ]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/submit', methods=['POST'])
def submit_entry():
    data = request.json
    entry = data.get('entry')

    if not entry:
        return jsonify({'error': 'No entry provided'}), 400

    try:
        creds = get_credentials()
        service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        doc_id = find_or_create_diary(service, drive_service)
        append_entry(service, doc_id, entry)

        return jsonify({'message': 'Entry saved successfully'})
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting server on http://localhost:5000")
    app.run(debug=True, port=5000)
