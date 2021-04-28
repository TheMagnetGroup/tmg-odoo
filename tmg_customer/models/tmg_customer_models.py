# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Buying group model
class BuyingGroup(models.Model):
    _name = 'partner.buying.group'
    _description = 'Buying Groups'
    _order = 'name'

    name = fields.Char(string='Buying Group', required=True)
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")


class tmg_customer(models.Model):

    _inherit = 'res.partner'

    Rebate = fields.Boolean()
    buying_group_id = fields.Many2one('partner.buying.group', string='Buying Group', track_visibility='onchange', copy=False)
    legacy_customer_number = fields.Char('Legacy Customer Number', copyf=False, required=False)

    _sql_constraints = [
        ('customer_number_uniq', 'unique (legacy_customer_number)', "Legacy customer number already exists!"),
    ]

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # buying_group_id = fields.Many2one('partner.buying.group', string='Buying Group')

    # @api.onchange('partner_id')
    # def _set_buying_group(self):
    #     if self.partner_id:
    #         if self.partner_id.buying_group_id:
    #             self.buying_group_id = self.partner_id.buying_group_id
    #         elif self.partner_id.parent_id.buying_group_id:
    #             self.buying_group_id = self.partner_id.parent_id.buying_group_id

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        bg_id = None
        # Look for a buying group anywhere in the account/parent hierarchy
        p_id = self.partner_id
        while p_id:
            if p_id.buying_group_id:
                bg_id = p_id.buying_group_id.id
                break
            p_id = p_id.parent_id

        if bg_id:
            invoice_vals.update({
                'buying_group_id': bg_id
            })
        return invoice_vals


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    buying_group_id = fields.Many2one('partner.buying.group', string='Buying Group')


# class SaleReport(models.Model):
#     _inherit = 'sale.report'
#
#     buying_group = fields.Char('Buying Group', readonly=True)
#
#     def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
#         fields['buying_group'] = ', bg.name as buying_group'
#
#         groupby += ', bg.name'
#
#         from_clause += 'left join partner_buying_group bg on (s.buying_group_id = bg.id)'
#
#         return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    buying_group = fields.Char('Buying Group', readonly=True)

    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        select_str += ', sub.buying_group'
        return select_str

    def _sub_select(self):
        select_str = super(AccountInvoiceReport, self)._sub_select()
        select_str += ', bg.name as buying_group'
        return select_str

    def _from(self):
        from_str = super(AccountInvoiceReport, self)._from()
        from_str += ' left join partner_buying_group bg on ai.buying_group_id = bg.id'
        return from_str

    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        group_by_str += ', bg.name'
        return group_by_str