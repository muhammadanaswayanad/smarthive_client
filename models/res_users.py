# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import AccessDenied

# Constants
CLIENT_CONFIG_MODEL = 'smarthive.client.config'


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        """Override authenticate to check SmartHive access restrictions"""
        # First perform normal authentication
        uid = super(ResUsers, cls).authenticate(db, login, password, user_agent_env)
        
        if uid:
            # Check SmartHive restrictions after successful authentication
            with cls.pool.cursor() as cr:
                env = api.Environment(cr, uid, {})
                
                try:
                    config = env[CLIENT_CONFIG_MODEL].get_active_config()
                    
                    if config and config.is_blocked:
                        user = env['res.users'].browse(uid)
                        
                        # Allow access for superuser, system admins, and SmartHive Client Admins
                        is_allowed = (
                            uid == 1 or  # Superuser
                            user.has_group('base.group_system') or  # System admin
                            user.has_group('smarthive_client.group_smarthive_client_admin') or  # SmartHive admin
                            user.has_group('base.group_erp_manager')  # ERP Manager as fallback
                        )
                        
                        if not is_allowed:
                            block_reason = config.block_reason or "System access is currently restricted. Contact your administrator."
                            raise AccessDenied(_("Access Denied: %s") % block_reason)
                            
                except Exception:
                    # If there's any error checking SmartHive config, allow access to prevent lockout
                    # This prevents the system from being completely inaccessible
                    pass
        
        return uid

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """Override to enforce SmartHive access restrictions"""
        # First check normal access rights
        result = super(ResUsers, self).check_access_rights(operation, raise_exception=raise_exception)
        
        try:
            # Skip check for superuser, system admins, and SmartHive Client Admins
            is_allowed = (
                self.env.uid == 1 or  # Superuser
                self.env.user.has_group('base.group_system') or  # System admin
                self.env.user.has_group('smarthive_client.group_smarthive_client_admin') or  # SmartHive admin
                self.env.user.has_group('base.group_erp_manager')  # ERP Manager as fallback
            )
            
            if is_allowed:
                return result
                
            # Check SmartHive restrictions for other users
            config = self.env[CLIENT_CONFIG_MODEL].get_active_config()
            if config and config.is_blocked:
                if raise_exception:
                    raise AccessDenied(_("System access is currently restricted: %s") % 
                                     (config.block_reason or "Contact administrator"))
                return False
                
        except Exception:
            # If there's any error, allow access to prevent system lockout
            pass
        
        return result