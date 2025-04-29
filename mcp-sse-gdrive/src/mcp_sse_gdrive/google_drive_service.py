# google_drive_service.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from typing import Optional, List
import os
import io
from datetime import datetime

# Define scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents'
]

class GoogleDriveService:
    def __init__(self, creds_file_path: str, token_path: str):
        """Initialize Google Drive service with authentication"""
        self.creds_file_path = creds_file_path
        self.token_path = token_path
        self.token = self._get_token()
        self.drive_service = build('drive', 'v3', credentials=self.token)
        self.sheets_service = build('sheets', 'v4', credentials=self.token)
        self.docs_service = build('docs', 'v1', credentials=self.token)

    def _get_token(self) -> Credentials:
        """Get or refresh Google API token"""
        token = None
        
        if os.path.exists(self.token_path):
            token = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not token or not token.valid:
            if token and token.expired and token.refresh_token:
                token.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_file_path, SCOPES)
                token = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token_file:
                token_file.write(token.to_json())

        return token

    async def search_files(self, query: str) -> List[dict]:
        """Search for files in Google Drive"""
        try:
            results = []
            page_token = None
            while True:
                response = self.drive_service.files().list(
                    q=query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, createdTime, modifiedTime)',
                    pageToken=page_token
                ).execute()

                results.extend(response.get('files', []))
                page_token = response.get('nextPageToken')
                if not page_token:
                    break

            return results
        except Exception as e:
            return {"error": str(e)}

    async def create_spreadsheet(self, title: str, data: Optional[List[List]] = None) -> dict:
        """Create a new Google Spreadsheet"""
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            spreadsheet_id = spreadsheet['spreadsheetId']
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            if data:
                range_name = 'Sheet1!A1'
                body = {
                    'values': data
                }
                self.sheets_service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
            
            return {
                "status": "success",
                "spreadsheet_id": spreadsheet_id,
                "url": spreadsheet_url,
                "message": f"Spreadsheet '{title}' created successfully"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def create_document(self, title: str, content: Optional[str] = None) -> dict:
        """Create a new Google Doc"""
        try:
            document = {
                'title': title
            }
            
            doc = self.docs_service.documents().create(body=document).execute()
            
            if content:
                requests = [{
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }]
                
                self.docs_service.documents().batchUpdate(
                    documentId=doc['documentId'],
                    body={'requests': requests}
                ).execute()
            
            return {
                "status": "success",
                "document_id": doc['documentId'],
                "message": f"Document '{title}' created successfully"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def read_spreadsheet(self, spreadsheet_id: str, range_name: str = 'Sheet1') -> dict:
        """Read content from a Google Spreadsheet"""
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            return {
                "status": "success",
                "values": result.get('values', []),
                "range": result.get('range')
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def read_document(self, document_id: str) -> dict:
        """Read content from a Google Doc"""
        try:
            document = self.docs_service.documents().get(
                documentId=document_id
            ).execute()
            
            return {
                "status": "success",
                "title": document.get('title'),
                "content": document.get('body'),
                "document_id": document_id
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def update_spreadsheet(self, spreadsheet_id: str, range_name: str, values: List[List]) -> dict:
        """Update content in a Google Spreadsheet"""
        try:
            body = {
                'values': values
            }
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return {
                "status": "success",
                "updated_cells": result.get('updatedCells'),
                "message": f"Updated {result.get('updatedCells')} cells"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def update_document(self, document_id: str, content: str) -> dict:
        """Update content in a Google Doc"""
        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            end_index = len(document.get('body').get('content', []))
            
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {
                            'index': 1
                        },
                        'text': content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return {
                "status": "success",
                "message": f"Document updated successfully"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}