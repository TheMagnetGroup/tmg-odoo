from odoo import tools
import re
from odoo import api, models,fields, _
import mimetypes
import base64
import hashlib
base_resize_images = tools.image_resize_images

def is_url(value):
    if value:
        return isinstance(value, str) and re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', value)


def new_image_resize_images(vals, big_name='image', medium_name='image_medium', small_name='image_small', sizes={}):
    url = None
    if big_name in vals and is_url(vals[big_name]):
        url = vals[big_name]
    elif medium_name in vals and is_url(vals[medium_name]):
        url = vals[medium_name]
    elif small_name in vals and is_url(vals[small_name]):
        url = vals[small_name]

    if url:
        vals.update({big_name: url})
        vals.update({medium_name: url})
        vals.update({small_name: url})
    else:
        base_resize_images(vals, big_name, medium_name, small_name, sizes)


tools.image_resize_images = new_image_resize_images

class Binary(fields.Binary):

    def write(self, records, vals, create=False):
        domain = [
            ('res_model', '=', records._name),
            ('res_field', '=', self.name),
            ('res_id', 'in', records.ids),
        ]
        atts = records.env['ir.attachment'].sudo().search(domain)
        if (vals and atts.url and atts.type == 'url' and not is_url(vals)):
            atts.write({
                'url': None,
                'type': 'binary',
            })
        if (vals and is_url(vals)):
            with records.env.norecompute():
                if value:
                    atts.write({
                        'url': value,
                        'mimetype': mimetypes.guess_type(vals)[0],
                        'datas': None,
                        'type': 'url',
                    })
                    for record in (records - records.browse(atts.mapped('res_id'))):
                        atts.create({
                            'name': self.name,
                            'res_model': record._name,
                            'res_field': self.name,
                            'res_id': record.id,
                            'type': 'url',
                            'url': vals,
                        })
                else:
                    atts.unlink()
        else:
            # super(Binary, self).write(records, vals, create=create)
            super(Binary, self).write(records, vals)


# fields.Binary = Binary
fields.Binary.write = Binary.write
