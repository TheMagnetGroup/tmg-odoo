# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class SaleOrderLineDeliveryEntryWizard(models.TransientModel):
    _name = 'sale.order.line.delivery.entry.wizard'
    _description = 'sale order line delivery entry wizard'

    # explicitly pass in context
    def _default_sol(self):
        return self.env['sale.order.line'].browse(self.env.context.get('active_ids'))[0]
    def _get_ups_service_types(self):
        return self.env['delivery.carrier']._get_ups_service_types()

    sale_line_id = fields.Many2one('sale.order.line', string='Active SOLs', ondelete='cascade', required=True, default=_default_sol)

    name = fields.Char(string='Name')
    street = fields.Char(string="Address1")
    street2 = fields.Char(string="Address2")
    city = fields.Char(string="City")
    state_id = fields.Many2one('res.country.state',string="State")
    Zip = fields.Char(string="Zip")
    country_id = fields.Many2one('res.country', string="Country")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    quantity = fields.Integer(string="Shipment Quantity")
    carrier_id = fields.Many2one('delivery.carrier' ,string="Delivery Carrier")
    ups_bill_my_account = fields.Boolean(related='carrier_id.ups_bill_my_account', readonly=True)
    ups_carrier_account = fields.Char(string='Carrier Account', copy=False)
    # ups_carrier_id = fields.Char(string="Carrier ID")
    ups_service_type = fields.Selection(_get_ups_service_types, string="UPS Service Type")
    # a helper function to set the criteria of what is considered a duplicate
    # for a customer contact

    # @api.constrains('ups_service_type')
    # def _validate_account(self):
    #     if self.ups_service_type:
    #         if not self.ups_carrier_id and self.ups_bill_my_account:
    #             raise ValidationError("You cannot select a third party shipper without supplying an account number")

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        self.ups_service_type = self.carrier_id.ups_default_service_type

    def _get_existing_partner_searching_domain(self, partner_id):
        return [
                    ('id', '!=', partner_id.id),
                    ('active', '=', True),
                    # ('parent_id', '=', partner_id.parent_id.id),
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
        if self.sale_line_id:

            partner_lst = []

            partner_obj = self.env['res.partner']
            new_partner = partner_obj.create({
                'active': True,
                'name': self.name,
                'street': self.street,
                'street2': self.street2,
                'city': self.city,
                'state': self.state_id,
                'zip': self.Zip,
                'country': self.country_id,
                'phone': self.phone,
                'email': self.email
            })
            partner_lst.append(new_partner)
            # go through our partner lst and unlink any duplicated ones
            # according to our duplicate domain
            corrected_partner_lst = []
            for i in range(len(partner_lst)):
                partner = partner_lst[i].id
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
            delOrd = self.env['sale.order.line.delivery']
            service_type = self.ups_service_type
            if self.carrier_id.delivery_type != "ups":
                service_type = False

            outOrd = delOrd.create({
                'carrier_id' : self.carrier_id.id,
                'shipping_partner_id': corrected_partner_lst[0],
                'sale_line_id': self.sale_line_id.id,
                'ups_carrier_account': self.ups_carrier_account,
                'ups_service_type': service_type,
                'qty': self.quantity,
            })
            # result_lst = self.do_import('sale.order.line.delivery', decoded_file, options)
            # result_lst = []
            # result_lst.append(outOrd)
            # for i in range(len(result_lst)):
            #     sold_id = self.env['sale.order.line.delivery'].browse(result_lst[i])
            #     if sold_id.qty:
            #         sold_id.write({
            #             'shipping_partner_id': corrected_partner_lst[i],
            #             'sale_line_id': self.sale_line_id.id
            #         })
            #     else:
            #         # delete when there is no delivery qty
            #         # but notice the contact will still be synced
            #         sold_id.unlink()

        return {'type': 'ir.actions.act_window_close'}