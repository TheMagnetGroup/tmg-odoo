odoo.define('delivery_iot.widgets', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var field_registry = require('web.field_registry');
var AbstractAction = require('web.AbstractAction')
var widget_registry = require('web.widget_registry');
var Dialog = require('web.Dialog');
var ActionManager = require('web.ActionManager');
var basic_fields = require('web.basic_fields');
var BusService = require('bus.BusService');

var _t = core._t;

ActionManager.include({
    _executeClientAction: function (action, options) {
        if (action.context.device_id) {
            // Call new route that sends you report to send to printer
            var self = this;
            self.action = action;
            return this._rpc({
                model: 'ir.actions.client',
                method: 'iot_render',
                args: [action.id, action.context.active_ids, {'device_id': action.context.device_id}]
            }).then(function (result) {
                debugger;
                self.call(
                    'iot_longpolling',
                    'action',
                    result[0],
                    result[1],
                    {'documents': result[2]},
                    self._onActionSuccess.bind(self),
                    self._onActionFail.bind(self)
                );
            });
        }
        else {
            return this._super.apply(this, arguments);
        }
    },
});
core.action_registry.add('print', AbstractAction());
});