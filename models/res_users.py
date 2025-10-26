# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import AccessDenied

# Constants
CLIENT_CONFIG_MODEL = 'smarthive.client.config'


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """Override to enforce SmartHive access restrictions"""
        # First check normal access rights
        result = super(ResUsers, self).check_access_rights(operation, raise_exception=raise_exception)
        
        # Skip check for superuser and system operations
        if self.env.uid == 1 or self.env.user.has_group('base.group_system'):
            return result
            
        # Check SmartHive restrictions for non-admin users
        config = self.env[CLIENT_CONFIG_MODEL].get_active_config()
        if config and config.is_blocked:
            if raise_exception:
                raise AccessDenied(_("System access is currently restricted: %s") % 
                                 (config.block_reason or "Contact administrator"))
            return False
        
        return result