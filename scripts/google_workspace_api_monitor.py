#!/usr/bin/env python3
"""
Google Workspace API Monitor

Monitors Google Workspace for security events, audit logs, and user activities.
Provides real-time alerting and compliance reporting.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.apis.admin import directory_v1
from google.apis.reports import reports_v1
from google.apis.drive import drive_v3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoogleWorkspaceMonitor:
    """Monitor Google Workspace security events and activities."""
    
    def __init__(self, service_account_file):
        """Initialize the monitor with service account credentials."""
        self.credentials = self._load_credentials(service_account_file)
        self.directory_service = self._build_service('admin', 'directory_v1')
        self.reports_service = self._build_service('admin', 'reports_v1')
        self.drive_service = self._build_service('drive', 'v3')
    
    def _load_credentials(self, service_account_file):
        """Load service account credentials."""
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(f"Service account file not found: {service_account_file}")
        
        scopes = [
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/admin.directory.group',
            'https://www.googleapis.com/auth/admin.reports.audit.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        credentials = Credentials.from_service_account_file(
            service_account_file,
            scopes=scopes
        )
        return credentials
    
    def _build_service(self, api_name, api_version):
        """Build API service object."""
        from googleapiclient.discovery import build
        return build(api_name, api_version, credentials=self.credentials)
    
    def get_audit_logs(self, start_date=None, max_results=100):
        """Retrieve audit logs from Google Workspace."""
        if not start_date:
            start_date = (datetime.now() - timedelta(hours=24)).isoformat()
        
        try:
            results = self.reports_service.activities().list(
                userKey='all',
                applicationName='admin',
                startTime=start_date,
                maxResults=max_results
            ).execute()
            
            activities = results.get('activities', [])
            logger.info(f"Retrieved {len(activities)} audit log entries")
            return activities
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []
    
    def check_mfa_status(self):
        """Check MFA status for all users."""
        try:
            results = self.directory_service.users().list(
                customer='my_customer',
                maxResults=500
            ).execute()
            
            users = results.get('users', [])
            mfa_enabled_count = sum(1 for u in users if u.get('twoStepVerificationEnrolled'))
            total_users = len(users)
            
            logger.info(f"MFA Status: {mfa_enabled_count}/{total_users} users have MFA enabled")
            return {
                'total_users': total_users,
                'mfa_enabled': mfa_enabled_count,
                'mfa_disabled': total_users - mfa_enabled_count,
                'percentage': round((mfa_enabled_count / total_users) * 100, 2) if total_users > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error checking MFA status: {e}")
            return {}
    
    def monitor_security_events(self):
        """Monitor for security-related events."""
        security_events = []
        
        # Get recent audit logs
        logs = self.get_audit_logs()
        
        # Filter for security-relevant events
        security_event_types = [
            'login_failure',
            'login_success_unusual_location',
            'password_change',
            'admin_grant',
            'admin_revoke',
            'create_user',
            'delete_user'
        ]
        
        for log in logs:
            events = log.get('events', [])
            for event in events:
                event_type = event.get('type')
                if any(sec_type in str(event_type) for sec_type in security_event_types):
                    security_events.append({
                        'timestamp': log.get('id', {}).get('time'),
                        'actor': log.get('actor', {}).get('email'),
                        'event_type': event_type,
                        'event_name': event.get('name')
                    })
        
        logger.info(f"Found {len(security_events)} security events")
        return security_events
    
    def generate_report(self):
        """Generate comprehensive security report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'mfa_status': self.check_mfa_status(),
            'security_events': self.monitor_security_events(),
            'audit_logs': self.get_audit_logs()
        }
        
        # Save report to file
        report_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report generated: {report_file}")
        return report

def main():
    """Main execution function."""
    service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
    
    monitor = GoogleWorkspaceMonitor(service_account_file)
    report = monitor.generate_report()
    
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
