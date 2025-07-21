from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import logging
import os

class UploadToDrive(): 
    def __init__(self, answers, drive_folder_id):
        # If modifying scopes, delete token.json first
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.TOKEN_PATH = 'token.json'
        self.answers = answers
        self.drive_folder_id = drive_folder_id

    def get_drive_service(self):
        # Load token if it exists
        if os.path.exists(self.TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(self.TOKEN_PATH, self.SCOPES)
        else:
            # If no valid credentials, prompt user to log in
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
            creds = flow.run_local_server(port=0)
            with open(self.TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())

        drive_service = build('drive', 'v3', credentials=creds)
        return drive_service

    def upload_and_convert_to_gdoc(self, path: str, name: str, folder_id: str, drive_service: str):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id]
        }
        media = MediaFileUpload(path,
                                mimetype='text/plain',  # <-- for .txt files
                                resumable=True)
        file = drive_service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        print(f"Uploaded and converted file '{name}' to Google Doc. File ID: {file.get('id')}")

    # Generate a unique filename by checking existing files in the folder
    def get_next_filename(self, base_name: str, folder_id: str, drive_service: str) -> str:
        query = f"name contains '{base_name}' and '{folder_id}' in parents and trashed = false"
        results = drive_service.files().list(q=query, fields="files(name)").execute()
        existing_files = [file['name'] for file in results.get('files', [])]
        
        count = 1
        while True:
            new_name = f"{base_name} {count}"
            if new_name not in existing_files:
                return new_name
            count += 1

    def upload_answers(self):
        if not self.answers:
            logging.error("No answers to upload.")
            return

        file_name = "response.txt"
        file_path = os.path.join(os.getcwd(), file_name)
        drive_service = self.get_drive_service()

        initial_doc_name = self.get_next_filename("Prompt", self.drive_folder_id, drive_service)
        initial_doc_num = int(initial_doc_name.split("Prompt ")[-1]) if initial_doc_name else 1

        cnt = 0
        for answer in self.answers:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(answer)

            self.upload_and_convert_to_gdoc(
                path=file_path,
                name=f"Prompt {initial_doc_num + cnt}",
                folder_id= self.drive_folder_id,
                drive_service=drive_service,
            )
            cnt += 1
            os.remove(file_path)


"""
# Example usage:
if(__name__ == "__main__"):
    FOLDER_ID = '1E7B_7nETIwOohQWAuya2JCwTHsqlG37F'
    file_name = get_next_filename('Prompt', FOLDER_ID)
    upload_and_convert_to_gdoc(r'chatLogger\response.txt', file_name, FOLDER_ID)
"""