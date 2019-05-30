# -*- coding: utf-8 -*-


from datetime import datetime
from odoo import models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class SalesHold(models.Model):

    _name = 'sale.hold'
    _description = "Order Hold"
    name = fields.Char(string="Name")
    blocks_production = fields.Boolean(string="Blocks Production")
    blocks_delivery = fields.Boolean(string="Blocks Delivery")
    color = fields.Char(string="Color")
    active = fields.Boolean(string="Active")
    group_ids = fields.Many2many("res.groups", string="Security Group")
    credit_hold = fields.Boolean(string="Credit Hold")
    promostandards_hold_description = fields.Char(string="Promostandards Hold Description")
  #  sales_order_ids = fields.Many2many("sale.order", string = "Sales Orders")


    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Allows to delete sales order lines in draft,cancel states"""
        hasGroup = False
        for rec in self.browse(cr, uid, ids, context=context):

            for grp in rec.group_ids:
                if self.env.user.has_group(rec.id):
                    hasGroup = True
            if not hasGroup :
                raise exceptions.except_osv(('Invalid Action!'), ('Cannot delete hold due to security \'%s\'.') % (rec.state,))
        return super(SalesHold, self).unlink(cr, uid, ids, context=context)

class SaleOrder(models.Model):

    _inherit = 'sale.order'
    order_holds = fields.Many2many('sale.hold',
                                   string='Order Holds')
    state = fields.Selection(selection_add=[('hold', 'On Hold')])
    on_production_hold = fields.Boolean(string='On Production Hold')
    on_hold = fields.Boolean(string='On Hold')

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#

    # def menu_on_hold(
    #     self,
    #     cr,
    #     uid,
    #     ids,
    #     context=None,
    #     ):
    #     res = self.write(cr, uid, ids, {'state': 'hold'},
    #                      context=context)
    #     return res

    @api.multi
    @api.onchange('order_holds')
    def on_hold_change(self):
        for order in self:
            if len(order.order_holds) > 0:
                hasShippingBlock = False
                hasProductionBlock = False
                for hold in order.order_holds:
                    if hold.blocks_production:
                        hasProductionBlock = True
                    if hold.blocks_delivery:
                        hasShippingBlock = True
                if hasShippingBlock:
                    for pi in self.picking_ids:
                        order.picking_ids.write({'on_hold': True})
                        order.on_hold = True
                else:
                    for pi in self.picking_ids:
                        order.picking_ids.write({'on_hold': False})
                if hasProductionBlock:
                    order.on_production_hold = True
                    order.on_hold = True
                else:
                    order.on_production_hold = False
            if len(order.order_holds) == 0:
                order.on_hold = False

    @api.multi
    def check_limit(self):

        self.ensure_one()

        partner = self.partner_id

        moveline_obj = self.env['account.move.line']

        movelines = moveline_obj.search([('partner_id', '=',
                partner.id), ('account_id.user_type_id.name', 'in',
                ['Receivable', 'Payable']), ('full_reconcile_id', '=',
                False)])

        (debit, credit) = (0.0, 0.0)

        today_dt = datetime.strftime(datetime.now().date(), DF)

        for line in movelines:

            if datetime.strftime(line.date_maturity, DF) < today_dt:
                credit += line.debit
                debit += line.credit

        if credit - debit + self.amount_total > partner.credit_limit:
            hold = self.env['sale.hold']
            hold_ids = hold.search([('credit_hold', '=', 'True')]).id

            holdsObj = hold.browse(hold_ids)

           # self.order_holds.write({''}) = holdsObj

            self.order_holds = holdsObj

           # res = self.write({'order_holds': holdsObj})
            # return res

    @api.multi
    def _action_confirm(self):

        for order in self:
            if order.payment_term_id.auto_credit_check:
                order.check_limit()
            if len(order.order_holds) > 0:
                for hold in order.order_holds:
                    if hold.blocks_production:

                        if order.state == 'hold':
                            raise Warning('Order cannot be committed with production holds'
                                    )
                        order.state = 'hold'
                        return
        super(SaleOrder, self)._action_confirm()