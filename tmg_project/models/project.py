# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    dft_task_description = fields.Html(string='Default Task Description')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _get_dft_task_description(self):
        dfts = super(ProjectTask, self).default_get(['project_id'])
        if dfts:
            project = self.env['project.project'].browse(dfts['project_id'])
            return project.dft_task_description
        else:
            return None

    description = fields.Html(string='Description', default=_get_dft_task_description)

    @api.multi
    def name_get(self):
        result = []
        for task in self:
            result.append((task.id, "%s (#%d)" % (task.name, task.id)))
        return result

