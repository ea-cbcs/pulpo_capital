odoo.define('credit_application.form_validation', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.FormValidation = publicWidget.Widget.extend({
        selector: '.s_website_form_submit',

        start: function () {
            this.$('.btn.s_website_form_send').on('click', this._checkRequiredFields.bind(this));
        },

        _checkRequiredFields: function (event) {
            var self = this;
            var firstEmptyRequiredField = self.$el.closest('form').find('[required]').filter(function() {
                return !this.value.trim();
            }).first();

            if (firstEmptyRequiredField.length) {
                event.preventDefault(); // Prevent form submission only if a required field is empty
                firstEmptyRequiredField.focus();
            }
            // If all required fields are filled, do nothing and let Odoo handle the submission
        },

    });
});