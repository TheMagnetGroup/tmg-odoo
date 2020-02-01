from odoo import models, fields, api, exceptions
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_launch_stock_rule(self):
        res = super(SaleOrderLine, self)._action_launch_stock_rule()
        orders = list(set(x.order_id for x in self))
        for order in orders:
            order.CheckHolds()
        return res

class SaleOrder(models.Model):

    _inherit = 'sale.order'
    order_holds = fields.Many2many('sale.hold' ,string='Order Holds')

    on_hold = fields.Boolean(string='On Hold')
    approved_credit = fields.Boolean(string='Approved Credit', default=False)
    had_credit_hold = fields.Boolean(string="Had Credit Hold", default=False)
    is_automated_hold = fields.Boolean(string = "Automated Credit Hold", default=False)
    on_production_hold = fields.Boolean(string="On Production Hold", default=False)


    def checkSecurity(self, value):
        hasGroup = False
        for grp in value.group_ids:
            rec_dic = grp.get_external_id()
            rec_list = list(rec_dic.values())
            rec_id = rec_list[0]
            if self.env.user.has_group(rec_id):
                hasGroup = True
        if len(value.group_ids) == 0:
            hasGroup = True
        if not hasGroup:
            return False

        else:
            return True

    @api.model
    def create(self, values):
        vals = values['order_holds']
        note_list = []
        if 'payment_term_id' not in values:


            cust_obj = self.env['res.partner']
            custNmbr = values['partner_id']
            cust = cust_obj.search([('id', '=', custNmbr)])
            values.update({'payment_term_id' : cust.property_payment_term_id.id})
        if vals:
            for t in vals[0][2]:
                hold_obj = self.env['sale.hold']
                holds = hold_obj.search([('id', '=', t)])
                for hold in holds:
                    hasGroup = self.checkSecurity(hold)
                    if not hasGroup:
                        if self.is_automated_hold and hold.credit_hold:
                            nothold = True
                        else:
                            raise Warning('Cannot add hold due to security on hold.')


                    else:
                        note_list.append('Added Hold ' + hold.name)
                        # message_text = message_text + 'Added Hold ' + hold.name + ' <br/>'

        result = super(SaleOrder, self).create(values)
        message_text = self.create_ul_from_list(note_list)
        if message_text != '':
            self.message_post(body=message_text)
        return result




    @api.multi
    def write(self, values):
        'Make sure to ignore any changes that do not affect order_holds'
        changed = self.filtered(
            lambda u: any(u[f] != values[f] if f in values else False
                          for f in {'order_holds'}))
        had_credit_hold = False
        for order in changed:
            note_list = []
            message_text = ''
            'Grab IDs of the records that have been changed'
            changed_holds = values['order_holds']
            # had_credit_hold = any(hol.credit_hold == True for hol in order._cache.record.order_holds)
            # has_credit_hold = False
            'Check to see if one of the changed holds is a removal'
            for cache in order._cache._record.order_holds:
                hasGroup = False
                exists = any(cache.id == hol for hol in changed_holds[0][2])

                'if it is a removal, check to see if the current user has permission to remove'
                if not exists:

                    hasGroup = self.checkSecurity(cache)
                    if not hasGroup:
                        raise Warning('Cannot delete hold due to security on hold ')
                    else:
                        note_list.append('Removed Hold ' + cache.name)
                       # message_text = message_text + 'Removed Hold ' + cache.name + ' <br/>'
            'Check to see if one of the changed holds is an addition'
            for item in changed_holds[0][2]:
                old = any(item == hol.id for hol in order.order_holds)
                if not old:
                    'if it is an additional hold, load the hold object from its ID'
                    hold_obj = self.env['sale.hold']
                    holds = hold_obj.search([('id', '=',item)])
                    if holds.credit_hold == True:
                        values.update({'had_credit_hold': True})

                    'if it is an addition, check to see if the current user has permission to add'
                    for hold in holds:
                        hasGroup = self.checkSecurity(hold)
                        if not hasGroup:
                            if self.is_automated_hold and hold.credit_hold:
                                nothold = True
                            else:
                                raise Warning('Cannot add hold due to security on hold.')


                        else:
                            note_list.append('Added Hold ' + hold.name)
                            #message_text = message_text + 'Added Hold ' + hold.name + ' <br/>'
                    values.update({'is_automated_hold': False})
            # if had_credit_hold:
            #     if not has_credit_hold:
            #         order.approved_credit = False
            message_text = self.create_ul_from_list(note_list)
            if message_text != '':
                order.message_post(body=message_text)



            credit_hold = False
            has_hold = False
            for hol in order.order_holds:


                had_hold = True

                if hol.credit_hold:
                    if not order.had_credit_hold:
                        values.update({'had_credit_hold': True})
                        #order.had_credit_hold = True
                    credit_hold = True
                    if order.approved_credit:
                        values.update({'approved_credit': False})
                        #order.approved_credit = False
                    break

            if not credit_hold:
                if order.had_credit_hold:
                    values.update({'had_credit_hold': False})
                    #order.had_credit_hold = False
            if has_hold == True:
                values.update({'on_hold': True})
                #order.on_hold = True
            else:
                if order.on_hold != False:
                    values.update({'on_hold': False})
                    #order.on_hold = False

        result = super(SaleOrder, self).write(values)


        return result


    def create_ul_from_list(self, ulist):
        output = ''
        if len(ulist) > 0:
            output = '<ul>'
            for line in ulist:
                output = output + ' <li>' + line + '</li>'
            output = output + ' </ul>'
        return   output

    @api.multi
    def CheckHolds(self):
        for order in self:
            hasShippingBlock = False
            hasProductionBlock = False
            if len(order.order_holds) > 0:
                hasShippingBlock = False
                hasProductionBlock = False
                for hold in order.order_holds:
                    if hold.blocks_production:
                        hasProductionBlock = True
                    if hold.blocks_delivery:
                        hasShippingBlock = True
                # if hasShippingBlock:
                #
                #     order.on_hold = True
                # else:
                #     for pi in self.picking_ids:
                #         order.picking_ids.write({'on_hold': False})
                #         order.picking_ids.write({'on_hold_text': ''})
                # if hasProductionBlock:
                #     for li in self.order_line:
                #         li.job_id.write({'on_hold': True})
                #         # for mo in li.job_id.mfg_order_ids:
                #         #     mo.on_hold = True
                #     order.on_production_hold = True
                #     order.on_hold = True
                # else:
                #     for li in self.order_line:
                #         li.job_id.write({'on_hold': False})
                #         # for mo in li.job_id.mfg_order_ids:
                #         #     mo.on_hold = False
                #     order.on_production_hold = False
            self.set_holds(hasShippingBlock, hasProductionBlock)
            if hasProductionBlock and hasShippingBlock:
                order.on_production_hold = True

            else:
                order.on_production_hold = False


            if len(order.order_holds) == 0:
                order.on_hold = False
                for pi in self.picking_ids:
                    order.picking_ids.write({'on_hold': False})
                    order.picking_ids.write({'on_hold_text': ''})
                for li in self.order_line:
                    li.job_id.write({'on_hold': False})
            else:
                order.on_hold = True
            if any(hol.credit_hold == True for hol in order.order_holds):
                order.approved_credit = False
            else:
                if order.had_credit_hold:
                    order.approved_credit = True

    @api.multi
    @api.onchange('order_holds')
    def on_hold_change(self):
        self.CheckHolds()

    def set_holds(self, ship, prod):
        if ship:
            for pi in self.picking_ids:
                self.picking_ids.write({'on_hold': True})
                self.picking_ids.write({'on_hold_text': 'On Hold'})
            self.on_hold = True
            for li in self.order_line:
                li.job_id.write({'on_hold': True})
        else:
            for pi in self.picking_ids:
                self.picking_ids.write({'on_hold': False})
                self.picking_ids.write({'on_hold_text': ''})
        if prod:
            for li in self.order_line:
                li.job_id.write({'on_hold': True})
                li.job_id.write({'on_production_hold': True})
                for mo in li.production_order:
                    mo.write({'on_hold': True})
                    mo.write({'on_hold_text': "On Hold"})
                    for wo in mo.workorder_ids:
                        wo.write({'on_hold': True})


            for pi in self.picking_ids:
                self.picking_ids.write({'on_hold': True})
                self.picking_ids.write({'on_hold_text': 'On Hold'})

            self.on_production_hold = True
            self.on_hold= True
        else:
            for li in self.order_line:
                li.job_id.write({'on_production_hold': False})
                for mo in li.production_order:
                    mo.write({'on_hold': False})
                    mo.write({'on_hold_text': ""})
                    for wo in mo.workorder_ids:
                        wo.write({'on_hold': True})
            if not ship:
                for li in self.order_line:
                    li.job_id.write({'on_hold': False})
                for pi in self.picking_ids:
                    self.picking_ids.write({'on_hold': False})
                    self.picking_ids.write({'on_hold_text': ''})


            self.on_production_hold = False




    @api.multi
    def check_limit(self):

        self.ensure_one()
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search([('partner_id', '=',
                partner.id), ('account_id.user_type_id.name', 'in',
                ['Receivable', 'Payable']), ('full_reconcile_id', '=',
                False)])
        order_obj = self.env['sale.order']
        orders = order_obj.search([('partner_id', '=', partner.id),
                                           ('state', '=', 'sale')])


        (debit, credit) = (0.0, 0.0)

        today_dt = datetime.strftime(datetime.now().date(), DF)

        for line in movelines:
            credit += line.debit
            debit += line.credit
        for lines in orders:
            credit += lines.amount_total

        if credit - debit + self.amount_total > partner.credit_limit:
            hold = self.env['sale.hold']
            hold_ids = hold.search([('credit_hold', '=', 'True')])

           # holdsObj = hold.browse(hold_ids)

           # self.order_holds.write({''}) = holdsObj
            self.is_automated_hold = True
            self.order_holds = self.order_holds | hold_ids

           # res = self.write({'order_holds': holdsObj})
            # return res

    @api.multi
    def action_confirm(self):
        has_stop_hold = False
        for order in self:
            if not order.approved_credit:
                if order.payment_term_id.auto_credit_check:
                    order.check_limit()
            if len(order.order_holds) > 0:
                for hold in order.order_holds:
                    if hold.blocks_production or hold.credit_hold:
                        has_stop_hold = True


            ret = super(SaleOrder, self).action_confirm()

            self.CheckHolds()


