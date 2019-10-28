# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def name_get(self):
        result = []
        for task in self:
            result.append((task.id, "%s (#%d)" % (task.name, task.id)))
        return result
