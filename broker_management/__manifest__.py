# -*- coding: utf-8 -*-
{
    'name': "Broker Management - Werfundingllc",
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': "Comprehensive Application Management for Brokers, Clients, and Funders.",
    'description': """This module provides a streamlined application management system for brokers, clients, and funders, ensuring efficient handling of applications, approvals, and funder interactions.

Key Features:

- **Broker Dashboard**:
  - A dedicated back-end interface where brokers can manage and track client applications.
  - Tools for reviewing, updating, and processing submissions.

- **Client Submission Portal**:
  - A website form allowing clients to submit their application details directly.
  - Secure data handling and validation for accurate submissions.

- **Client Profile Management**:
  - A centralized dashboard for managing client profiles and application statuses.
  - Integrated email functionality to notify company managers about approved applications.

- **Manager Dashboard**:
  - A separate dashboard for company managers to oversee all applications.
  - Tools to approve and forward applications to funders or banks.

- **Funder Management**:
  - A structured database for maintaining funder profiles and details.
  - Efficient tracking and management of funder interactions.

- **PDF Generation**:
  - Capability to generate application PDFs with both original and demo details for documentation and sample purposes.

This module enhances transparency, automates workflows, and ensures a seamless application handling process from client submission to funder approvals.
""",
    'author': 'Caribou Consulting.',
    'company': 'Caribou Consulting.',
    'website': "https://www.cariboucs.com",
    'license': 'Other proprietary',
    'depends': ['base', 'mail', 'crm', 'website'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_config_views.xml',
        'views/view_crm_application.xml',
        'wizard/submit_application_wizard.xml',
        'views/web_application_templates.xml',
        'views/view_report_template.xml',
        'report/report_templates.xml',
    ],
    'application': True,
}
