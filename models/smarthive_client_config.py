# -*- coding: utf-8 -*-

import json
import logging
import requests
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, UserError, ValidationError

_logger = logging.getLogger(__name__)


class SmartHiveClientConfig(models.Model):
    _name = 'smarthive.client.config'
    _description = 'SmartHive Client Configuration'
    
    name = fields.Char(
        string='Configuration Name',
        default='SmartHive Client Config',
        required=True
    )
    
    server_url = fields.Char(
        string='SmartHive Server URL',
        required=True,
        help='URL of the SmartHive server instance (Odoo 18 EE)'
    )
    
    client_id = fields.Char(
        string='Client ID',
        required=True,
        help='Unique client identifier configured on the server'
    )
    
    api_key = fields.Char(
        string='API Key',
        required=True,
        help='API key for authentication with server'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    # Status fields
    is_blocked = fields.Boolean(
        string='Client Blocked',
        default=False,
        help='Whether this client is currently blocked by the server'
    )
    
    block_reason = fields.Text(
        string='Block Reason',
        help='Reason provided by server for blocking'
    )
    
    show_warning = fields.Boolean(
        string='Show Warning Banner',
        default=False,
        help='Show warning banner to users'
    )
    
    warning_message = fields.Text(
        string='Warning Message',
        help='Warning message from server to display'
    )
    
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('pending', 'Pending Payment'),
        ('overdue', 'Overdue'),
        ('blocked', 'Payment Blocked')
    ], string='Payment Status', default='paid')
    
    outstanding_amount = fields.Float(
        string='Outstanding Amount',
        help='Outstanding payment amount from server'
    )
    
    last_server_contact = fields.Datetime(
        string='Last Server Contact',
        help='Last successful communication with server'
    )
    
    heartbeat_interval = fields.Integer(
        string='Heartbeat Interval (minutes)',
        default=15,
        help='How often to send heartbeat to server'
    )
    
    auto_report_status = fields.Boolean(
        string='Auto Report Status',
        default=True,
        help='Automatically report status to server'
    )

    @api.constrains('server_url')
    def _check_server_url_format(self):
        """Validate server URL format"""
        for record in self:
            if record.server_url:
                if not (record.server_url.startswith('http://') or record.server_url.startswith('https://')):
                    raise ValidationError(_('Server URL must start with http:// or https://'))

    def _get_api_headers(self):
        """Get headers for API requests to server"""
        return {
            'Content-Type': 'application/json',
            'X-SmartHive-API-Key': self.api_key,
            'X-SmartHive-Client-ID': self.client_id,
        }

    def _make_server_request(self, endpoint, method='POST', data=None):
        """Make API request to SmartHive server"""
        try:
            url = f"{self.server_url.rstrip('/')}/smarthive/api/{endpoint}"
            headers = self._get_api_headers()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                # For Odoo JSON endpoints, we need to send data as JSON in the request body
                response = requests.post(url, headers=headers, data=json.dumps(data or {}), timeout=30)
            
            response.raise_for_status()
            
            # Handle different response types
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {'success': False, 'error': 'Invalid JSON response from server'}
            else:
                return {'success': False, 'error': 'Empty response from server'}
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Cannot connect to server at {self.server_url}: {str(e)}"
            _logger.error(f"Connection error: {error_msg}")
            return {'success': False, 'error': error_msg}
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timeout (30s) to server: {str(e)}"
            _logger.error(f"Timeout error: {error_msg}")
            return {'success': False, 'error': error_msg}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error {e.response.status_code}: {str(e)}"
            _logger.error(f"HTTP error: {error_msg}")
            return {'success': False, 'error': error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            _logger.error(f"Server request failed: {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            _logger.error(f"Unexpected error in server request: {error_msg}")
            return {'success': False, 'error': error_msg}

    def action_test_connection(self):
        """Test connection to SmartHive server"""
        self.ensure_one()
        
        # Validate configuration first
        if not self.server_url:
            raise UserError(_("Please configure the server URL first"))
        if not self.api_key:
            raise UserError(_("Please configure the API key first"))
        if not self.client_id:
            raise UserError(_("Please configure the client ID first"))
            
        # Send heartbeat to test connection
        result = self.send_heartbeat()
        if result.get('success'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _('Successfully connected to SmartHive server'),
                    'type': 'success',
                }
            }
        else:
            error_message = result.get('error', 'Unknown error')
            raise UserError(_("Connection test failed: %s") % error_message)

    def send_heartbeat(self):
        """Send heartbeat to server and get current status"""
        try:
            data = {
                'odoo_version': self.env['ir.module.module'].get_module_info('base').get('version', 'Unknown'),
                'addon_version': '17.0.1.0.0',
                'timestamp': fields.Datetime.now().isoformat(),
                'users_count': self.env['res.users'].search_count([]),
                'companies_count': self.env['res.company'].search_count([]),
            }
            
            result = self._make_server_request('client/heartbeat', data=data)
            
            if result.get('success'):
                # Update local status based on server response
                self.write({
                    'is_blocked': result.get('blocked', False),
                    'block_reason': result.get('block_reason', ''),
                    'show_warning': result.get('show_warning', False),
                    'warning_message': result.get('warning_message', ''),
                    'payment_status': result.get('payment_status', 'paid'),
                    'last_server_contact': fields.Datetime.now(),
                })
                
                # Log status update
                self.env['smarthive.client.status'].create({
                    'status_type': 'heartbeat',
                    'status': 'success',
                    'message': 'Heartbeat successful',
                    'details': json.dumps(result),
                })
            
            return result
            
        except Exception as e:
            _logger.error(f"Heartbeat failed: {str(e)}")
            # Log failed heartbeat
            self.env['smarthive.client.status'].create({
                'status_type': 'heartbeat',
                'status': 'error',
                'message': f'Heartbeat failed: {str(e)}',
            })
            return {'success': False, 'error': str(e)}

    def send_status_update(self, status_data):
        """Send status update to server"""
        try:
            result = self._make_server_request('client/status', data=status_data)
            
            if result.get('success'):
                self.last_server_contact = fields.Datetime.now()
                
            return result
            
        except Exception as e:
            _logger.error(f"Status update failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    @api.model
    def cron_heartbeat(self):
        """Cron job to send regular heartbeat to server"""
        configs = self.search([
            ('active', '=', True),
            ('server_url', '!=', False),
            ('client_id', '!=', False),
            ('api_key', '!=', False),
        ])
        
        for config in configs:
            try:
                # Check if it's time for heartbeat
                if (not config.last_server_contact or 
                    (fields.Datetime.now() - config.last_server_contact).total_seconds() >= config.heartbeat_interval * 60):
                    config.send_heartbeat()
            except Exception as e:
                _logger.error(f"Cron heartbeat failed for config {config.id}: {str(e)}")

    @api.model
    def get_active_config(self):
        """Get active SmartHive configuration"""
        return self.search([('active', '=', True)], limit=1)

    def _check_access_allowed(self):
        """Check if user access is allowed (not blocked)"""
        if self.is_blocked:
            return False
        return True

    def get_warning_data(self):
        """Get current warning data for display"""
        if not self.show_warning:
            return None
            
        return {
            'show_warning': True,
            'message': self.warning_message or 'System notification from administrator',
            'payment_status': self.payment_status,
            'outstanding_amount': self.outstanding_amount,
            'block_reason': self.block_reason if self.is_blocked else None,
        }