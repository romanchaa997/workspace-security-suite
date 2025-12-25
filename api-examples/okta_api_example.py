#!/usr/bin/env python3
"""
Okta API Integration Example
Demonstrates how to integrate with Okta for identity and access management
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class OktaIntegration:
    """Integration client for Okta API"""

    def __init__(self, org_url: str, api_token: str):
        """Initialize Okta client with credentials"""
        self.org_url = org_url.rstrip("/")
        self.api_token = api_token
        self.base_url = f"{self.org_url}/api/v1"
        self.headers = {
            "Authorization": f"SSWS {api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[Dict]:
        """Make HTTP request to Okta API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(
                method, url, headers=self.headers, **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {str(e)}")
            return None

    def list_users(
        self, filter_query: Optional[str] = None, limit: int = 20
    ) -> List[Dict]:
        """List all users in Okta"""
        try:
            params = {"limit": limit}
            if filter_query:
                params["filter"] = filter_query

            response = self._request("GET", "/users", params=params)
            return response if response else []
        except Exception as e:
            print(f"Error listing users: {str(e)}")
            return []

    def get_user_details(self, user_id: str) -> Optional[Dict]:
        """Get detailed information for a specific user"""
        try:
            return self._request("GET", f"/users/{user_id}")
        except Exception as e:
            print(f"Error getting user details: {str(e)}")
            return None

    def list_user_groups(self, user_id: str) -> List[Dict]:
        """Get list of groups for a user"""
        try:
            response = self._request("GET", f"/users/{user_id}/groups")
            return response if response else []
        except Exception as e:
            print(f"Error listing user groups: {str(e)}")
            return []

    def get_user_activities(
        self, user_id: str, days_back: int = 7
    ) -> List[Dict]:
        """Get activity log for a user"""
        try:
            since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            params = {
                "since": f"{since_date}Z",
                "limit": 100,
            }
            response = self._request(
                "GET", f"/users/{user_id}/logs", params=params
            )
            return response if response else []
        except Exception as e:
            print(f"Error getting user activities: {str(e)}")
            return []

    def list_mfa_devices(self, user_id: str) -> List[Dict]:
        """List MFA devices for a user"""
        try:
            response = self._request(
                "GET", f"/users/{user_id}/factors"
            )
            return response if response else []
        except Exception as e:
            print(f"Error listing MFA devices: {str(e)}")
            return []

    def list_applications(self, limit: int = 20) -> List[Dict]:
        """List all applications in the organization"""
        try:
            params = {"limit": limit}
            response = self._request("GET", "/apps", params=params)
            return response if response else []
        except Exception as e:
            print(f"Error listing applications: {str(e)}")
            return []

    def get_app_users(self, app_id: str, limit: int = 20) -> List[Dict]:
        """Get users assigned to an application"""
        try:
            params = {"limit": limit}
            response = self._request(
                "GET", f"/apps/{app_id}/users", params=params
            )
            return response if response else []
        except Exception as e:
            print(f"Error getting app users: {str(e)}")
            return []

    def list_groups(self, limit: int = 20) -> List[Dict]:
        """List all groups in the organization"""
        try:
            params = {"limit": limit}
            response = self._request("GET", "/groups", params=params)
            return response if response else []
        except Exception as e:
            print(f"Error listing groups: {str(e)}")
            return []

    def get_group_members(self, group_id: str, limit: int = 20) -> List[Dict]:
        """Get members of a group"""
        try:
            params = {"limit": limit}
            response = self._request(
                "GET", f"/groups/{group_id}/users", params=params
            )
            return response if response else []
        except Exception as e:
            print(f"Error getting group members: {str(e)}")
            return []

    def get_security_events(
        self, days_back: int = 7, limit: int = 100
    ) -> List[Dict]:
        """Get security/audit events from system log"""
        try:
            since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            params = {
                "since": f"{since_date}Z",
                "limit": limit,
            }
            response = self._request("GET", "/logs", params=params)
            return response if response else []
        except Exception as e:
            print(f"Error getting security events: {str(e)}")
            return []

    def list_network_zones(self) -> List[Dict]:
        """List network zones"""
        try:
            response = self._request("GET", "/zones")
            return response if response else []
        except Exception as e:
            print(f"Error listing network zones: {str(e)}")
            return []

    def get_org_info(self) -> Optional[Dict]:
        """Get organization information"""
        try:
            return self._request("GET", "")
        except Exception as e:
            print(f"Error getting org info: {str(e)}")
            return None


def main():
    """Example usage of Okta integration"""
    # Load credentials from environment variables
    org_url = os.getenv("OKTA_ORG_URL")
    api_token = os.getenv("OKTA_API_TOKEN")

    if not all([org_url, api_token]):
        print("Error: Missing required Okta credentials in environment variables")
        print("Set OKTA_ORG_URL and OKTA_API_TOKEN")
        return

    # Initialize Okta integration
    okta = OktaIntegration(org_url=org_url, api_token=api_token)

    # Get organization info
    print("\n=== Organization Information ===")
    org_info = okta.get_org_info()
    if org_info:
        print(f"Organization: {org_info.get('org', {}).get('name')}")

    # List users
    print("\n=== Users ===")
    users = okta.list_users(limit=10)
    print(f"Found {len(users)} users")
    for user in users[:5]:
        print(f"  - {user.get('profile', {}).get('login')}")

    # List groups
    print("\n=== Groups ===")
    groups = okta.list_groups(limit=10)
    print(f"Found {len(groups)} groups")
    for group in groups[:5]:
        print(f"  - {group.get('profile', {}).get('name')}")

    # List applications
    print("\n=== Applications ===")
    apps = okta.list_applications(limit=10)
    print(f"Found {len(apps)} applications")
    for app in apps[:5]:
        print(f"  - {app.get('name')}")

    # Get security events
    print("\n=== Recent Security Events ===")
    events = okta.get_security_events(days_back=7, limit=10)
    print(f"Found {len(events)} security events in last 7 days")
    for event in events[:3]:
        print(f"  - {event.get('eventType')} at {event.get('published')}")

    # List network zones
    print("\n=== Network Zones ===")
    zones = okta.list_network_zones()
    print(f"Found {len(zones)} network zones")
    for zone in zones[:5]:
        print(f"  - {zone.get('name')} ({zone.get('type')})")


if __name__ == "__main__":
    main()
