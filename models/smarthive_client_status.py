# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SmartHiveClientStatus(models.Model):
    _name = 'smarthive.client.status'
    _description = 'SmartHive Client Status Log'
    _order = 'create_date desc'

    status_type = fields.Selection([
        ('heartbeat', 'Heartbeat'),
        ('warning', 'Warning'),
        ('block', 'Block Status'),
        ('system', 'System'),
        ('error', 'Error')
    ], string='Status Type', required=True)
    
    status = fields.Selection([
        ('success', 'Success'),
        ('warning', 'Warning'), 
        ('error', 'Error'),
        ('info', 'Information')
    ], string='Status', required=True)
    
    message = fields.Text(
        string='Message',
        required=True
    )
    
    details = fields.Text(
        string='Details'
    )
    
    create_date = fields.Datetime(
        string='Date',
        readonly=True
    )

    @api.model
    def log_status(self, status_type, status, message, details=None):
        """Helper method to log client status"""
        return self.create({
            'status_type': status_type,
            'status': status,
            'message': message,
            'details': details,
        })