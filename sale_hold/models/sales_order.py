from odoo import models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime

class SaleOrder(models.Model):

    _inherit = 'sale.order'
    order_holds = fields.Many2many('sale.hold' ,string='Order Holds')
    state = fields.Selection(selection_add=[('hold', 'On Hold')])
    on_production_hold = fields.Boolean(string='On Production Hold')
    on_hold = fields.Boolean(string='On Hold')

    @api.multi
    def write(self, values):
        changed = self.filtered(
            lambda u: any(u[f] != values[f] if f in values else False
                          for f in {'order_holds'}))
        for order in changed:
            message_text = ''
            changed_holds = values['order_holds']
            for cache in order._cache._record.order_holds:
                hasGroup = False
                exists = any(cache.id == hol for hol in changed_holds[0][2])
                if not exists:
                    for grp in cache.group_ids:
                        rec_dic = grp.get_external_id()
                        rec_list = list(rec_dic.values())
                        rec_id = rec_list[0]
                        if self.env.user.has_group(rec_id):
                            hasGroup = True
                    if len(cache.group_ids) == 0:
                        hasGroup = True
                    if not hasGroup:
                        raise Warning('Cannot delete hold due to security on hold ')
                    else:
                        message_text = message_text + 'Removed Hold ' + cache.name + '<br/>'
            for item in changed_holds[0][2]:
                old = any(item == hol.id for hol in order.order_holds)

                if not old:
                    hold_obj = self.env['sale.hold']
                    holds = hold_obj.search([('id', '=',
                                                      item)])
                    for hold in holds:
                        message_text = message_text + 'Removed Hold ' + hold.name + ' <br/>'
            if message_text != '':
                order.message_post(body=message_text)
        return super(SaleOrder, self).write(values)
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
            if order.on_hold:
                order.state = 'hold'

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