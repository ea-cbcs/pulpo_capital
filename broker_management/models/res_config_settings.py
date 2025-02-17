# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_app_page_url = fields.Char("Web Application Page URL", config_parameter='broker_management.web_app_page_url')
    web_app_password = fields.Char("Web Application Page Password", config_parameter='broker_management.web_app_password')

    def set_values(self):
        """Override set_values to store the setting in ir.config_parameter."""
        super(ResConfigSettings, self).set_values()
        # Store the setting value in ir.config_parameter for all fields
        params = {
            'broker_management.web_app_password': self.web_app_password,
        }
        for key, value in params.items():
            self.env['ir.config_parameter'].sudo().set_param(key, value)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='')
        web_app_form_url = base_url + '/crm/lead_submission'
        self.env['ir.config_parameter'].sudo().set_param('broker_management.web_app_page_url', web_app_form_url)

        if 'broker_management.web_app_password' in params:
            view = self.sudo().env.ref('broker_management.crm_lead_submission')
            view.visibility_password = self.web_app_password

    @api.model
    def get_values(self):
        """Override get_values to retrieve the setting from ir.config_parameter."""
        ConfigParameter = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        # Retrieve the setting values from ir.config_parameter
        res.update({
            'web_app_page_url': ConfigParameter.get_param(
                'broker_management.web_app_page_url', default=''),
            'web_app_password': ConfigParameter.get_param(
                'broker_management.web_app_password', default=''),
        })
        return res
