#!/usr/bin/env python3
"""
Microsoft Graph API Integration Example
Demonstrates how to integrate with Microsoft 365 services via Graph API
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient


class MicrosoftGraphIntegration:
    """Integration client for Microsoft Graph API"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        scopes: Optional[List[str]] = None,
    ):
        """Initialize Microsoft Graph client with credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.scopes = scopes or ["https://graph.microsoft.com/.default"]

        # Initialize credential
        self.credential = ClientSecretCredential(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )

        # Initialize Graph client
        self.client = GraphClient(credential=self.credential)

    def get_users(self, filter_query: Optional[str] = None) -> List[Dict]:
        """Get list of users from Azure AD"""
        try:
            endpoint = "/users"
            query_params = {}

            if filter_query:
                query_params["$filter"] = filter_query

            query_params["$select"] = "id,displayName,mail,userPrincipalName,accountEnabled"

            response = self.client.get(endpoint, params=query_params)
            return response.json().get("value", [])
        except Exception as e:
            print(f"Error fetching users: {str(e)}")
            return []

    def get_security_alerts(self, days_back: int = 7) -> List[Dict]:
        """Get security alerts from the last N days"""
        try:
            since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            filter_query = f"createdDateTime gt {since_date}Z"

            endpoint = "/security/alerts_v2"
            query_params = {
                "$filter": filter_query,
                "$select": "id,createdDateTime,title,severity,category,status",
                "$top": 100,
            }

            response = self.client.get(endpoint, params=query_params)
            return response.json().get("value", [])
        except Exception as e:
            print(f"Error fetching security alerts: {str(e)}")
            return []

    def get_audit_logs(
        self, activity_type: Optional[str] = None, days_back: int = 7
    ) -> List[Dict]:
        """Get audit logs from Directory"""
        try:
            since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            filter_parts = [f"activityDateTime gt {since_date}Z"]

            if activity_type:
                filter_parts.append(f"activityDisplayName eq '{activity_type}'")

            filter_query = " and ".join(filter_parts)

            endpoint = "/auditLogs/directoryAudits"
            query_params = {
                "$filter": filter_query,
                "$select": "id,activityDateTime,activityDisplayName,result,userDisplayName,targetResources",
                "$top": 100,
            }

            response = self.client.get(endpoint, params=query_params)
            return response.json().get("value", [])
        except Exception as e:
            print(f"Error fetching audit logs: {str(e)}")
            return []

    def get_device_compliance_status(self) -> List[Dict]:
        """Get device compliance status for Intune managed devices"""
        try:
            endpoint = "/deviceManagement/deviceCompliancePolicies"
            query_params = {
                "$select": "id,displayName,createdDateTime,lastModifiedDateTime"
            }

            response = self.client.get(endpoint, params=query_params)
            return response.json().get("value", [])
        except Exception as e:
            print(f"Error fetching device compliance: {str(e)}")
            return []

    def get_conditional_access_policies(self) -> List[Dict]:
        """Get Conditional Access policies"""
        try:
            endpoint = "/identity/conditionalAccess/policies"
            query_params = {
                "$select": "id,displayName,createdDateTime,state,conditions"
            }

            response = self.client.get(endpoint, params=query_params)
            return response.json().get("value", [])
        except Exception as e:
            print(f"Error fetching CA policies: {str(e)}")
            return []

    def check_mfa_status(self, user_id: str) -> Dict:
        """Check MFA status for a specific user"""
        try:
            endpoint = f"/users/{user_id}/authentication/methods"

            response = self.client.get(endpoint)
            methods = response.json().get("value", [])

            mfa_methods = [m for m in methods if m["@odata.type"] != "#microsoft.graph.passwordAuthenticationMethod"]

            return {"user_id": user_id, "mfa_enabled": len(mfa_methods) > 0, "methods": mfa_methods}
        except Exception as e:
            print(f"Error checking MFA status: {str(e)}")
            return {"user_id": user_id, "mfa_enabled": False, "error": str(e)}


def main():
    """Example usage of Microsoft Graph integration"""
    # Load credentials from environment variables
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")

    if not all([client_id, client_secret, tenant_id]):
        print("Error: Missing required Azure credentials in environment variables")
        return

    # Initialize Graph integration
    graph = MicrosoftGraphIntegration(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
    )

    # Get users
    print("\n=== Getting Users ===")
    users = graph.get_users()
    print(f"Found {len(users)} users")
    for user in users[:5]:  # Print first 5
        print(f"  - {user.get('displayName')} ({user.get('mail')})")

    # Get security alerts
    print("\n=== Getting Security Alerts ===")
    alerts = graph.get_security_alerts(days_back=7)
    print(f"Found {len(alerts)} alerts in last 7 days")
    for alert in alerts[:3]:  # Print first 3
        print(f"  - {alert.get('title')} (Severity: {alert.get('severity')})")

    # Get audit logs
    print("\n=== Getting Audit Logs ===")
    audit_logs = graph.get_audit_logs(days_back=7)
    print(f"Found {len(audit_logs)} audit events in last 7 days")
    for log in audit_logs[:3]:  # Print first 3
        print(f"  - {log.get('activityDisplayName')} by {log.get('userDisplayName')}")

    # Get device compliance
    print("\n=== Getting Device Compliance ===")
    compliance = graph.get_device_compliance_status()
    print(f"Found {len(compliance)} compliance policies")

    # Get Conditional Access policies
    print("\n=== Getting Conditional Access Policies ===")
    ca_policies = graph.get_conditional_access_policies()
    print(f"Found {len(ca_policies)} CA policies")


if __name__ == "__main__":
    main()
