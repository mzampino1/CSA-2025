from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete token.json first
SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

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
    print(f"Uploaded and converted to Google Doc. File ID: {file.get('id')}")

# Example usage:
FOLDER_ID = '1E7B_7nETIwOohQWAuya2JCwTHsqlG37F'
upload_and_convert_to_gdoc('yourfile.txt', 'My Google Doc', FOLDER_ID)
