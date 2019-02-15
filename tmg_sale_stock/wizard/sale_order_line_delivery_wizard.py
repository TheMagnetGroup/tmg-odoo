# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLineDeliveryWizard(models.TransientModel):
    _name = 'sale.order.line.delivery.wizard'

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
                    ('parent_id', '=', partner_id.parent_id.id),
                    ('name', '=', partner_id.name),
                    ('street', '=', partner_id.street),
                    ('street2', '=', partner_id.street2),
                    ('city', '=', partner_id.city),
                    ('state_id', '=', partner_id.state_id.id),
                    ('zip', '=', partner_id.zip),
                    ('country_id', '=', partner_id.country_id.id),
                    ('phone', '=', partner_id.phone),
                    ('email', '=', partner_id.email)
                ]

    def _get_fields_and_columns(self, import_wizard_id, model_name, data, options):
        valid_fields = import_wizard_id.get_fields(model_name)
        # todo: maybe have extra filter here to make sure fields are desired
        # mainly because we are importing 2 different models here and
        # we want to be sure that there is no conflicting fields
        # print(valid_fields)
        headers = data.split('\n')[0].split(',') if data.split('\n') else []  # todo: use exception
        headers, matches = import_wizard_id._match_headers(iter([headers]), valid_fields, options)
        final_fields = [(matches[i] and matches[i][0]) or False for i in range(len(headers))]
        return final_fields, headers

    # parent company
    # Delivery Quantity
    def action_import_deliveries(self):
        self.ensure_one()
        if self.sale_line_id and self.file:
            content = base64.b64decode(self.file)

            # let's do this crazy thing where we first create all the res.partners
            # and then we delete those who are already in db ...
            # I feel so bad
            # someone saves me from this nonsense ...

            data = content.decode("utf-8")
            options = {'quoting': '"', 'separator': ',', 'headers': True}

            import_partner_id = self.env['base_import.import'].create({
                'res_model': 'res.partner',
                'file': content,
                'file_type': 'text/csv'
            })
            partner_fields, partner_columns = self._get_fields_and_columns(import_partner_id, 'res.partner', data, options)
            import_partner_result = import_partner_id.do(partner_fields, partner_columns, options)

            partner_lst = import_partner_result.get('ids')
            if not partner_lst:
                raise ValidationError(_('Cannot create/find customers from the uploaded file. \n'
                                        '{}'.format(import_partner_result.get('messages'))))

            # go through our partner lst and unlink any duplicated ones
            # according to our duplicate domain
            corrected_partner_lst = []
            for i in range(len(partner_lst)):
                partner = partner_lst[i]
                partner_id = self.env['res.partner'].browse(partner)
                partner_id.write({
                    'customer': True,
                    'type': 'delivery' if partner_id.parent_id else 'contact'
                })  # todo: maybe other default fields
                existing_partner_id = self.env['res.partner'].search(self._get_existing_partner_searching_domain(partner_id), limit=1)
                if existing_partner_id:
                    # print(existing_partner_id, partner_id)
                    partner = existing_partner_id.id
                    partner_id.unlink()
                corrected_partner_lst.append(partner)
            # print(corrected_partner_lst)

            import_sold_id = self.env['base_import.import'].create({
                'res_model': 'sale.order.line.delivery',
                'file': content,
                'file_type': 'text/csv'
            })

            sold_fields, sold_columns = self._get_fields_and_columns(import_sold_id, 'sale.order.line.delivery', data, options)
            # print(sold_fields, sold_columns)
            import_sold_result = import_sold_id.do(sold_fields, sold_columns, options)
            result_lst = import_sold_result.get('ids')

            if not result_lst:
                raise ValidationError(_('Cannot upload input file. \n'
                                        '{}'.format(import_sold_result.get('messages'))))

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