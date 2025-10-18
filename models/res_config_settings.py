# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    smarthive_client_server_url = fields.Char(
        string='SmartHive Server URL',
        config_parameter='smarthive_client.server_url',
        help='URL of the SmartHive server instance'
    )
    
    smarthive_client_id = fields.Char(
        string='Client ID',
        config_parameter='smarthive_client.client_id',
        help='Unique client identifier'
    )
    
    smarthive_client_api_key = fields.Char(
        string='API Key',
        config_parameter='smarthive_client.api_key',
        help='API key for server authentication'
    )
    
    smarthive_client_heartbeat_interval = fields.Integer(
        string='Heartbeat Interval (minutes)',
        default=15,
        config_parameter='smarthive_client.heartbeat_interval',
        help='How often to send heartbeat to server'
    )
    
    smarthive_client_auto_report = fields.Boolean(
        string='Auto Report Status',
        default=True,
        config_parameter='smarthive_client.auto_report',
        help='Automatically report status to server'
    )