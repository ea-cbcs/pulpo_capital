# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import random


def _generate_fake_email():
    names = ["alice", "bob", "charlie", "david", "ella"]
    domains = ["gmail", "yahoo", "hotmail", "outlook", "thunderbird"]
    return f"{random.choice(names)}{random.randint(10, 99)}@{random.choice(domains)}.com"


def _generate_fake_phone():
    return f"+1{random.randint(1000000000, 9999999999)}"


class CreditApplication(models.Model):
    _inherit = 'crm.lead'
    _description = 'Credit Application'

    app_id = fields.Char(string="App Id", copy=False, readonly=True, default=lambda self: _("New"))
    fake_business_phone = fields.Char(string='Fake Business Phone')

    web_submission = fields.Boolean()
    partner_id = fields.Many2one(string='Company Name')
    legal_corporate_name = fields.Char(related='partner_id.name', readonly=False, store=True, string='Legal Corporate Name')
    industry = fields.Many2one('res.partner.industry', string='Industry', tracking=True, related='partner_id.industry_id', readonly=False, store=True)
    vat = fields.Char(string="Federal Tax ID", tracking=True, related='partner_id.vat', readonly=False, store=True)
    state_id = fields.Many2one('res.country.state', string='Incorporation State', tracking=True, related='partner_id.state_id', readonly=False, store=True)
    legal_entity = fields.Selection(selection=[
        ('llc', 'LLC'),
        ('corporation', 'Corporation'),
        ('sole_prop', 'Sole Prop.'),
        ('partnership', 'Partnership'),
        ('other', 'Other')
    ], string='Entity', tracking=True, related='partner_id.legal_entity', readonly=False, store=True)
    phone = fields.Char(string="Phone", tracking=True, related='partner_id.phone', readonly=False, store=True)
    city = fields.Char(string="City", tracking=True, related='partner_id.city', readonly=False, store=True)
    zip = fields.Char(tracking=True, related='partner_id.zip', readonly=False, store=True)
    country_id = fields.Many2one('res.country', string="Country", tracking=True, related='partner_id.country_id', readonly=False, store=True)
    business_start_date = fields.Date(string='Business Start Date', tracking=True)
    business_owner_ids = fields.Many2many(
        'res.partner',
        'crm_lead_business_owners_rel',
        string="Business Owners"
    )

    attachment_bank_statements_ids = fields.Many2many('ir.attachment', 'attachment_bank_statement_rel',
                                                      string="Bank Statements")
    attachment_id_ids = fields.Many2many('ir.attachment', 'attachment_id_rel', string="IDs")
    attachment_voided_check_ids = fields.Many2many('ir.attachment', 'attachment_voided_check_rel',
                                                   string="Voided Checks")

    attachment_proof_of_ein_ids = fields.Many2many('ir.attachment', 'attachment_proof_of_ein_rel',
                                                   string="Proof of EIN")
    attachment_extras_ids = fields.Many2many('ir.attachment', 'attachment_extras_rel', string="Extras")

    attachment_pdf_id = fields.Many2one('ir.attachment', 'Attachment PDF')
    additional_notes = fields.Html(string='Additional Notes')

    # Compute fields that will be used with smart buttons.
    bank_statements_count = fields.Integer(
        string="Bank Statement Docs Count",
        compute="_compute_attachments_count",
        store=False
    )
    ids_count = fields.Integer(
        string="ID Docs Count",
        compute="_compute_attachments_count",
        store=False
    )
    voided_checks_count = fields.Integer(
        string="Voided Checks Docs Count",
        compute="_compute_attachments_count",
        store=False
    )
    proof_ein_count = fields.Integer(
        string="Proof of EIN Count",
        compute="_compute_attachments_count",
        store=False
    )
    extras_count = fields.Integer(
        string="Extras Count",
        compute="_compute_attachments_count",
        store=False
    )

    @api.depends('attachment_bank_statements_ids', 'attachment_id_ids', 'attachment_voided_check_ids', 'attachment_proof_of_ein_ids', 'attachment_extras_ids')
    def _compute_attachments_count(self):
        for record in self:
            record.bank_statements_count = len(record.attachment_bank_statements_ids)
            record.ids_count = len(record.attachment_id_ids)
            record.voided_checks_count = len(record.attachment_voided_check_ids)
            record.proof_ein_count = len(record.attachment_proof_of_ein_ids)
            record.extras_count = len(record.attachment_extras_ids)

    def action_view_attachment_bank_statements(self):
        """Redirect to the attachments related to bank statements"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bank Statements',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.attachment_bank_statements_ids.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_attachment_ids(self):
        """Redirect to the attachments related to IDs"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'IDs',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.attachment_id_ids.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_attachment_voided_checks(self):
        """Redirect to the attachments related to voided checks"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Voided Checks',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.attachment_voided_check_ids.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_attachment_proof_of_ein(self):
        """Redirect to the attachments related to EIN proofs"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'EIN Proofs',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.attachment_proof_of_ein_ids.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_view_attachment_extras(self):
        """Redirect to the attachments related to extra documents"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Extras',
            'view_mode': 'kanban',
            'res_model': 'ir.attachment',
            'domain': [('id', 'in', self.attachment_extras_ids.ids)],
            'context': {'create': 0, 'edit': 0, 'delete': 0},
            'target': 'current',
        }

    def action_generate_leads(self):
        pass

    def action_send_funders_wizard(self):
        return {
            'name': 'Send to Funds',
            'type': 'ir.actions.act_window',
            'res_model': 'submit.application.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('broker_management.submit_application_wizard').id,
            'target': 'new',
            'context': {
                'default_credit_application_id': self.id, 'submission_to_funder': True, 'app_submission': False
            }
        }

    def action_submit_application(self):
        return {
            'name': 'Submit Application',
            'type': 'ir.actions.act_window',
            'res_model': 'submit.application.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('broker_management.submit_application_wizard').id,
            'target': 'new',
            'context': {
                'default_credit_application_id': self.id, 'app_submission': True, 'submission_to_funder': False
            }
        }

    @api.model
    def create(self, vals):

        vals['app_id'] = self.env['ir.sequence'].next_by_code('credit.application') or _('New')

        vals['fake_business_phone'] = _generate_fake_phone()

        res = super().create(vals)
        return res
