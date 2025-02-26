from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64


class SubmitApplicationWizard(models.TransientModel):
    _name = 'submit.application.wizard'
    _description = 'Submit Application Popup'

    credit_application_id = fields.Many2one('crm.lead', string='Credit Application')
    funder_ids = fields.Many2many('res.partner', string='Funders')
    in_house = fields.Boolean()
    external = fields.Boolean()
    # Document options
    applications = fields.Boolean()
    doc_ids = fields.Boolean(string="Ids")
    proof_ein = fields.Boolean(string="Proof of EIN")
    bank_statement = fields.Boolean(string="Bank Statements")
    voided_checks = fields.Boolean(string="Voided Checks")
    extras = fields.Boolean(string="Extras")
    email_message = fields.Html(string='Message', default=lambda self: self._context.get('additional_notes'))

    def _generate_application_pdf(self, app_id_ref):
        company_name = self.credit_application_id.partner_id.name
        app_id = self.credit_application_id.app_id
        file_name = f"{company_name}-{app_id}.pdf"

        report_id = self.env.ref(app_id_ref).id
        report = self.env['ir.actions.report'].browse(report_id)

        pdf_data, _ = self.env.ref(app_id_ref)._render_qweb_pdf(report.id,
                                             [self.credit_application_id.id])
        # Create a new attachment record with the PDF data
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': base64.b64encode(pdf_data),
            'res_model': 'crm.lead',
            'res_id': self.credit_application_id.id,
            'type': 'binary',
            'mimetype': 'application/pdf'
        })
        self.credit_application_id.attachment_pdf_id = attachment.id

        return attachment

    def gather_attachment_ids(self, credit_application_id):

        applications = self.env['ir.attachment']

        if self.bank_statement:
            applications |= credit_application_id.attachment_bank_statements_ids
        if self.doc_ids:
            applications |= credit_application_id.attachment_id_ids
        if self.proof_ein:
            applications |= credit_application_id.attachment_proof_of_ein_ids
        if self.voided_checks:
            applications |= credit_application_id.attachment_voided_check_ids
        if self.extras:
            applications |= credit_application_id.attachment_extras_ids

        if not len(applications) and not self.in_house and not self.external:
            raise ValidationError(_("Please select attachment options for Submission."))

        all_attachment_ids = applications.ids

        return all_attachment_ids

    def action_send_mail_funds(self):
        if not self.funder_ids and not self.env.context.get('app_submission', False):
            raise ValidationError(_("Please Select Funders to Send the application."))

        Mail = self.env['mail.mail']
        body = self.email_message
        subject = f'New Submission - {self.credit_application_id.partner_id.name} - {self.credit_application_id.app_id}'
        attachment_ids = self.gather_attachment_ids(self.credit_application_id)

        if self.in_house:
            attachment_ids.append(self._generate_application_pdf('broker_management.credit_app_report_id').id)
        if self.external:
            attachment_ids.append(self._generate_application_pdf('broker_management.credit_app_report_fake').id)

        if not self.env.context.get('app_submission', False):
            # message_body = ''
            for funder in self.funder_ids:
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_from': self.env.company.email,
                    'email_to': funder.email,
                    'reply_to': self.env.company.email
                }

                mail = Mail.create(mail_values)
                mail.unrestricted_attachment_ids = [(6, 0, attachment_ids)]
                mail.send()

                # Create an unordered list of names with HTML line breaks
                # names = self.funder_ids.mapped('name')
                # for name in names:
                #     message_body += '<li>%s</li>' % name

            # # Post a message in the chatter with line breaks
            # if message_body:
            #     message_body = f'Application Submitted at <b>{fields.Datetime.now()}</b> to Funders:<br/><br/><ul>' + message_body + '</ul><br/>'
            #     self.credit_application_id.message_post(body=message_body)

        else:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_from': self.env.user.email,
                'email_to': self.env.company.email
            }

            mail = Mail.create(mail_values)
            mail.unrestricted_attachment_ids = [(6, 0, attachment_ids)]
            mail.send()

        return {'type': 'ir.actions.act_window_close'}
