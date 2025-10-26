# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SmartHiveCrmWarningWizard(models.TransientModel):
    _name = 'smarthive.crm.warning.wizard'
    _description = 'SmartHive CRM Warning Wizard'

    warning_message = fields.Text(
        string='Warning Message',
        readonly=True
    )
    
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('pending', 'Pending Payment'),
        ('overdue', 'Overdue'),
        ('blocked', 'Payment Blocked')
    ], string='Payment Status', readonly=True)
    
    outstanding_amount = fields.Float(
        string='Outstanding Amount',
        readonly=True
    )
    
    local_admin_mode = fields.Boolean(
        string='Local Admin Mode',
        readonly=True
    )

    def action_acknowledge(self):
        """Acknowledge the warning and continue"""
        return {'type': 'ir.actions.act_window_close'}

    def action_contact_admin(self):
        """Open action to contact administrator"""
        return {
            'type': 'ir.actions.act_url',
            'url': 'mailto:admin@company.com?subject=SmartHive System Notice',
            'target': 'new',
        }


class SmartHiveBlockWizard(models.TransientModel):
    _name = 'smarthive.block.wizard'
    _description = 'SmartHive Block Wizard'

    block_reason = fields.Text(
        string='Block Reason',
        readonly=True
    )
    
    local_admin_mode = fields.Boolean(
        string='Local Admin Mode',
        readonly=True
    )

    def action_contact_admin(self):
        """Open action to contact administrator"""
        return {
            'type': 'ir.actions.act_url',
            'url': 'mailto:admin@company.com?subject=System Access Blocked - Assistance Required',
            'target': 'new',
        }