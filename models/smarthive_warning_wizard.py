# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SmartHiveWarningWizard(models.TransientModel):
    _name = 'smarthive.warning.wizard'
    _description = 'SmartHive Warning Configuration Wizard'

    config_id = fields.Many2one(
        'smarthive.client.config',
        string='Configuration',
        required=True
    )
    
    show_warning = fields.Boolean(
        string='Show Warning Banner',
        default=True,
        help='Display warning banner to users'
    )
    
    warning_message = fields.Text(
        string='Warning Message',
        help='Message to display in the warning banner'
    )
    
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('pending', 'Pending Payment'),
        ('overdue', 'Overdue'),
        ('blocked', 'Payment Blocked')
    ], string='Payment Status', default='paid')
    
    outstanding_amount = fields.Float(
        string='Outstanding Amount',
        help='Outstanding payment amount to display'
    )

    def action_apply_warning(self):
        """Apply warning configuration"""
        self.ensure_one()
        self.config_id._check_local_admin_access()
        
        self.config_id.write({
            'show_warning': self.show_warning,
            'warning_message': self.warning_message,
            'payment_status': self.payment_status,
            'outstanding_amount': self.outstanding_amount,
        })
        
        # Log the warning action
        self.env['smarthive.client.status'].create({
            'status_type': 'warning',
            'status': 'info',
            'message': 'Local admin updated warning configuration',
        })
        
        return {'type': 'ir.actions.act_window_close'}