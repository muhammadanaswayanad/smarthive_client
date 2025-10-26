# -*- coding: utf-8 -*-

import json
import logging
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)

# Constants
CLIENT_CONFIG_MODEL = 'smarthive.client.config'
CLIENT_STATUS_MODEL = 'smarthive.client.status'


class SmartHiveClientController(http.Controller):
    
    def _authenticate_request(self):
        """Authenticate API request from SmartHive server"""
        api_key = request.httprequest.headers.get('X-SmartHive-API-Key')
        client_id = request.httprequest.headers.get('X-SmartHive-Client-ID')
        
        if not api_key or not client_id:
            return False, "Missing API key or client ID"
        
        config = request.env[CLIENT_CONFIG_MODEL].sudo().search([
            ('client_id', '=', client_id),
            ('api_key', '=', api_key),
            ('active', '=', True)
        ], limit=1)
        
        if not config:
            return False, "Invalid API credentials"
            
        return config, None


class SmartHiveServerController(http.Controller):
    """Controller for server-to-client API endpoints"""
    
    def _authenticate_request(self):
        """Authenticate API request from SmartHive server"""
        api_key = request.httprequest.headers.get('X-SmartHive-API-Key')
        client_id = request.httprequest.headers.get('X-SmartHive-Client-ID')
        
        if not api_key or not client_id:
            return False, "Missing API key or client ID"
        
        config = request.env[CLIENT_CONFIG_MODEL].sudo().search([
            ('client_id', '=', client_id),
            ('api_key', '=', api_key),
            ('active', '=', True)
        ], limit=1)
        
        if not config:
            return False, "Invalid API credentials"
            
        return config, None

    @http.route('/smarthive_client/ping', type='json', auth='none', methods=['GET'], csrf=False)
    def ping(self):
        """Health check endpoint"""
        try:
            _, error = self._authenticate_request()
            if error:
                return {'success': False, 'error': error}
            
            return {
                'success': True,
                'odoo_version': request.env['ir.module.module'].get_module_info('base').get('version', 'Unknown'),
                'addon_version': '17.0.1.0.0',
                'timestamp': fields.Datetime.now().isoformat(),
            }
            
        except Exception as e:
            _logger.error(f"Ping endpoint error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/smarthive_client/block', type='json', auth='none', methods=['POST'], csrf=False)
    def block_client(self):
        """Block client access"""
        try:
            config, error = self._authenticate_request()
            if error:
                return {'success': False, 'error': error}
            
            data = request.jsonrequest
            
            config.sudo().write({
                'is_blocked': data.get('blocked', True),
                'block_reason': data.get('block_reason', 'Blocked by administrator'),
            })
            
            # Log the block action
            request.env[CLIENT_STATUS_MODEL].sudo().create({
                'status_type': 'block',
                'status': 'warning',
                'message': f"Client access blocked: {data.get('block_reason', 'No reason provided')}",
            })
            
            return {'success': True}
            
        except Exception as e:
            _logger.error(f"Block client error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/smarthive_client/unblock', type='json', auth='none', methods=['POST'], csrf=False)
    def unblock_client(self):
        """Unblock client access"""
        try:
            config, error = self._authenticate_request()
            if error:
                return {'success': False, 'error': error}
            
            config.sudo().write({
                'is_blocked': False,
                'block_reason': '',
            })
            
            # Log the unblock action
            request.env[CLIENT_STATUS_MODEL].sudo().create({
                'status_type': 'block',
                'status': 'success',
                'message': "Client access unblocked",
            })
            
            return {'success': True}
            
        except Exception as e:
            _logger.error(f"Unblock client error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/smarthive_client/warning', type='json', auth='none', methods=['POST'], csrf=False)
    def set_warning(self):
        """Set warning banner configuration"""
        try:
            config, error = self._authenticate_request()
            if error:
                return {'success': False, 'error': error}
            
            data = request.jsonrequest
            
            config.sudo().write({
                'show_warning': data.get('show_warning', False),
                'warning_message': data.get('warning_message', ''),
                'payment_status': data.get('payment_status', 'paid'),
                'outstanding_amount': data.get('outstanding_amount', 0.0),
            })
            
            # Log the warning action
            request.env[CLIENT_STATUS_MODEL].sudo().create({
                'status_type': 'warning',
                'status': 'info',
                'message': f"Warning banner {'enabled' if data.get('show_warning') else 'disabled'}",
                'details': json.dumps(data),
            })
            
            return {'success': True}
            
        except Exception as e:
            _logger.error(f"Set warning error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/smarthive_client/status', type='json', auth='none', methods=['GET'], csrf=False)
    def get_status(self):
        """Get current client status"""
        try:
            config, error = self._authenticate_request()
            if error:
                return {'success': False, 'error': error}
            
            return {
                'success': True,
                'is_blocked': config.is_blocked,
                'block_reason': config.block_reason,
                'show_warning': config.show_warning,
                'warning_message': config.warning_message,
                'payment_status': config.payment_status,
                'outstanding_amount': config.outstanding_amount,
                'last_server_contact': config.last_server_contact.isoformat() if config.last_server_contact else None,
            }
            
        except Exception as e:
            _logger.error(f"Get status error: {str(e)}")
            return {'success': False, 'error': str(e)}


# Separate controller for warning data
class SmartHiveWarningController(http.Controller):
    
    @http.route('/smarthive_client/warning_data', type='json', auth='user', methods=['GET'], csrf=False)
    def get_warning_data(self):
        """Get warning banner data for current user"""
        try:
            config = request.env[CLIENT_CONFIG_MODEL].get_active_config()
            if not config:
                return {'show_warning': False}
            
            return config.get_warning_data() or {'show_warning': False}
            
        except Exception as e:
            _logger.error(f"Get warning data error: {str(e)}")
            return {'show_warning': False, 'error': str(e)}


class SmartHiveLocalAdminController(http.Controller):
    """Local administration endpoints for super admin"""
    
    def _check_admin_access(self):
        """Check if current user is admin"""
        if not request.env.user.has_group('base.group_system'):
            return False, "Access denied: Admin privileges required"
        return True, None
    
    @http.route('/smarthive_client/local/block', type='json', auth='user', methods=['POST'], csrf=False)
    def local_block_client(self):
        """Block client access locally (admin only)"""
        try:
            is_admin, error = self._check_admin_access()
            if not is_admin:
                return {'success': False, 'error': error}
            
            config = request.env[CLIENT_CONFIG_MODEL].get_active_config()
            if not config:
                return {'success': False, 'error': 'No active configuration found'}
            
            if not config.local_admin_mode:
                return {'success': False, 'error': 'Local admin mode not enabled'}
            
            data = request.jsonrequest or {}
            
            config.sudo().write({
                'is_blocked': True,
                'block_reason': data.get('block_reason', 'Access blocked by local administrator'),
            })
            
            # Log the block action
            request.env[CLIENT_STATUS_MODEL].sudo().create({
                'status_type': 'block',
                'status': 'warning',
                'message': 'Local admin blocked client access',
            })
            
            return {'success': True}
            
        except Exception as e:
            _logger.error(f"Local block client error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/smarthive_client/local/unblock', type='json', auth='user', methods=['POST'], csrf=False)
    def local_unblock_client(self):
        """Unblock client access locally (admin only)"""
        try:
            is_admin, error = self._check_admin_access()
            if not is_admin:
                return {'success': False, 'error': error}
            
            config = request.env[CLIENT_CONFIG_MODEL].get_active_config()
            if not config:
                return {'success': False, 'error': 'No active configuration found'}
            
            if not config.local_admin_mode:
                return {'success': False, 'error': 'Local admin mode not enabled'}
            
            config.sudo().write({
                'is_blocked': False,
                'block_reason': '',
            })
            
            # Log the unblock action
            request.env[CLIENT_STATUS_MODEL].sudo().create({
                'status_type': 'block',
                'status': 'success',
                'message': 'Local admin unblocked client access',
            })
            
            return {'success': True}
            
        except Exception as e:
            _logger.error(f"Local unblock client error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/smarthive_client/local/warning', type='json', auth='user', methods=['POST'], csrf=False)
    def local_set_warning(self):
        """Set warning banner locally (admin only)"""
        try:
            is_admin, error = self._check_admin_access()
            if not is_admin:
                return {'success': False, 'error': error}
            
            config = request.env[CLIENT_CONFIG_MODEL].get_active_config()
            if not config:
                return {'success': False, 'error': 'No active configuration found'}
            
            if not config.local_admin_mode:
                return {'success': False, 'error': 'Local admin mode not enabled'}
            
            data = request.jsonrequest or {}
            
            config.sudo().write({
                'show_warning': data.get('show_warning', False),
                'warning_message': data.get('warning_message', ''),
                'payment_status': data.get('payment_status', 'paid'),
                'outstanding_amount': data.get('outstanding_amount', 0.0),
            })
            
            # Log the warning action
            request.env[CLIENT_STATUS_MODEL].sudo().create({
                'status_type': 'warning',
                'status': 'info',
                'message': 'Local admin updated warning configuration',
            })
            
            return {'success': True}
            
        except Exception as e:
            _logger.error(f"Local set warning error: {str(e)}")
            return {'success': False, 'error': str(e)}