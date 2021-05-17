# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
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

class tmg_proofing(models.Model):
    _name = 'sale.tmg_proofing'
    id = fields.Integer(string="ID")

    name = fields.Char(string="Name")

    sale_line = fields.Many2one("sale.order.line", string = "Sale Line")
    sale_order = fields.Many2one('sale.order',related='sale_line.order_id')
    art_file = fields.Many2one("ir.attachment", string="ArtFiles", domain="[('res_id','in',[sale_order]),('res_model', '=', 'sale.order')]")
    proofing_link = fields.Char(string = "Proof Link")
    original_date = fields.Datetime(string= "Original Date", default=datetime.today())
    notes = fields.Html('Order Notes')
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("approved_with_changes", "Approved With Changes")],
        "Proof State",
        default="pending",
    )

    def build_xml(self):
        proof_ele = ET.Element('Proof')
        proofName = ET.SubElement(proof_ele,"Name").text = self.name

        artFile = ET.SubElement(proof_ele, "ProofLink").text = self.art_file.url
        # artFile.text = self.art_file.url
        saleOrderID = ET.SubElement(proof_ele, "SaleOrderID").text = str(self.sale_order.id)
        # saleOrderID.text = self.sale_order.id
        saleOrderName = ET.SubElement(proof_ele, "SaleOrderName").text = self.sale_order.name
        # saleOrderName.text = self.sale_order.name
        saleLineID = ET.SubElement(proof_ele, "SaleLineID").text = str(self.sale_line.id)
        # saleLineID.text = self.sale_line.id
        return ET.tostring(proof_ele, pretty_print= True)


    def send_proof(self):
        session = ftplib.FTP('ftp.magnetonline.com', 'cdunn', 'magnet123')
        xml = self.build_xml()
        session.mkd("/Proofing/" + str(self.id))
        filePath = "/Proofing/" + str(self.id) + "/" + str(self.id) + ".xml"
        f = BytesIO(xml)
        session.storbinary("STOR " + filePath, f)
        session.quit()

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    proofing_lines = fields.One2many("sale.tmg_proofing","sale_line", string="Sale Line")



