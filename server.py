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
    
    # Get current document content to check for existing date
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body').get('content')
    
    has_todays_date = False
    if content:
        # Check the first paragraph (index 1 usually, index 0 is section break)
        # Content structure is list of StructuralElements. 
        # We look for the first paragraph's textRun.
        try:
            # Iterate through elements to find the first paragraph with text
            for element in content:
                if 'paragraph' in element:
                    elements = element.get('paragraph').get('elements')
                    for elem in elements:
                        if 'textRun' in elem:
                            text = elem.get('textRun').get('content')
                            if text.strip() == today:
                                has_todays_date = True
                                break
                    if has_todays_date:
                        break
        except Exception as e:
            print(f"Error checking date: {e}")

    requests = []
    
    if has_todays_date:
        # Find the end of the current day's section
        # We look for the next date header or the end of the document
        insert_index = -1
        
        try:
            # Start searching after the first paragraph (which is the date header)
            # content[0] is usually SectionBreak, content[1] is Date Header
            start_search_index = 2
            
            for i in range(start_search_index, len(content)):
                element = content[i]
                if 'paragraph' in element:
                    elements = element.get('paragraph').get('elements')
                    for elem in elements:
                        if 'textRun' in elem:
                            text = elem.get('textRun').get('content').strip()
                            # Check if this text looks like a date
                            try:
                                datetime.datetime.strptime(text, "%A, %b %d, %Y")
                                # Found a date! This is the start of the previous day.
                                insert_index = element.get('startIndex')
                                break
                            except ValueError:
                                # Not a date, continue searching
                                pass
                    if insert_index != -1:
                        break
            
            if insert_index == -1:
                # No other date found, insert at the end of the document
                # We want to insert before the final SectionBreak
                # content[-1] is usually the SectionBreak
                insert_index = content[-1].get('startIndex')

        except Exception as e:
            print(f"Error finding insert index: {e}")
            # Fallback: insert after date header if something goes wrong
            insert_index = 1 + len(today) + 1

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': insert_index,
                    },
                    'text': f"\n{entry_text}\n"
                }
            },
            {
                'updateTextStyle': {
                    'range': {
                        'startIndex': insert_index + 1, # +1 for the leading newline
                        'endIndex': insert_index + 1 + len(entry_text)
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
    else:
        # Insert new date header and entry at the top
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
