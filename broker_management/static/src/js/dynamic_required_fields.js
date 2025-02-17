odoo.define('credit_application.dynamic_required_fields', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.DynamicRequiredFields = publicWidget.Widget.extend({
        selector: '.s_website_form_field',

        start: function () {
            var self = this;
            self._updateFieldsRequirement();
            self.$('input[name="has_second_owner"]').on('change', function() {
                self._updateFieldsRequirement();
            });
        },

        _updateFieldsRequirement: function () {
            var self = this;
            var isSecondOwnerChecked = self.$('input[name="has_second_owner"]').is(':checked');
            var fieldsToMonitor = [
                'contact_name2', 'contact_name_last2', 'birth_date2', 'mobile2', 'email2',
                'social_security_no2', 'city2', 'zip2', 'business_owner_street2',
                'sign_2', 'title_2', 'date_2', 'state_id2'
            ];

            fieldsToMonitor.forEach(function(fieldName) {
                $('input[name="' + fieldName + '"]').prop('required', isSecondOwnerChecked);
            });
        },
    });
});
