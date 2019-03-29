# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import logging
from datetime import datetime,time
import odoo.modules as addons
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta
class bucket_filter(models.Model):
    _name = 'pr1_s3.bucket_filter'
    def _get_name(self):
        for record in self:
            if(record.res_model.id!=False and record.mime_type!=False):
                record.name=record.res_model.name+"-"+record.mime_type
            elif(record.res_model.id!=False):
                record.name=record.res_model.name
            else:
                record.name="Empty Filter"
                
        
    name = fields.Char(compute="_get_name",String="Name")
    res_model = fields.Many2one('ir.model', string="Model To Use", help="Select the model to use for this filter")
    mime_type=fields.Char("String Mime Types To Use", help="enter a , seperated list of mime types to upload: e.g. application/pdf,image/png,image/jpeg or leave blank for all",default=False)  
    s3_connection_id=fields.Many2one("pr1_s3.s3_connection",string="Linked Connection")