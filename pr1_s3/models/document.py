import base64
import os
import hashlib
import logging
from odoo import api, models,fields, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)
try:
    import boto3
except:
    _logger.debug('boto3 package is required!!')
import requests
class Document(models.Model):
    _inherit = 'ir.attachment'
    is_in_s3 = fields.Boolean(string='Is in S3',default=False)
    s3_connection_id=fields.Many2one('pr1_s3.s3_connection', string="S3 Connection")
    version_id = fields.Char(string='Version Id', help='The unique version id of the attachment in S3')
    
    @api.multi
    def _filter_protected_attachments(self):
        return self.filtered(lambda r: r.res_model != 'ir.ui.view' or not r.name.startswith('/web/content/'))
    
    @api.depends('store_fname', 'db_datas')
    def _compute_datas(self):
        bin_size = self._context.get('bin_size')
        url_records = self.filtered(lambda r: r.type == 'url' and r.url)
        for attach in url_records:
            if (bin_size):
                attach.datas = "1.00 Kb"
            else:
                r = requests.get(attach.url)
                attach.datas = base64.b64encode(r.content)
        super(Document, self - url_records)._compute_datas()
        
    @api.multi
    def unlink(self):
        for record in self:
            if(record.is_in_s3==True):
                self.delete_s3_attachment()
            return super(Document,record).unlink()
    
    @api.multi
    def delete_s3_attachment(self):
        connection=False
        s3_bucket = False
        s3_service =False
        for attach in self:
            if(attach.is_in_s3==False):
                continue
            if(attach.s3_connection_id.id==False):
                connection=self.env['pr1_s3.s3_connection'].get_s3_connection(attach.res_model,attach.mimetype)
            elif(connection==False or attach.s3_connection_id.id!=connection.id):
                connection=attach.s3_connection_id
                s3_bucket,s3_service = connection.get_bucket()
            if(connection==False):
                raise UserError("The connection associated with this attachment is not accessible")
            
            try:
                # item=s3_service.Object(connection.s3_bucket_name,attach.url)
                item = s3_service.ObjectVersion(connection.s3_bucket_name,attach.url,self.version_id)
                item.delete()
            except:
                pass  #item has already been deleted from S3
            
    def _inverse_datas(self):
        s3_to_do = self._filter_protected_attachments()
        s3_to_do = self.filtered('datas')
        connection=False
        for attach in s3_to_do: #todo find out what this does if res_model is blank
            if(connection==False or (conection.res_model.name!=attach.res_model and connection.has_mime_type(connection,attach.mimetype))):
                connection=self.env['pr1_s3.s3_connection'].get_s3_connection(attach.res_model,attach.mimetype)
                if(connection==False): #nothing to do here
                    super(Document,self)._inverse_datas()
                    continue
                s3_bucket,s3_service = connection.get_bucket()
            value = attach.datas
            bin_data = base64.b64decode(value) if value else b''
            
            if not self.res_name:

                fname = hashlib.sha1(bin_data).hexdigest()

                if(len(fname)>6): #small random fname
                    fname=fname[:6]
            
                fname=str(attach.id)+fname
            else:
                fname = self.res_name + '-' + str(self.res_id) # create folder based on resource name and id(sales order, task, etc)

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
            
            
            s3_obj = s3_bucket.put_object(Key=fname,Body=bin_data,ACL='public-read',ContentType=attach.mimetype,Metadata=Metadata)
            vals = {
                'checksum': self._compute_checksum(bin_data),
                'url': connection.get_s3_url(fname, s3_service),
                'file_size': len(bin_data),
                'index_content': self._index(bin_data, attach.datas_fname, attach.mimetype),
                'is_in_s3':True,
                's3_connection_id':connection.id,
                'store_fname': fname,
                'db_datas': False,
                'type': 'url',
                'version_id' : s3_obj.version_id
            }
            super(Document, attach.sudo()).write(vals)

        super(Document, self - s3_to_do)._inverse_datas()
