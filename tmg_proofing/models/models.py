# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning
from io import BytesIO
# import xml.etree.ElementTree as ET
from lxml import etree as ET
import ssl
import ftplib
import urllib.request
import json
import base64
import os
import traceback

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    proofing_count = fields.Integer(compute="_get_proofing_count")

    def _get_proofing_count(self):
        proofsObj = self.env['sale.tmg_proofing']
        proofs = proofsObj.search([("sale_order.id", "=", self.id)])
        if proofs:
            self.proofing_count = len(proofs)


class tmg_proofing(models.Model):
    _name = 'sale.tmg_proofing'
    id = fields.Integer(string="ID")

    name = fields.Char(string="Name", default='Proof')
    product = fields.Many2one("product.product", related="sale_line.product_id", string = "Product")
    brand = fields.Many2one("product.category", related="product.brand")
    sale_line = fields.Many2one("sale.order.line", string = "Sale Line")
    sale_order = fields.Many2one('sale.order',related='sale_line.order_id')
    sale_team = fields.Many2one('crm.team', related='sale_order.team_id')
    email_ids = fields.Many2many('res.partner', string='Send To')
    art_file = fields.Many2one("ir.attachment", string="ArtFiles",
                               domain="[('res_id','=',[sale_order]),('type', '=', 'url'),('res_model', '=', 'sale.order')]")
    # art_file = fields.Many2one("ir.attachment", string="ArtFiles",
    #                            domain="[('type', '=', 'url'),('res_model', '=', 'sale.order')]")
    proofing_link = fields.Char(string = "Proof Link")
    original_date = fields.Datetime(string= "Original Date", default=datetime.today())
    # original_file_name = fields.Char(string="File Name")
    # original_file_url = fields.Binary(string="Original File")
    send_attachment = fields.Boolean(string="Send Attachments", default=False)
    suggested_layout = fields.Boolean(string="Sent Suggested Layout")
    notes = fields.Html('Order Notes')
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("approved_with_changes", "Approved With Changes")],
        "Proof State",
        default="pending"
    )
    processed = fields.Boolean("Processed")
    suggested_layout_accepted = fields.Boolean(string="Suggested Layout Approved")
    proof_response_date = fields.Datetime(string="Response Date")
    work_order = fields.Many2one('mrp.production', string = "Work Order",
                                 domain="[('sale_line_id','=',[sale_line]),('state', 'not in', ['done', 'cancel'])]")
                                        # "('res_model', '=', 'sale.order')]")

    @api.constrains('art_file')
    def _check_file(self):
        if str(self.art_file.datas_fname.split(".")[1]) != 'pdf':
            raise ValidationError("Art File must be .pdf file")

    # @api.model
    # def create(self, vals):
    #     proof = super(tmg_proofing, self).create(vals)
    #     if proof.art_file:
    #
    #         proof.original_file_url = proof.art_file.url
    #         proof.original_file_name = proof.art_file.datas_fname
    #     return proof


    def update_proof(self, proof_id, state, notes, suggested = False):
        proof = self.env['sale.tmg_proofing'].browse(proof_id)
        proof.write({
                'state': state,
                'proof_response_date': datetime.today(),
                'notes': notes,
                'suggested_layout_accepted': suggested
            })
        return "Success"

    def build_xml(self):
        proof_ele = ET.Element('Proof')
        emails = ','.join([o.email for o in self.email_ids])

        artFile = ET.SubElement(proof_ele, "ProofFile").text = self.art_file.get_public_url()
        artFileName = ET.SubElement(proof_ele, "ProofFileName").text = self.art_file.store_fname
        # artFile.text = self.art_file.url
        saleOrderID = ET.SubElement(proof_ele, "SaleOrderID").text = str(self.sale_order.id)
        # saleOrderID.text = self.sale_order.id
        saleOrderName = ET.SubElement(proof_ele, "SaleOrderName").text = self.sale_order.name
        emails = ET.SubElement(proof_ele,"EmailTo").text = emails.replace(',',';')
        saleLineID = ET.SubElement(proof_ele, "SaleLineID").text = str(self.sale_line.id)
        description = ET.SubElement(proof_ele, "Description").text = self.sale_line.name
        productionOrder = ET.SubElement(proof_ele, "WorkOrder").text = str(self.work_order.name)
        suggestedID = ET.SubElement(proof_ele, "Suggested").text = str(self.suggested_layout)
        PONumber = ET.SubElement(proof_ele, "PONumber").text = self.sale_order.client_order_ref or ''
        Quantity = ET.SubElement(proof_ele, "Quantity").text = str(self.sale_line.product_uom_qty)
        sendAtt = ''
        if self.send_attachment:
            sendAtt = "Y"
        else:
            sendAtt = "N"

        send_attachments =  ET.SubElement(proof_ele, "SendAttachments").text = sendAtt
        # saleLineID.text = self.sale_line.id
        return ET.tostring(proof_ele, pretty_print= True)

    def mark_processed(self):
        self.processed = True

    def _get_lookup_value(self, name, category):
        cont = self.env['tmg_external_api.tmg_reference']
        val = cont.search([('category', '=', category), ('name', '=', name)])
        return val.value

    def send_proof(self):

        ftpSite = self._get_lookup_value("Site", "Proofing")
        ftpUser = self._get_lookup_value("Username", "Proofing")
        ftpPassword = self._get_lookup_value("Password", "Proofing")
        xml = self.build_xml()
        session = ftplib.FTP(ftpSite, ftpUser, ftpPassword)

        session.mkd("/Proofing/" + str(self.id))
        filePath = "/Proofing/" + str(self.id) + "/" + str(self.id) + ".xml"
        f = BytesIO(xml)
        session.storbinary("STOR " + filePath, f)
        session.quit()

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    proofing_lines = fields.One2many("sale.tmg_proofing","sale_line", string="Sale Line")

class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    def name_get(self):
        context = self.env.context or {}
        res = []

        for r in self:

            if r.name:
                if context.get('Show_Item', False):
                    res.append((r.id, r.name + '-' + r.product_id.name))
                else:
                    res.append((r.id, r.name))
        return res



