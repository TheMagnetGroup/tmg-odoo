# -*- coding: utf-8 -*-

from odoo import models, api, fields


class invoice(models.Model):
    _name = 'tmg_external_api.invoice'
    _description = 'Serve customer invoice information'

    # provide common calculation components
    _inv_sales_total = float(0.0)
    _inv_ship_total = float(0.0)
    _inv_handling = float(0.0)
    _inv_payments_down = float(0.0)

# ------------------
#  Public functions
# ------------------

    @api.model
    def Invoice(self, partner_str, po, invoice_number, invoice_date_str, as_of_date_str):
        invoice_data = []
        sales_order = dict()   # initial release expects only 1 order; return dict() instead of list[dict()]

        # a partner ID is required
        if not (partner_str and partner_str.strip()):
            return invoice_data

        # one query search value is required (1st value found is used, validated in the sequence below)
        search = [('partner_id', '=', int(partner_str))]
        if invoice_number and invoice_number.strip():
            search.append(('number', '=', invoice_number))
        elif po and po.strip():
            sales_order = self._get_sale_orders(po, '')
            if sales_order:
                search.append(('origin', '=', sales_order['name']))
            else:
                return invoice_data
        elif invoice_date_str and invoice_date_str.strip():
            inv_date = fields.Date.from_string(invoice_date_str)
            search.append(('date_invoice', '=', inv_date))
        elif as_of_date_str and as_of_date_str.strip():
            inv_available = fields.Datetime.from_string(as_of_date_str)
            search.append(('date_invoice', '>=', inv_available))
        else:
            return invoice_data

        invoice_data = self._get_invoices(search, sales_order)

        return invoice_data

# -------------------
#  Private functions
# -------------------

    @api.model
    def _get_invoices(self, invoice_search, so):
        invoice_data = []

        # obtain the main invoice level data
        invoices = self.env['account.invoice']\
            .search_read(invoice_search,
                         ['id',
                          'number',
                          'type',
                          'date_invoice',
                          'partner_id',
                          'payment_term_id',
                          'date_due',
                          'currency_id',
                          'origin',
                          'invoice_line_ids',
                          'amount_tax',
                          'amount_total',
                          'residual',
                          'tax_line_ids']
                         )
        # load the return list with a dict() for each invoice found
        for i in invoices:
            invoice._inv_ship_total = 0.0
            invoice._inv_handling = 0.0
            invoice._inv_sales_total = 0.0
            invoice._inv_payments_down = 0.0

            invoice_so_number = i['origin']
            invoice_type = ("CREDIT MEMO" if i['type'] == 'out_refund' else "INVOICE")

            if not so:
                # credit memo "origin" doc is actually the related invoice; use to override with correct sales order
                if invoice_type == "CREDIT MEMO":
                    rel_invoice_search = [('partner_id', '=', i['partner_id'][0]),
                                          ('number', '=', i['origin'])]
                    rel_i = self.env['account.invoice'] \
                        .search_read(rel_invoice_search,
                                     ['id',
                                      'number',
                                      'type',
                                      'date_invoice',
                                      'partner_id',
                                      'origin']
                                     )
                    invoice_so_number = rel_i[0]['origin'] if rel_i else ''
                so = self._get_sale_orders('', invoice_so_number)

            # create a list of address tuples for obtaining bill-to/sold-to account info
            bil_id = ("BILL TO", int(i['partner_id'][0]))
            sol_id = ("SOLD TO", int(so['partner_id'][0])) if so else tuple()
            list_contacts = [bil_id, sol_id]
            account_addresses = self._address_fmt(list_contacts)
            invoice_comments = (("Related Document: " + i['origin']) if invoice_type == "CREDIT MEMO" else '')

            # obtain line and tax info as lists formatted for the invoice dict() return value
            txs = (self._get_taxes(i['tax_line_ids']) if float(i['amount_tax']) != 0.0 else [])
            lns = self._get_lines(i['invoice_line_ids'])

            # populate the dict() of data for the invoice
            if not lns:
                data = dict(
                            errorList=[dict(
                                code=999,
                                severity='Error',
                                message="Invoice " + i['number'] + " found but invoice lines failed or missing")
                                ]
                            )
            else:
                inv_amt_calc = (invoice._inv_sales_total
                                + invoice._inv_ship_total
                                + invoice._inv_handling
                                + float(i['amount_tax']))
                if inv_amt_calc == 0:
                    # possibly no products actually sold/shipped, but a prior balance or adjustment is carried over
                    inv_amt_calc = float(i['amount_total'])
                data = dict(
                    errorList=[],
                    invoiceNumber=i['number'],
                    invoiceType=invoice_type,
                    invoiceDate=fields.Date.to_string(i['date_invoice']),
                    purchaseOrderNumber=(so['client_order_ref'] if so else ''),
                    addresses=account_addresses,
                    comments=invoice_comments,
                    paymentTerms=(i['payment_term_id'][1] if i['payment_term_id'] else ''),
                    paymentDueDate=fields.Date.to_string(i['date_due']),
                    currency=i['currency_id'][1],
                    fob=(so['warehouse_id'][1] if so else ''),
                    salesAmount=invoice._inv_sales_total,
                    shippingAmount=invoice._inv_ship_total,
                    handlingAmount=invoice._inv_handling,
                    taxAmount=float(i['amount_tax']),
                    invoiceAmount=inv_amt_calc,
                    advancePaymentAmount=invoice._inv_payments_down,
                    invoiceAmountDue=float(i['amount_total']),
                    lineItems=lns,
                    salesOrderNumbers=[invoice_so_number],
                    taxes=txs
                    )
            invoice_data.append(data)
            # force fresh retrieval of the sales order for the next invoice
            so = dict()
        if len(invoice_data) == 0:
            invoice_data = [dict(
                                errorList=[dict(
                                    code=903,
                                    severity='Information',
                                    message="No Invoices found")
                                    ]
                                )
                            ]
        return invoice_data

    @api.model
    def _get_sale_orders(self, po_number, order_number):
        order_fields = [
            'name',
            'client_order_ref',
            'partner_id',
            'warehouse_id'
        ]
        order_data = []
        # lookup corresponding order info if order number was specified
        if order_number and order_number.strip():
            order_data = self.env['sale.order']\
                .search_read([('name', '=', order_number)], order_fields)
        # ... otherwise, lookup corresponding order info by the original requested PO
        elif po_number and po_number.strip():
            order_data = self.env['sale.order']\
                .search_read([('client_order_ref', '=', po_number)], order_fields)
        # as of initial release, only one sales order per invoice is expected (hence element[0])
        # if in the future one invoice can correspond to multiple orders, modify to return a list
        if order_data and len(order_data) > 0:
            return order_data[0]
        else:
            return dict()

    @api.model
    def _get_lines(self, line_ids):
        lines_data = []
        lines = self.env['account.invoice.line']\
            .search_read([('id', 'in', line_ids)],
                         ['id',
                          'product_id',
                          'quantity',
                          'uom_id',
                          'name',
                          'price_unit',
                          'price_subtotal',
                          'price_total']
                         )
        for li in lines:
            _isDownPmt = False
            _isForShipping = False
            line_product = ''
            line_part = ''
            line_charged = ''
            # obtain specific line item product info
            if li['product_id']:
                pp = self.env['product.product']\
                    .search_read([('id', '=', int(li['product_id'][0]))],
                                 ['id',
                                  'product_tmpl_id',
                                  'product_style_number',
                                  'default_code']
                                 )
                if pp:
                    _isDownPmt = True if (pp[0]['default_code'] == "DOWN") else False
                    # some generic-template level product data is also required
                    pt = self.env['product.template'] \
                        .search_read([('id', '=', int(pp[0]['product_tmpl_id'][0]))],
                                     ['id',
                                      'default_code',
                                      'categ_id',
                                      'type']
                                     )
                    category = []
                    if pt:
                        line_product = pp[0]['product_style_number'] \
                            if (pt[0]['type'] in ['product', 'consu']) and pp[0]['product_style_number'] else ''
                        line_charged = pt[0]['default_code'] \
                            if (pt[0]['type'] == 'service') and pt[0]['default_code'] else ''
                        line_part = pp[0]['default_code'] \
                            if (pt[0]['type'] in ['product', 'consu']) and pp[0]['default_code'] else ''
                        category = self.env['product.category'] \
                            .search_read([('id', '=', int(pt[0]['categ_id'][0]))], ['name'])
                        _isForShipping = True if (category and category[0]['name'] == "Delivery") else False
                # advance/"down" payments are listed as a line item "product"; reverse sign and accumulate
                if _isDownPmt:
                    invoice._inv_payments_down += (0 - float(li['price_total']))
                # shipping and sales items are distinguished by category
                elif _isForShipping:
                    invoice._inv_ship_total += float(li['price_total'])
                else:
                    invoice._inv_sales_total += float(li['price_total'])
            else:
                line_product = ''
                line_part = ''
                line_charged = ''
            data = dict(
                lineItemNumber=int(li['id']),
                productId=line_product,
                partId=line_part,
                charged=line_charged,
                orderedQty=float(li['quantity']),
                invoiceQty=float(li['quantity']),
                qtyUOM=(li['uom_id'][1] if li['uom_id'] else ''),
                lineItemDescription=str(li['name'].replace('\n', ' ')),
                unitPrice=float(li['price_unit']),
                extendedPrice=float(li['price_subtotal'])
            )
            lines_data.append(data)
        return lines_data

    @api.model
    def _address_fmt(self, list_partner):
        address_info = []
        for p in list_partner:
            if p != tuple():
                ad = self.env['res.partner'].search_read([('id', '=', p[1])])
                if ad:
                    data = dict(
                        addressCode=p[0],
                        accountName=str(ad[0]['name'].replace('\n', ' ')),
                        accountNumber=int(ad[0]['id']),
                        attentionTo="",
                        address1=ad[0]['street'] if ad[0]['street'] else '',
                        address2=ad[0]['street2'] if ad[0]['street2'] else '',
                        address3="",
                        city=ad[0]['city'],
                        region=ad[0]['state_id'][1],
                        postalCode=ad[0]['zip'],
                        country=ad[0]['country_id'][1],
                        email=ad[0]['email'] if ad[0]['email'] else '',
                        phone=ad[0]['phone'] if ad[0]['phone'] else ''
                    )
                    address_info.append(data)
        return address_info

    @api.model
    def _get_taxes(self, tax_line_ids):
        tax_line_data = []
        tax_lines = self.env['account.invoice.tax'].search_read([('id', 'in', tax_line_ids)], ['name', 'amount'])
        for tl in tax_lines:
            tax_info = dict(
                taxType="SALES",
                taxJurisdiction=tl['name'],
                taxAmount=float(tl['amount'])
            )
            # taxType designation criteria may change if we ever start having to charge HST/GST, PST or VAT
            tax_line_data.append(tax_info)
        return tax_line_data
