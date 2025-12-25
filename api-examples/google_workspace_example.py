#!/usr/bin/env python3
"""
Google Workspace API Integration Example
Demonstrates how to integrate with Google Workspace APIs
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleWorkspaceAPIExample:
    """Example integration with Google Workspace APIs"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/admin.directory.user',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self, credentials_file='credentials.json'):
        self.credentials_file = credentials_file
        self.credentials = None
        self.admin_service = None
        self.gmail_service = None
        self.drive_service = None
    
    def authenticate(self):
        """Authenticate with Google APIs"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES)
            self.credentials = flow.run_local_server(port=0)
            logger.info("Authentication successful")
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
    
    def list_users(self, customer='my_customer', max_results=10):
        """List users in the organization"""
        try:
            if not self.admin_service:
                self.admin_service = build('admin', 'directory_v1',
                                          credentials=self.credentials)
            
            results = self.admin_service.users().list(
                customer=customer,
                maxResults=max_results,
                orderBy='email'
            ).execute()
            
            users = results.get('users', [])
            logger.info(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Failed to list users: {str(e)}")
            return []
    
    def get_user(self, user_key):
        """Get specific user details"""
        try:
            if not self.admin_service:
                self.admin_service = build('admin', 'directory_v1',
                                          credentials=self.credentials)
            
            user = self.admin_service.users().get(userKey=user_key).execute()
            logger.info(f"Retrieved user: {user.get('primaryEmail')}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    example = GoogleWorkspaceAPIExample()
    example.authenticate()
    users = example.list_users()
    for user in users[:5]:
        print(f"User: {user.get('primaryEmail')}")
