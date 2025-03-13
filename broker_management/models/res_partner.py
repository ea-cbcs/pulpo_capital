# -*- coding: utf-8 -*-

import requests
import base64
import json

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from ..models.crm_lead import _generate_fake_email, _generate_fake_phone


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    broker_application_link = fields.Char(
        string="Broker Application Link",
        compute="_compute_broker_application_link",
        precompute=True,
        store=False
    )

    def _compute_broker_application_link(self):
        """Computes the broker application link for the user."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='')
        for user in self:
            if base_url:
                user.broker_application_link = f"{base_url}/crm/lead_submission?user_id={user.id}"
            else:
                user.broker_application_link = "Base URL not configured"


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    _sql_constraints = [
        ('ssn_uniq', 'unique (social_security_no)',
         "The Social Security No. must be unique, this number is already associated with another person.")
    ]

    def download_and_store_audio(self):
        """Downloads an audio file and stores it as an attachment in Odoo."""
        url = "https://www.cs.uic.edu/~i101/SoundFiles/CantinaBand60.wav"

        response = requests.get(url)
        if response.status_code == 200:
            file_data = base64.b64encode(response.content)

            attachment = self.env['ir.attachment'].create({
                'name': 'CantinaBand60.wav',
                'type': 'binary',
                'datas': file_data,
                'res_model': 'crm.lead',  # Change to your desired model
                'res_id': self.id,
                'mimetype': 'audio/wav',
            })

            # self.audio_attachment_id = attachment.id

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
        else:
            raise ValueError("Failed to download the audio file")

    # vicidial_lead_id = fields.Char(string="Vicidial Lead ID", readonly=True)
    # is_vici_lead = fields.Boolean(string="Vicidial Lead?", readonly=True)

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

    def _get_vicidial_field_mapping(self):
        """Maps Odoo fields to Vicidial fields."""
        return {
            "name": "first_name",
            "last_name": "last_name",
            "email": "email",
            "phone": "phone_number",
            "mobile": "alt_phone",
            "street": "address1",
            "street2": "address2",
            "city": "city",
            "state_id": "state",
            "zip": "postal_code",
            "birth_date": "date_of_birth",
            'comment': 'comments'
        }

    def _prepare_vicidial_payload(self, vals):
        """Prepares the payload for Vicidial API."""
        mapping = self._get_vicidial_field_mapping()
        payload = {}

        for odoo_field, vicidial_param in mapping.items():
            if odoo_field in vals:
                value = vals[odoo_field]

                if odoo_field == "state_id":
                    value = self.env['res.country.state'].browse(value).name if value else ''
                elif odoo_field == "birth_date":
                    try:
                        date_obj = fields.Date.from_string(value)
                        value = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        value = ''

                payload[vicidial_param] = value

        return payload

    def create_lead_in_vicidial(self, vals):
        return 4
        # """Creates a lead in Vicidial and stores the returned lead ID."""
        # url = "https://vicidial.example.com/api/leads"
        # payload = self._prepare_vicidial_payload(vals)
        #
        # try:
        #     response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        #     response_data = response.json()
        #
        #     if response.status_code == 201 and response_data.get("lead_id"):
        #         return response_data["lead_id"]
        #     else:
        #         raise Exception("Failed to create lead in Vicidial: {}".format(response_data))
        # except requests.RequestException as e:
        #     raise Exception("Error communicating with Vicidial API: {}".format(str(e)))

    def update_lead_in_vicidial(self, vicidial_lead_id, vals):
        """Updates an existing lead in Vicidial."""
        url = f"https://vicidial.example.com/api/leads/{vicidial_lead_id}"
        payload = self._prepare_vicidial_payload(vals)

        if not payload:
            return  # No changes to update

        try:
            response = requests.put(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

            if response.status_code != 200:
                raise Exception("Failed to update lead in Vicidial: {}".format(response.text))
        except requests.RequestException as e:
            raise Exception("Error communicating with Vicidial API: {}".format(str(e)))

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            vals['fake_email'] = _generate_fake_email()
            vals['fake_phone'] = _generate_fake_phone()
            # if self._context.get('is_vici_lead'):
            #     vals['is_vici_lead'] = True
            # if vals.get('is_vici_lead', False):
            #     vicidial_lead_id = self.create_lead_in_vicidial(vals)
            #     if vicidial_lead_id:
            #         vals['vicidial_lead_id'] = vicidial_lead_id

        return super().create(vals_list)

    def write(self, vals):
        """Overrides write to automatically update Vicidial lead when relevant fields change."""
        # for record in self:
        #     if record.vicidial_lead_id:
        #         changes = {}
        #         for odoo_field, vicidial_param in self._get_vicidial_field_mapping().items():
        #             if odoo_field in vals and vals[odoo_field] != record[odoo_field]:
        #                 changes[vicidial_param] = vals[odoo_field]
        #
        #         res = super(ResPartnerInherit, record).write(vals)
        #
        #         if changes:
        #             record.update_lead_in_vicidial(record.vicidial_lead_id, changes)
        #
        #         return res

        return super(ResPartnerInherit, self).write(vals)
