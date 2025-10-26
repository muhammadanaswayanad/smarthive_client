# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_check_smarthive_warnings(self):
        """Check for SmartHive warnings and show them to user"""
        config = self.env['smarthive.client.config'].get_active_config()
        
        if not config:
            return True
            
        # Check if client is blocked
        if config.is_blocked:
            return {
                'type': 'ir.actions.act_window',
                'name': _('System Access Restricted'),
                'res_model': 'smarthive.block.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_block_reason': config.block_reason,
                    'default_local_admin_mode': config.local_admin_mode,
                },
            }
        
        # Check for warnings
        if config.show_warning:
            return {
                'type': 'ir.actions.act_window',
                'name': _('System Notice'),
                'res_model': 'smarthive.crm.warning.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_warning_message': config.warning_message,
                    'default_payment_status': config.payment_status,
                    'default_outstanding_amount': config.outstanding_amount,
                    'default_local_admin_mode': config.local_admin_mode,
                },
            }
        
        return True

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to check for warnings when CRM leads are loaded"""
        # First check for SmartHive warnings
        config = self.env['smarthive.client.config'].get_active_config()
        
        # Store warning state in user context for frontend to handle
        if config:
            self.env.context = dict(self.env.context)
            if config.is_blocked:
                self.env.context['smarthive_blocked'] = True
                self.env.context['smarthive_block_reason'] = config.block_reason
            elif config.show_warning:
                self.env.context['smarthive_warning'] = True
                self.env.context['smarthive_warning_data'] = {
                    'message': config.warning_message,
                    'payment_status': config.payment_status,
                    'outstanding_amount': config.outstanding_amount,
                }
        
        return super().search_read(domain, fields, offset, limit, order)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to check warnings when creating new leads"""
        self._check_smarthive_access()
        return super().create(vals_list)

    def write(self, vals):
        """Override write to check warnings when updating leads"""
        self._check_smarthive_access()
        return super().write(vals)

    def _check_smarthive_access(self):
        """Check if SmartHive is blocking access"""
        config = self.env['smarthive.client.config'].get_active_config()
        
        if config and config.is_blocked:
            # Don't block admin users
            if not (self.env.user.has_group('base.group_system') or self.env.user.id == 1):
                raise UserError(_(
                    "System access is currently restricted.\n\n"
                    "Reason: %s\n\n"
                    "Please contact your system administrator for assistance."
                ) % (config.block_reason or "Access temporarily blocked"))