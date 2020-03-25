# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class SaleOrderLineDeliveryWizard(models.TransientModel):
    _name = 'sale.order.line.delivery.wizard'
    _description = 'sale order line delivery wizard'

    # explicitly pass in context
    def _default_sol(self):
        return self.env['sale.order.line'].browse(self.env.context.get('active_ids'))[0]

    sale_line_id = fields.Many2one('sale.order.line', string='Active SOLs', ondelete='cascade', required=True, default=_default_sol)

    file = fields.Binary(string='Import File')

    # a helper function to set the criteria of what is considered a duplicate
    # for a customer contact
    def _get_existing_partner_searching_domain(self, partner_id):
        return [
                    ('id', '!=', partner_id.id),
                    ('active', '=', True),
                    # ('parent_id', '=', partner_id.parent_id.id),
                    ('name', '=', partner_id.name),
                    ('attention_to', '=', partner_id.attention_to),
                    ('street', '=', partner_id.street),
                    ('street2', '=', partner_id.street2),
                    ('city', '=', partner_id.city),
                    ('state_id', '=', partner_id.state_id.id),
                    ('zip', '=', partner_id.zip),
                    ('country_id', '=', partner_id.country_id.id),
                    ('phone', '=', partner_id.phone),
                    ('email', '=', partner_id.email)
                ]

    def do_import(self, model_name, decoded_file, options):
        import_id = self.env['base_import.import'].create({
                'res_model': model_name,
                'file': decoded_file,
                'file_type': 'text/csv'
            })
        data_gen = import_id._read_file(options)
        # the first item from data generator is header
        header = next(data_gen)
        valid_fields = import_id.get_fields(model_name)
        parsed_header, matches = import_id._match_headers(iter([header]), valid_fields, options)
        recognized_fields = [(matches[i] and matches[i][0]) or False for i in range(len(parsed_header))]
        result = import_id.do(recognized_fields, parsed_header, options)
        rids = result.get('ids')
        if not rids:
            raise ValidationError(_('Cannot create/find {} records from the uploaded file.\n'
                                    'Make sure the headers of your file match the technical or functional field names on model {}.\n\n'
                                    'Input Header: {}\n'
                                    'Mapped Header: {}\n'
                                    'Error Message: {}'.format(model_name, model_name, parsed_header, recognized_fields,
                                                               result.get('messages'))))
        return rids

    # parent company
    # Delivery Quantity
    def action_import_deliveries(self):
        self.ensure_one()
        if self.sale_line_id and self.file:
            decoded_file = base64.b64decode(self.file)
            options = {'quoting': '"', 'separator': ',', 'headers': True}
            partner_lst = self.do_import('res.partner', decoded_file, options)

            # go through our partner lst and unlink any duplicated ones
            # according to our duplicate domain
            corrected_partner_lst = []
            for i in range(len(partner_lst)):
                partner = partner_lst[i]
                partner_id = self.env['res.partner'].browse(partner)
                partner_id.write({
                    'customer': False,  # new request specifiy this to be False
                    'type': 'delivery' 
                })  # todo: maybe other default fields
                existing_partner_id = self.env['res.partner'].search(self._get_existing_partner_searching_domain(partner_id), limit=1)
                if existing_partner_id:
                    # print(existing_partner_id, partner_id)
                    partner = existing_partner_id.id
                    partner_id.unlink()
                corrected_partner_lst.append(partner)
            # print(corrected_partner_lst)

            result_lst = self.do_import('sale.order.line.delivery', decoded_file, options)

            for i in range(len(result_lst)):
                sold_id = self.env['sale.order.line.delivery'].browse(result_lst[i])
                if sold_id.qty:
                    sold_id.write({
                        'shipping_partner_id': corrected_partner_lst[i],
                        'sale_line_id': self.sale_line_id.id
                    })
                else:
                    # delete when there is no delivery qty
                    # but notice the contact will still be synced
                    sold_id.unlink()

        return {'type': 'ir.actions.act_window_close'}
