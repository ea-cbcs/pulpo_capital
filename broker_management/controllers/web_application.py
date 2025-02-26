import base64
import re

from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import Forbidden


def _extract_data(values):
    data = {
        'record': {},  # Values to create record
        'attachments': {},  # Attachments grouped by field
    }

    for field_name, field_value in values.items():
        # Decode field name
        field_name = re.sub('&quot;', '"', field_name)

        # Check if the value is a list of files (e.g., multiple attachments)
        attachments = request.httprequest.files.getlist(field_name)
        # Iterate through each file and group them by field name
        for file in attachments:
            original_field_name = field_name.split('[', 1)[0]
            if original_field_name not in data['attachments']:
                data['attachments'][original_field_name] = []
            file.field_name = original_field_name
            data['attachments'][original_field_name].append(file)

    return data


def _get_or_create_partner(owner_data):
    """Get or create a business owner based on SSN."""
    ssn = owner_data.get('social_security_no')
    partner = request.env['res.partner'].sudo().search([('social_security_no', '=', ssn)], limit=1)
    if not partner:
        partner = request.env['res.partner'].sudo().create(owner_data)
    return partner.id


class CrmLeadSubmissionController(http.Controller):

    @http.route('/crm/lead_submission', auth='public', website=True, type='http', methods=['GET', 'POST'])
    def submit_crm_lead(self, **post):
        env = request.env
        industries = request.env['res.partner.industry'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([('country_id.code', '=', 'US')])
        countries = request.env['res.country'].sudo().search([])

        values = {
            'industries': industries,
            'states': states,
            'countries': countries,
            'funding_specialist_id': request.params.get('user_id')
        }

        view = env.ref('broker_management.crm_lead_submission')
        view = view.sudo()

        if post.get('visibility_password') and (
                request.website.is_public_user() or view.id not in request.session.get('views_unlock', [])):
            pwd = post['visibility_password']
            if pwd and env.user._crypt_context().verify(
                    pwd, view.visibility_password):
                request.session.setdefault('views_unlock', list()).append(view.id)
                return request.render("broker_management.crm_lead_submission", values)
            error = Forbidden('website_visibility_password_required')
            raise error

        if post and request.httprequest.method == 'POST':
            # Log the entire request for debugging
            salesperson = request.env['res.users'].sudo().browse(int(post.get('salesperson')))
            vat = post.get('vat')
            # bank_statements = request.httprequest.files.getlist('attachment_bank_statements_ids')

            partner = env['res.partner'].sudo().search([('vat', '=', vat)], limit=1)
            if not partner:
                country_usa = env['res.country'].sudo().search([('code', '=', 'US')], limit=1)
                partner = env['res.partner'].sudo().create({
                    'name': post.get('legal_corporate_name'),
                    'vat': vat,
                    'industry_id': int(post.get('industry')) if post.get('industry') else False,
                    'state_id': int(post.get('state_id')) if post.get('state_id') else False,
                    'legal_entity': post.get('legal_entity'),
                    'phone': post.get('phone'),
                    'city': post.get('city'),
                    'zip': post.get('zip'),
                    'country_id': country_usa.id if country_usa else False,
                    'is_company': True
                })

            owner_1_data = {
                'name': post.get('owner1_first_name'),
                'last_name': post.get('owner1_last_name'),
                'email': post.get('owner1_email'),
                'ownership_percent': post.get('owner1_ownership_percent'),
                'social_security_no': post.get('owner1_ssn'),
                'birth_date': post.get('owner1_birth_date'),
                'phone': post.get('owner1_phone'),
                'mobile': post.get('owner1_mobile'),
                'street': post.get('owner1_street'),
                'city': post.get('owner1_city'),
                'state_id': int(post.get('owner1_state_id')) if post.get('owner1_state_id') else False,
                'zip': post.get('owner1_zip'),
            }

            owner_2_data = {
                'name': post.get('owner2_first_name'),
                'last_name': post.get('owner2_last_name'),
                'email': post.get('owner2_email'),
                'ownership_percent': post.get('owner2_ownership_percent'),
                'social_security_no': post.get('owner2_ssn'),
                'birth_date': post.get('owner2_birth_date'),
                'phone': post.get('owner2_phone'),
                'mobile': post.get('owner2_mobile'),
                'street': post.get('owner2_street'),
                'city': post.get('owner2_city'),
                'state_id': int(post.get('owner2_state_id')) if post.get('owner2_state_id') else False,
                'zip': post.get('owner2_zip'),
            }

            owner_1_id = _get_or_create_partner(owner_1_data)
            owner_2_id = _get_or_create_partner(owner_2_data)

            lead = env['crm.lead'].sudo().create({
                'web_submission': True,
                'name': post.get('legal_corporate_name'),
                'partner_id': partner.id,
                'user_id': salesperson.id if salesperson else False,
                'business_start_date': post.get('business_start_date'),
                'business_owner_ids': [(6, 0, [owner_1_id, owner_2_id])],
            })

            data = _extract_data(post)
            # Process and attach files for each attachment field
            for field_name, files in data['attachments'].items():
                attachment_ids = []
                for file in files:
                    # Convert file to base64 and create attachment
                    file_base64 = base64.b64encode(file.read()).decode('utf-8')

                    attachment = env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'type': 'binary',
                        'datas': file_base64,
                        'mimetype': file.mimetype,
                        'res_model': 'crm.lead',
                        'res_id': lead.id,
                    })
                    attachment_ids.append(attachment.id)

                lead.sudo().write({field_name: [(6, 0, attachment_ids)]})

            return request.redirect('/contactus-thank-you')

        return request.render("broker_management.crm_lead_submission", values)
