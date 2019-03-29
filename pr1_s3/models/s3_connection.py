# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import logging
from datetime import datetime,time
import odoo.modules as addons
import os
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta
import random
import time
import base64
import hashlib
try:
    import boto3
except:
    _logger.debug('boto3 package is required!!')
import requests

_logger = logging.getLogger(__name__)

class S3Connection(models.Model):
    _name = 'pr1_s3.s3_connection'
        
    name = fields.Char(String="Name",help="A description of this connection to s3, e.g. for products..")
    s3_bucket_name=fields.Char("S3 Bucket Name")
    bucket_filters=fields.One2many("pr1_s3.bucket_filter","s3_connection_id",string="Bucket Filters")
    s3_access_key=fields.Char("S3 Access Key")
    s3_secret_key=fields.Char("S3 Secret Key")
    sub_folder=fields.Char("Sub Folder",help="This is the sub folder to use if you have multiple DBs you might want to store the data in a sub folder",default="")
    s3_api_url=password=fields.Char("S3 API URL", help="Leave blank if its Amazon S3",default="")
    test_connected=fields.Boolean("Test Connected",default=False,help="This will connect and attempt to push a file up to ensure the connection works.")
    for_all=fields.Boolean("Fallback", help="Tick this to make this work globally for all where no other is found or if you wish it to work globally")
    append_file_name_to_start=fields.Boolean("Append File Name",help="If you tick this the file name will be preserved and appended to the hex key folder e.g. /asdfgghss/abc.pdf - highly recommended",default=True)
    s3_location=fields.Char("Bucket Location",help="Defaults to S3 (leave blank if default bucket location",default="s3")
    s3_enabled=fields.Boolean("S3 Enabled", help="Disable this to turn off the auto upload of new attachments for this connection", default=True)
    test_file=fields.Binary("Test File", help="Please upload a test file in order to test the S3 Connection.",attachment=True)
            
    @api.multi
    def upload_all_existing(self):
        s = requests.session() 
        s.keep_alive = False
        for record in self:
            if(record.can_use(record)==False):
                continue
            connection=False
            connection=record
            s3_bucket,s3_service = connection.get_bucket()
            attachments2=[]
            attachments=False
            for filter in record.bucket_filters:
                if(filter.mime_type!=False):
                    comma_sep=[x.strip() for x in filter.mime_type.split(',')]
                    for ext in comma_sep:
                        attachments3=self.env['ir.attachment'].sudo().search([('res_model','=',filter.res_model.model),('mimetype','=',ext),('is_in_s3','=',False)]).ids
                        if(len(attachments3)>0):
                            attachments2+=attachments3
                else:
                    attachments2=attachments2+self.env['ir.attachment'].sudo().search([('res_model','=',filter.res_model.model),('is_in_s3','=',False)]).ids
            
            if(len(record.bucket_filters)==0):        
                attachments=self.env['ir.attachment'].sudo().search([('is_in_s3','=',False),('type','=','binary')])
            elif(len(attachments2)==0):
                continue
            else:
                attachments=self.env['ir.attachment'].sudo().browse(attachments2)
                
            attachments = attachments._filter_protected_attachments()
            attachments = attachments.filtered('datas')
            for attach in attachments:
                value = attach.datas
                bin_data = base64.b64decode(value) if value else b''
                
                fname = hashlib.sha1(bin_data).hexdigest()
        
                if(len(fname)>6): #small random fname
                    fname=fname[:6]
                
                fname=str(attach.id)+fname
                if(attach.datas_fname!=False):
                    Metadata={
                        'FileName': attach.datas_fname
                        }
                else:
                    Metadata={}
                
                if(connection.append_file_name_to_start):
                    if(attach.datas_fname!=False):
                        fname=fname+"/"+attach.datas_fname
                    else:
                        fname = hashlib.sha1(bin_data).hexdigest()
                if(connection.sub_folder!="" and connection.sub_folder!=False):
                    fname=connection.sub_folder+"/"+fname
                try:
                    s3_bucket.put_object(Key=fname,Body=bin_data,ACL='public-read',ContentType=attach.mimetype,Metadata=Metadata)
                except Exception as e:
                    raise exceptions.UserError(e.message)

                vals = {
                    'checksum': attach._compute_checksum(bin_data),
                    'url': connection.get_s3_url(fname,s3_service),
                    'file_size': len(bin_data),
                    'index_content': attach._index(bin_data, attach.datas_fname, attach.mimetype),
                    'is_in_s3':True,
                    'store_fname': fname,
                    'db_datas': False,
                    'type': 'url',
                }
                attach.write(vals)
    
    @api.multi
    def get_bucket(self):
        for record in self:
            s3_bucket=False
            if(record.s3_api_url!="" and record.s3_api_url!=False):
                s3_bucket = boto3.resource('s3',aws_access_key_id=record.s3_access_key,
                                        aws_secret_access_key=record.s3_secret_key,endpoint_url=record.s3_api_url)
            else:
                s3_bucket = boto3.resource('s3',aws_access_key_id=record.s3_access_key,
                                        aws_secret_access_key=record.s3_secret_key)
            bucket=s3_bucket.Bucket(record.s3_bucket_name)
            
            if not bucket:
                s3_bucket.create_bucket(Bucket=record.s3_bucket_name)
                
            return bucket,s3_bucket
    @api.multi
    def get_s3_url(self,file_name,s3_resource):
        object_url=False
        for record in self:
            if(record.s3_api_url=="" or record.s3_api_url==False):
                if(record.s3_location=='s3'):
                    bucket_location = s3_resource.meta.client.get_bucket_location(Bucket=record.s3_bucket_name)
                    location_constraint = bucket_location.get('LocationConstraint')
                    record.s3_location = location_constraint
                location_bit = 's3' + '-' + record.s3_location
                object_url = "https://{0}.amazonaws.com/{1}/{2}".format(location_bit,record.s3_bucket_name,file_name)
            else:
                object_url = record.s3_api_url+"/{0}/{1}".format(record.s3_bucket_name, file_name)
        return object_url
    
    @api.model
    def has_mime_type(self,conn, mime_type):
        for record in self:
            if(len(record.bucket_filters)==0):
                return True
            for filter in record.bucket_filters:
                comma_sep=[x.strip() for x in filter.mime_type.split(',')]
                for ext in comma_sep:
                    if(mime_type==ext):
                        return True
        return False
    @api.model
    def can_use(self,connection):
        if(connection.test_connected==True and connection.s3_enabled==True):
            return True
        return False
    
    @api.model
    def get_s3_connection(self, model, mime_type):
        res=self.env['pr1_s3.bucket_filter'].search([('res_model.model','=',model)])
        if(len(res)==1):
            if(res[0].s3_connection_id.can_use(res[0].s3_connection_id)):
                return res[0].s3_connection_id  
            
        elif(len(res)==0):
            res=self.env['pr1_s3.s3_connection'].search([('for_all','=',True)],limit=1)

            if(len(res)>0 and self.env['pr1_s3.s3_connection'].can_use(res[0])):
                return res[0]
            elif(len(res)==0 or self.env['pr1_s3.s3_connection'].can_use(res[0])==False):
                return False

        res=self.env['pr1_s3.bucket_filter'].search([('res_model.model','=',model),('mime_type','like',mime_type)])
        if(len(res)==0):
            return False
        for record in res: #through all the buckets for this model...
            if(res.s3_connection_id.can_use(res.s3_connection_id)==False):
                continue
            comma_sep=[x.strip() for x in record.mime_type.split(',')]
            for ext in comma_sep:
                if(mime_type==ext):
                    return record.s3_connection_id
        return False
        
    @api.multi
    def test_connection(self):
        for connection in self:
            if(connection.test_file == False):
                raise UserError("You must upload a test file in order to test the connection!!")
            attach=self.env['ir.attachment'].search([('res_model','=','pr1_s3.s3_connection'),('res_field','=','test_file'),('res_id','=',connection.id)],limit=1)
            s3_bucket,s3_service = connection.get_bucket()
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            fname = str(attach.id)+hashlib.sha1(bin_data).hexdigest()
            if(connection.append_file_name_to_start):
                fname=fname+"/test_file"
            
            if(connection.sub_folder!="" and connection.sub_folder!=False):
                fname=connection.sub_folder+"/"+fname
            
            try:
                s3_bucket.put_object(Key=fname,Body=bin_data,ACL='public-read',ContentType=attach.mimetype)
                attach.write({'datas_fname':'test_file','is_in_s3':True,'s3_connection_id':connection.id,'url':connection.get_s3_url(fname, s3_service)})
                attach.unlink()
                connection.write({'test_file':False})
            except  Exception as e:
                raise e
            connection.write({'test_connected':True,'s3_enabled':True})#ok we are test connected!
        
            