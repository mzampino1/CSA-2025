from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

# If modifying scopes, delete token.json first
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token.json'

# Load token if it exists
if os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
else:
    # If no valid credentials, prompt user to log in
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, 'w') as token_file:
        token_file.write(creds.to_json())

drive_service = build('drive', 'v3', credentials=creds)

from googleapiclient.http import MediaFileUpload

def upload_and_convert_to_gdoc(local_path: str, name: str, folder_id: str):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    media = MediaFileUpload(local_path,
                            mimetype='text/plain',  # <-- for .txt files
                            resumable=True)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    print(f"Uploaded and converted file '{name}' to Google Doc. File ID: {file.get('id')}")

# Generate a unique filename by checking existing files in the folder
def get_next_filename(base_name: str, folder_id: str) -> str:
    query = f"name contains '{base_name}' and '{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(name)").execute()
    existing_files = [file['name'] for file in results.get('files', [])]
    
    count = 1
    while True:
        new_name = f"{base_name} {count}"
        if new_name not in existing_files:
            return new_name
        count += 1

# Example usage:
if(__name__ == "__main__"):
    FOLDER_ID = '1E7B_7nETIwOohQWAuya2JCwTHsqlG37F'
    file_name = get_next_filename('Prompt', FOLDER_ID)
    upload_and_convert_to_gdoc(r'chatLogger\response.txt', file_name, FOLDER_ID)