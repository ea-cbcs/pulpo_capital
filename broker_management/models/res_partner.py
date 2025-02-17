# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from ..models.crm_lead import _generate_fake_email, _generate_fake_phone


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    _sql_constraints = [
        ('ssn_uniq', 'unique (social_security_no)',
         "The Social Security No. must be unique, this number is already associated with another person.")
    ]

    business_owner = fields.Boolean(string='Business Owner?')
    funder = fields.Boolean(string='Funder?')
    last_name = fields.Char(string='Last Name')
    ownership_percent = fields.Float(string='Ownership (%)', tracking=True)
    social_security_no = fields.Char(string='Social Security No', tracking=True)
    birth_date = fields.Date(string='Date of Birth')
    vat = fields.Char(string="Federal Tax ID", tracking=True)
    incorporation_state_id = fields.Many2one('res.country.state', string='Incorporation State', tracking=True)
    legal_entity = fields.Selection(selection=[
        ('llc', 'LLC'),
        ('corporation', 'Corporation'),
        ('sole_prop', 'Sole Prop.'),
        ('partnership', 'Partnership'),
        ('other', 'Other')
    ], string='Entity', tracking=True)

    fake_email = fields.Char(string='Fake Email')
    fake_phone = fields.Char(string='Fake Phone')
    state_id = fields.Many2one(domain=[('country_id.code', '=', 'US')])

    @api.constrains('ownership_percent')
    def _check_ownership_percent(self):
        for record in self:
            if record.ownership_percent > 100 or record.ownership_percent < 0:
                raise ValidationError(_("Ownership percent should be between 0 and 100."))

    @api.constrains('birth_date')
    def _check_birth_date(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(_("Date of Birth cannot be in the future."))

    @api.model
    def create(self, vals):

        vals['fake_email'] = _generate_fake_email()
        vals['fake_phone'] = _generate_fake_phone()
        # vals['funder_number'] = self.env['ir.sequence'].next_by_code('res.partner.funder') or _('New')

        return super().create(vals)
