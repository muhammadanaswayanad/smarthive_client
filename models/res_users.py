# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import AccessDenied

# Constants
CLIENT_CONFIG_MODEL = 'smarthive.client.config'


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _check_smarthive_access(self):
        """Check if SmartHive allows user access"""
        # Skip check for superuser and system users
        if self.env.is_superuser() or self.env.user._is_system():
            return True
            
        # Get SmartHive configuration
        config = self.env[CLIENT_CONFIG_MODEL].get_active_config()
        if not config:
            return True  # No configuration means no restrictions
            
        # Check if client is blocked
        if config.is_blocked:
            return False
            
        return True

    def _login(self, db, login, password, user_agent_env):
        """Override login to check SmartHive access restrictions"""
        # First perform normal login
        uid = super(ResUsers, self)._login(db, login, password, user_agent_env)
        
        if uid:
            # Check SmartHive access restrictions
            user = self.browse(uid)
            # Skip check for superuser and admin
            if not user._is_admin() and not self.env.is_superuser():
                if not user._check_smarthive_access():
                    config = self.env[CLIENT_CONFIG_MODEL].get_active_config()
                    block_reason = config.block_reason if config else "Access restricted by administrator"
                    raise AccessDenied(_("Access Denied: %s") % block_reason)
        
        return uid

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """Override to enforce SmartHive access restrictions"""
        # First check normal access rights
        result = super(ResUsers, self).check_access_rights(operation, raise_exception=raise_exception)
        
        # Skip check for superuser and system operations
        if self.env.is_superuser() or self.env.user._is_system():
            return result
            
        # Check SmartHive restrictions for non-admin users
        if not self.env.user._is_admin():
            config = self.env[CLIENT_CONFIG_MODEL].get_active_config()
            if config and config.is_blocked:
                if raise_exception:
                    raise AccessDenied(_("System access is currently restricted: %s") % 
                                     (config.block_reason or "Contact administrator"))
                return False
        
        return result