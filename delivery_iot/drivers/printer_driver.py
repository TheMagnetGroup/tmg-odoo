# -*- coding: utf-8 -*-

from base64 import b64decode
from odoo import api, fields, models
from odoo.addons.hw_drivers.drivers import PrinterDriver


class IotPrinterDriver(PrinterDriver.PrinterDriver):

    def action(self, data):
        if data.get('action') == 'cashbox':
            self.open_cashbox()
        elif data.get('action') == 'print_receipt':
            self.print_receipt(b64decode(data['receipt']))
        else:
            if 'documents' in data:
                for data_chunk in data['documents']:
                    self.print_raw(b64decode(data_chunk))
            else:
                self.print_raw(b64decode(data['document']))
