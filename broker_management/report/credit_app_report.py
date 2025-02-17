# -*- coding:utf-8 -*-
from odoo import models, fields, api


class CreditApp(models.AbstractModel):
    _name = 'report.credit_app_report.credit_report'
    _description = "Credit App Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['crm.lead'].browse(docids)

        company = self.env['res.company'].search([('id', '=', 1)])

        return {
            'doc_ids': docids,
            'doc_model': 'crm.lead',
            'data': data,
            'docs': record,
            'company': company
        }


class CreditAppFake(models.AbstractModel):
    _name = 'report.credit_app_report.credit_report_fake'
    _description = "Credit App Report Fake"

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['crm.lead'].browse(docids)

        company = self.env['res.company'].search([('id', '=', 1)])

        return {
            'doc_ids': docids,
            'doc_model': 'crm.lead',
            'data': data,
            'docs': record,
            'company': company
        }
