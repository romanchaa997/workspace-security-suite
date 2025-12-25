#!/usr/bin/env python3
"""
SIEM Integration Script

Integrates Google Workspace logs with SIEM systems (Splunk, Chronicle, FortiSIEM).
Supports real-time log streaming and alert generation.
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SIEMIntegrator:
    """Base class for SIEM integration."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_endpoint = config.get('api_endpoint')
        self.api_key = config.get('api_key')
        self.verify_ssl = config.get('verify_ssl', True)
    
    def send_logs(self, logs: List[Dict]) -> bool:
        """Send logs to SIEM system."""
        raise NotImplementedError
    
    def create_alert(self, alert_data: Dict) -> bool:
        """Create alert in SIEM system."""
        raise NotImplementedError

class SplunkIntegrator(SIEMIntegrator):
    """Splunk Enterprise Security integration."""
    
    def send_logs(self, logs: List[Dict]) -> bool:
        """Send logs to Splunk."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            for log in logs:
                response = requests.post(
                    f'{self.api_endpoint}/services/collector',
                    json={'event': log, 'sourcetype': 'google:workspace:audit'},
                    headers=headers,
                    verify=self.verify_ssl
                )
                response.raise_for_status()
            
            logger.info(f'Sent {len(logs)} logs to Splunk')
            return True
        except Exception as e:
            logger.error(f'Error sending logs to Splunk: {e}')
            return False
    
    def create_alert(self, alert_data: Dict) -> bool:
        """Create alert in Splunk."""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.post(
                f'{self.api_endpoint}/services/alerts',
                json=alert_data,
                headers=headers,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            logger.info('Alert created in Splunk')
            return True
        except Exception as e:
            logger.error(f'Error creating alert in Splunk: {e}')
            return False

class ChronicleIntegrator(SIEMIntegrator):
    """Google Chronicle SIEM integration."""
    
    def send_logs(self, logs: List[Dict]) -> bool:
        """Send logs to Google Chronicle."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'logEntries': [
                    {
                        'severity': log.get('severity', 'LOW'),
                        'logMessage': json.dumps(log),
                        'logSourceRegion': log.get('region', 'global')
                    } for log in logs
                ]
            }
            
            response = requests.post(
                f'{self.api_endpoint}/v1/events:batchCreate',
                json=payload,
                headers=headers,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            logger.info(f'Sent {len(logs)} logs to Google Chronicle')
            return True
        except Exception as e:
            logger.error(f'Error sending logs to Chronicle: {e}')
            return False
    
    def create_alert(self, alert_data: Dict) -> bool:
        """Create alert in Chronicle."""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.post(
                f'{self.api_endpoint}/v1/alerts',
                json=alert_data,
                headers=headers,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            logger.info('Alert created in Google Chronicle')
            return True
        except Exception as e:
            logger.error(f'Error creating alert in Chronicle: {e}')
            return False

class FortiSIEMIntegrator(SIEMIntegrator):
    """FortiSIEM integration."""
    
    def send_logs(self, logs: List[Dict]) -> bool:
        """Send logs to FortiSIEM."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.api_endpoint}/api/events/custom',
                json={'events': logs},
                headers=headers,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            logger.info(f'Sent {len(logs)} logs to FortiSIEM')
            return True
        except Exception as e:
            logger.error(f'Error sending logs to FortiSIEM: {e}')
            return False
    
    def create_alert(self, alert_data: Dict) -> bool:
        """Create alert in FortiSIEM."""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.post(
                f'{self.api_endpoint}/api/alerts',
                json=alert_data,
                headers=headers,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            logger.info('Alert created in FortiSIEM')
            return True
        except Exception as e:
            logger.error(f'Error creating alert in FortiSIEM: {e}')
            return False

def get_siem_integrator(siem_type: str, config: Dict) -> SIEMIntegrator:
    """Factory function to get appropriate SIEM integrator."""
    integrators = {
        'splunk': SplunkIntegrator,
        'chronicle': ChronicleIntegrator,
        'fortisiem': FortiSIEMIntegrator
    }
    
    integrator_class = integrators.get(siem_type.lower())
    if not integrator_class:
        raise ValueError(f'Unknown SIEM type: {siem_type}')
    
    return integrator_class(config)

if __name__ == '__main__':
    config = {
        'api_endpoint': 'https://siem.example.com',
        'api_key': 'your-api-key',
        'verify_ssl': True
    }
    
    integrator = get_siem_integrator('splunk', config)
    print('SIEM integrator initialized successfully')
