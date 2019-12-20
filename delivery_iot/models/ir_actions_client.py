# -*- coding: utf-8 -*-

import base64

from odoo import api, fields, models


class IrActionsClient(models.Model):
    _inherit = "ir.actions.client"

    device_id = fields.Many2one('iot.device', string='IoT Device', domain="[('type', '=', 'printer')]",
                                help='When setting a device here, the report will be printed through this device on the IoT Box')

    def iot_render(self, res_ids, data=None):
        if self.mapped('device_id'):
            device = self.mapped('device_id')[0]
        else:
            device = self.env['iot.device'].browse(data['device_id'])
        attachments = self.env['ir.attachment'].browse(res_ids)
        return device.iot_id.ip, device.identifier, attachments.mapped('datas')
