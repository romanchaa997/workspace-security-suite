"""Pytest configuration and fixtures for Workspace Security Suite tests"""

import pytest
import json
from unittest.mock import Mock, MagicMock


@pytest.fixture
def api_client():
    """Fixture providing a mock API client"""
    client = MagicMock()
    client.authenticate.return_value = True
    client.get_users.return_value = [{"id": "user_001", "email": "test@example.com"}]
    return client


@pytest.fixture
def siem_config():
    """Fixture providing SIEM configuration"""
    return {
        "platform": "splunk",
        "host": "splunk.example.com",
        "port": 8088,
        "token": "test_token_123",
    }


@pytest.fixture
def test_user():
    """Fixture providing a test user object"""
    return {
        "id": "user_001",
        "email": "test@example.com",
        "name": "Test User",
        "status": "ACTIVE",
        "created_time": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def test_event():
    """Fixture providing a test event object"""
    return {
        "id": "evt_001",
        "type": "user_login",
        "timestamp": "2024-12-25T10:00:00Z",
        "actor": "user@example.com",
        "resource": "Gmail",
        "severity": "low",
    }


@pytest.fixture
def mock_workspace_api():
    """Fixture providing a complete mock Workspace API"""
    api = MagicMock()
    api.list_users.return_value = [
        {"id": "user_001", "email": "test1@example.com"},
        {"id": "user_002", "email": "test2@example.com"},
    ]
    api.list_groups.return_value = [
        {"id": "group_001", "email": "devs@example.com"},
    ]
    api.get_audit_logs.return_value = []
    return api


@pytest.fixture
def sample_audit_logs():
    """Fixture providing sample audit logs"""
    return [
        {
            "id": "evt_001",
            "type": "user_login",
            "timestamp": "2024-12-25T10:00:00Z",
            "actor": "user@example.com",
        },
        {
            "id": "evt_002",
            "type": "file_shared",
            "timestamp": "2024-12-25T10:15:00Z",
            "actor": "admin@example.com",
        },
    ]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "security: mark test as security test")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook for test result reporting"""
    outcome = yield
    result = outcome.get_result()


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers"""
    for item in items:
        if "test_" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
