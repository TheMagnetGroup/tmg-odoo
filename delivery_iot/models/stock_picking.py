# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_print_labels(self):
        if self.carrier_id.printer_id:
            attachments = self.env['ir.attachment'].search([('res_id', '=', self.id), ('res_model', '=', 'stock.picking')])
            labels = self.env['ir.attachment']
            for att in attachments:
                file_name = att.datas_fname
                if any([ext == file_name.split('.') for ext in ('ZPL', 'ZPLII', 'EPL')]):
                    labels |= att
            if labels:
                return {
                    'name': 'Print Labels',
                    'type': 'ir.actions.client',
                    'tag': 'print',
                    'context': {
                        'active_ids': labels.ids,
                        'device_id': self.carrier_id.printer_id.id
                    }
                }
            else:
                raise UserError(_("No labels found having any of ZPL,ZPLII,EPL extensions."))
        else:
            raise UserError(_('Label printer is not configured on Delivery Method: {}'.format(self.carrier_id.name)))
