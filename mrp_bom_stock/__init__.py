# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import models
from . import report

from odoo import api, SUPERUSER_ID


def _update_locations(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    locations = env['stock.location'].search([('location_id', '!=', False), ('warehouse_id', '=', False)])
    for location in locations:
        location.warehouse_id = location.get_warehouse()
