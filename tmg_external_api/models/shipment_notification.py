# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models, fields, api
import json


class shipment_notificaiton(models.Model):
    _name = 'tmg_external_api.shipment_notificaiton'


    def ShipmentNotification(self, PONumber, SONumber, LastUpdate, Partner_id):
            if LastUpdate == '':
                LastUpdate = '02/01/1990'
            sql = """SELECT sale.id
                        FROM sale_order as sale
                        join res_partner partner ON (partner.id = sale.partner_id)
                        join stock_picking pick ON (pick.sale_id = sale.id)
                        where (client_order_ref = %(PONumber)s or %(PONumber)s =  '')
                        and ((CAST(partner.id as VARCHAR(20)) = %(Partner_ID)s or CAST(partner.parent_id as VARCHAR(20)) = %(Partner_ID)s) or %(Partner_ID)s = '')
                        and (sale.name = %(SONumber)s or %(SONumber)s = '')
                        and (pick.date_done >= %(LastUpdate)s);"""
            params = {
                'PONumber': PONumber,
                'SONumber': SONumber,
                'LastUpdate': LastUpdate,
                'Partner_ID': Partner_id,
            }
            self.env.cr.execute(sql, params)
            orderObj = self.env['sale.order']

            itemList = []

            for val in self.env.cr.dictfetchall():
                order_id = val['id']
                order = orderObj.browse(order_id)
                complete = False
                if order.invoice_status == 'invoiced':
                    complete = True
                shipments = self.get_shipments(order)
                data = [

                    ('purchaseOrderNumber', '=', order.client_order_ref),
                    # ('parent_id', '=', partner_id.parent_id.id),
                    ('SalesOrderNumber', '=', order.name),
                    ('complete', '=', complete),
                    ('locations', '=', shipments)
                ]
                itemList.append(['Sales_order', '=', data])
            return itemList


    def get_shipments(self, sale):
        shipments = self.get_common_shipments(sale.picking_ids)
        location_array = []
        if shipments:

            for v in shipments:
                shipmentArray = []
                for record in v:

                    fromPartner =  self.get_address(record.location_id.warehouse_id.partner_id) or []
                    toPartner = self.get_address(record.partner_id) or []
                    packages = self.get_packages(record) or []

                    SONumber = sale.name
                    data = [

                        ('ship_from_address', '=', fromPartner),
                        # ('parent_id', '=', partner_id.parent_id.id),
                        ('shipToAddress', '=', toPartner),
                        ('packageArray', '=', packages)

                    ]
                    shipmentArray.append(['shipment', '=', data])
            location_array.append(['location', '=', shipmentArray])
        return location_array



    def get_packages(self, picking_id):
        packages = []
        for rec in picking_id.package_ids:
            data = [

                ('Carrier', '=', picking_id.carrier_id.delivery_type or 'Not Provided'),
                # ('parent_id', '=', partner_id.parent_id.id),
                ('tracking_number', '=', picking_id.carrier_tracking_ref or 'Not Provided'),
                ('shipment_date', '=', picking_id.date_done ),
                ('height', '=', rec.packaging_id.height or '0'),
                ('width', '=', rec.packaging_id.width or '0'),
                ('length', '=', rec.packaging_id.length or '0'),
                ('dimUOM', '=', '0'),
                ('weight', '=', rec.shipping_weight),
                ('ShipMethod', '=', picking_id.carrier_id.name)
            ]
            packages.append(['package', '=', data])
        return packages

    def get_address(self, partner_id):
        data = [

            ('Address1', '=', partner_id.street or 'Not Provided'),
            # ('parent_id', '=', partner_id.parent_id.id),
            ('Address2', '=', partner_id.street2 or 'Not Provided'),
            ('City', '=', partner_id.city or 'Not Provided'),
            ('State', '=', partner_id.state_id.name or 'NA'),
            ('Zip', '=', partner_id.zip or 'NA')
        ]
        return data

    def get_common_shipments(self, picking_ids):
        values = list(x.partner_id for x in picking_ids)
        cont = []
        for v in values:
            vals = []
            for p in picking_ids:
                if picking_ids.partner_id == v:
                    vals.append(p)
            cont.append(vals)
        return cont


