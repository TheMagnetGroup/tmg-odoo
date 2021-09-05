import base64
import os
import hashlib
import logging
import re
from odoo import api, models,fields
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
    def get_public_url(self):
        connection = False
        s3_bucket = False
        s3_service = False
        for attach in self:
            if (attach.is_in_s3 == False):
                continue
            if (attach.s3_connection_id.id == False):
                connection = self.env['pr1_s3.s3_connection'].get_s3_connection(attach.res_model, attach.mimetype)
            elif (connection == False or attach.s3_connection_id.id != connection.id):
                connection = attach.s3_connection_id
                s3_bucket, s3_service = connection.get_bucket_client()
            if (connection == False):
                raise UserError("The connection associated with this attachment is not accessible")

            obj = s3_service.generate_presigned_url('get_object', Params = {'Bucket': s3_bucket, 'Key': attach.store_fname}, ExpiresIn = 100)


            return obj

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
            if(connection==False or (connection.res_model.name!=attach.res_model and connection.has_mime_type(connection,attach.mimetype))):
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

            s3_filename = ''
            if(attach.datas_fname!=False):
                s3_filename = re.sub(r'[ ]', r'_', attach.datas_fname)
                s3_filename = re.sub(r'[\&\$\@\=\;\:\+\,\?\\\{\^\}\%\`\]\>\[\~\<\#\|]',r'', s3_filename)

            if(attach.datas_fname!=False):
                Metadata={
                # 'FileName': attach.datas_fname
                'FileName' : s3_filename
                }
            else:
                Metadata={}
            
            if(connection.append_file_name_to_start):
                if(attach.datas_fname!=False):
                    #fname=fname+"/"+attach.datas_fname
                    fname = fname + "/" + s3_filename
                else:
                    fname = hashlib.sha1(bin_data).hexdigest()
            
            if(connection.sub_folder!="" and connection.sub_folder!=False):
                fname=connection.sub_folder+"/"+fname

            try:
                s3_obj = s3_bucket.put_object(Key=fname,Body=bin_data,ACL='public-read',ContentType=attach.mimetype,Metadata=Metadata)
            except Exception as e:
                r = 3
                # raise exceptions.UserError(e.message)

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

    # This routine uploads an attachment to the standard TMG public bucket
    @api.multi
    def _upload_to_public_bucket(self, folder):
        # We only want to deal with a single attachment here
        self.ensure_one()
        # First we need to get the public bucket defined in the buckets model
        connection = self.env['pr1_s3.s3_connection'].search([('name', '=', 'tmg_public')])
        # If we got a connection object
        if connection:
            # Is the connection S3 enabled? If not then skip uploading (testing purposes)
            if connection.s3_enabled:
                s3_bucket, s3_service = connection.get_bucket()
                upload = False

                # Decode from base64 and get the md5 checksum value
                bin_data = base64.b64decode(self.data)
                # Get the MD5 checksum of the data
                local_md5 = '"' + hashlib.md5(bin_data).hexdigest() + '"'

                # Is the file already in S3?
                obj = list(s3_bucket.objects.filter(Prefix=self.name))
                if len(obj) == 0:
                    upload = True
                else:
                    # Check the MD5 of the file in S3 and compare that against the current file.  If different, upload
                    s3_md5 = obj[0].e_tag
                    if s3_md5 != local_md5:
                        upload = True

                # Upload the file to the public bucket
                if upload:
                    try:
                        s3_obj = s3_bucket.put_object(Key=folder + self.name,Body=self.datas,ACL='public-read',ContentType=self.mimetype)
                    except Exception as e:
                        raise e.UserError(e.message)

            # Return the path to the file in our public bucket.
            return connection.s3_api_url + "/" + connection.s3_bucket_name + "/" + folder + self.name