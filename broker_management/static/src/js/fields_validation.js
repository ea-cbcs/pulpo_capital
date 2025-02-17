odoo.define('credit_application.fields_formatter', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.FieldFormatter = publicWidget.Widget.extend({
        selector: '.s_website_form_input',

        start: function () {
            this.$el.on('input', this._formatField.bind(this));
        },

        _formatField: function (event) {
            var input = event.target;
            var fieldName = input.getAttribute('name');

            if (['vat', 'social_security_no1', 'social_security_no2', 'mobile1', 'mobile2', 'phone'].includes(fieldName)) {
                var originalValue = input.value;
                var value = originalValue.replace(/\D/g, ''); // Remove non-digits

                if (fieldName === 'vat') {
                    value = this._formatVAT(value);
                } else if (fieldName === 'social_security_no1' || fieldName === 'social_security_no2') {
                    value = this._formatSSN(value);
                } else if (fieldName === 'mobile1' || fieldName === 'mobile2' || fieldName === 'phone') {
                    value = this._formatMobile(value);
                }

                // Update the input value only if it has changed
                if (originalValue !== value) {
                    var selectionStart = input.selectionStart;
                    var diff = value.length - originalValue.length;
                    input.value = value;
                    input.setSelectionRange(selectionStart + diff, selectionStart + diff);
                }
            }
        },

        _formatVAT: function (value) {
            // VAT: xx-xxxxxxx (total 10 characters including dash)
            value = value.length > 2 ? value.slice(0, 2) + '-' + value.slice(2) : value;
            return value.length > 10 ? value.slice(0, 10) : value;
        },

        _formatSSN: function (value) {
            // Social: xxx-xx-xxxx (total 11 characters including dashes)
            if (value.length > 3) {
                value = value.slice(0, 3) + '-' + value.slice(3);
            }
            if (value.length > 6) {
                value = value.slice(0, 6) + '-' + value.slice(6);
            }
            return value.length > 11 ? value.slice(0, 11) : value;
        },

        _formatMobile: function (value) {
            // Phone: xxx-xxx-xxxx (total 12 characters including dashes)
            if (value.length > 3) {
                value = value.slice(0, 3) + '-' + value.slice(3);
            }
            if (value.length > 7) {
                value = value.slice(0, 7) + '-' + value.slice(7);
            }
            return value.length > 12 ? value.slice(0, 12) : value;
        }
    });
});
