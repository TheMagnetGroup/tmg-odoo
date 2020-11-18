# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class DropShipWizard(models.TransientModel):
    _name = 'drop.ship.wizard'
    _description = 'Drop Shipment wizard'
