# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
	_inherit = "mrp.routing.workcenter"

	attribute_value_ids = fields.Many2many('product.attribute.value', 'routing_workcenter_prod_attribute_value_rel', 'workcenter_id', 'attr_value_id', string="Attribute Values",
		                                    help="Attribute values for which workorder for this operation shuold gets created.")
