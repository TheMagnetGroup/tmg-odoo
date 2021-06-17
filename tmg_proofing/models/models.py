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

    sale_line = fields.Many2one("sale.order.line", string = "Sale Line")
    sale_order = fields.Many2one('sale.order',related='sale_line.order_id')

    art_file = fields.Many2one("ir.attachment", string="ArtFiles",
                               domain="[('res_id','in',[sale_order]),('type', '=', 'url')]")
    proofing_link = fields.Char(string = "Proof Link")
    original_date = fields.Datetime(string= "Original Date", default=datetime.today())
    suggested_layout = fields.Boolean(string="Sent Suggested Layout")
    notes = fields.Html('Order Notes')
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("approved_with_changes", "Approved With Changes")],
        "Proof State",
        default="pending",
    )
    processed = fields.Boolean("Processed")
    suggested_layout_accepted = fields.Boolean(string="Suggested Layout Approved")
    proof_response_date = fields.Datetime(string="Response Date")


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


        artFile = ET.SubElement(proof_ele, "ProofLink").text = self.art_file.url
        # artFile.text = self.art_file.url
        saleOrderID = ET.SubElement(proof_ele, "SaleOrderID").text = str(self.sale_order.id)
        # saleOrderID.text = self.sale_order.id
        saleOrderName = ET.SubElement(proof_ele, "SaleOrderName").text = self.sale_order.name
        # saleOrderName.text = self.sale_order.name
        saleLineID = ET.SubElement(proof_ele, "SaleLineID").text = str(self.sale_line.id)
        suggestedID = ET.SubElement(proof_ele, "Suggested").text = str(self.suggested_layout)
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

        session = ftplib.FTP(ftpSite, ftpUser, ftpPassword)
        xml = self.build_xml()
        session.mkd("/Proofing/" + str(self.id))
        filePath = "/Proofing/" + str(self.id) + "/" + str(self.id) + ".xml"
        f = BytesIO(xml)
        session.storbinary("STOR " + filePath, f)
        session.quit()

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    proofing_lines = fields.One2many("sale.tmg_proofing","sale_line", string="Sale Line")



