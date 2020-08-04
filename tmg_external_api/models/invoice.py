# -*- coding: utf-8 -*-

from odoo import models, api, fields


class invoice(models.Model):
    _name = 'tmg_external_api.invoice'
    _description = 'Serve customer invoice information'

    # these facilitate common access to identifiers
    _partner_id = fields.Integer(0)
    _invoice = fields.Char(None)
    _po = fields.Char(None)
    _inv_date = fields.Date(None)
    _inv_available = fields.Datetime(None)

    # these provide common calculation components
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

        # a partner ID is required
        if partner_str and partner_str.strip():
            invoice._partner_id = int(partner_str)
        else:
            return invoice_data

        # one query search value is required (1st value found is used, validated in the sequence below)
        if invoice_number and invoice_number.strip():
            invoice._invoice = invoice_number
        elif po and po.strip():
            invoice._po = po
        elif invoice_date_str and invoice_date_str.strip():
            invoice._inv_date = fields.Date.from_string(invoice_date_str)
        elif as_of_date_str and as_of_date_str.strip():
            invoice._inv_available = fields.Datetime.from_string(as_of_date_str)
        else:
            return invoice_data

        invoice_data = self._get_invoices()

        return invoice_data

# -------------------
#  Private functions
# -------------------

    @api.model
    def _get_invoices(self):
        so = dict()   # a/o initial release return dict() instead of list[]
        invoice_data = []

        # obtain the main invoice level data
        invoice_search = [('partner_id', '=', invoice._partner_id)]
        if invoice._invoice:
            invoice_search.append(('number', '=', invoice._invoice))
        elif invoice._inv_date:
            invoice_search.append(('date_invoice', '=', invoice._inv_date))
        elif invoice._inv_available:
            invoice_search.append(('date_invoice', '>=[bil_id, sol_id]', invoice._inv_available))
        elif invoice._po:
            so = self._get_sale_orders()
            invoice_search.append(('origin', '=', so['number']))
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
            if not so:
                so = self._get_sale_orders(i['origin'])

            # create a list of address tuples for obtaining bill-to/sold-to account info
            bil_id = ("BILL TO", int(i['partner_id'][0]))
            sol_id = ("SOLD TO", int(so['partner_id'][0])) if so else tuple()
            list_contacts = [bil_id, sol_id]
            account_addresses = self._address_fmt(list_contacts)

            # obtain line and tax info as lists formatted for the invoice dict() return value
            txs = (self._get_taxes(i['tax_line_ids']) if float(i['amount_tax']) != 0.0 else [])
            lns = self._get_lines(i['invoice_line_ids'])

            # populate the dict() of data for the invoice
            if not lns:
                data = dict(
                            errorList=[dict(
                                severity='Warning',
                                message='Error returning invoice lines or lines not found')
                                ]
                            )
            else:
                data = dict(
                    errorList=[],
                    invoiceNumber=i['number'],
                    invoiceType=("CREDIT MEMO" if i['type'] == 'out_refund' else "INVOICE"),
                    invoiceDate=fields.Date.to_string(i['date_invoice']),
                    purchaseOrderNumber=so['client_order_ref'],
                    addresses=account_addresses,
                    paymentTerms=i['payment_term_id'][1],
                    paymentDueDate=fields.Date.to_string(i['date_due']),
                    currency=i['currency_id'][1],
                    fob=so['warehouse_id'][1],
                    salesAmount=invoice._inv_sales_total,
                    shippingAmount=invoice._inv_ship_total,
                    handlingAmount=invoice._inv_handling,
                    taxAmount=float(i['amount_tax']),
                    invoiceAmount=float(i['amount_total']),
                    advancePaymentAmount=invoice._inv_payments_down,
                    invoiceAmountDue=float(i['amount_total']) - invoice._inv_payments_down,
                    lineItems=lns,
                    salesOrderNumbers=[i['origin']],
                    taxes=txs
                    )
            invoice_data.append(data)

        return invoice_data

    @api.model
    def _get_sale_orders(self, order_number):
        order_fields = [
            'number',
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
        elif invoice._po and invoice._po.strip():
            order_data = self.env['sale.order']\
                .search_read([('client_order_ref', '=', invoice._po)], order_fields)
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
            # obtain specific line item product info
            pp = self.env['product.product']\
                .search_read([('id', '=', int(li['product_id'][0]))],
                             ['id',
                              'product_tmpl_id',
                              'product_style_number',
                              'default_code']
                             )
            # advance payments are listed as a line item "product"; accumulate total if found
            if pp[0]['default_code'] == "DOWN":
                invoice._inv_payments_down += float(li['price_total'])
            # some generic-template level product data is also required
            pt = self.env['product.template']\
                .search_read([('id', '=', int(pp[0]['product_tmpl_id'][0]))],
                             ['id',
                              'default_code',
                              'categ_id',
                              'type']
                             )
            # accumulate various invoice totals based on the line item category
            category = self.env['product.category']\
                .search_read([('id', '=', int(pt[0]['categ_id'][0]))], ['name'])
            if category[0] == "Delivery":
                invoice._inv_ship_total += float(li['price_total'])
            else:
                invoice._inv_sales_total += float(li['price_total'])
            data = dict(
                lineItemNumber=int(li['id']),
                productId=(pp[0]['product_style_number'] if pt[0]['type'] in ['product', 'consu'] else ''),
                partId=(pp[0]['default_code'] if pt[0]['type'] in ['product', 'consu'] else ''),
                charged=(pt[0]['default_code'] if pt[0]['type'] == 'service' else ''),
                orderedQty=float(li['quantity']),
                invoiceQty=float(li['quantity']),
                qtyUOM=li['uom_id'][1],
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
            ad = self.env['res.partner'].search_read([('id', '=', p[1])])
            if ad:
                data = dict(
                    addressCode=p[0],
                    accountName=str(ad[0]['name'].replace('\n', ' ')),
                    accountNumber=int(ad[0]['id']),
                    attentionTo="",
                    address1=ad[0]['street'],
                    address2=ad[0]['street2'],
                    address3="",
                    city=ad[0]['city'],
                    region=ad[0]['state_id'][1],
                    postalCode=ad[0]['zip'],
                    country=ad[0]['country_id'][1],
                    email=ad[0]['email'],
                    phone=ad[0]['phone']
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
